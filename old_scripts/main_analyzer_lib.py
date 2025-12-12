#!/usr/bin/env python3
"""
TOFcam Main Analyzer - Refactored with tofcam.lib
================================================

Análise com persistência usando exclusivamente tofcam.lib.
Mantém todas as funcionalidades originais.
"""

import cv2
import numpy as np
import time
import os
import json
from typing import Optional

# Imports da biblioteca centralizada
from tofcam.lib import (
    create_camera_manager, create_depth_estimator, create_navigator,
    create_render_pipeline, discover_cameras, CameraConfig, 
    NavigationMode, TOFConfig, logger, AnalysisFrame
)

class PersistentAnalyzer:
    """Analisador com persistência usando tofcam.lib"""
    
    def __init__(self, config: TOFConfig = None, cameras: list = None):
        self.config = config or TOFConfig()
        self.available_cameras = cameras or discover_cameras()
        self.current_camera_index = 0
        
        # Componentes da biblioteca
        self.camera_manager = create_camera_manager()
        self.depth_estimator = create_depth_estimator()
        self.navigator = create_navigator(self.config.navigation)
        self.render_pipeline = create_render_pipeline()
        
        if not self.available_cameras:
            # Tentar modo de teste
            logger.warning("Nenhuma câmera física encontrada, usando modo de teste")
            self.available_cameras = [0]
            self.config.camera.use_test_image = True
            
        print(f"📹 Câmeras encontradas: {self.available_cameras}")
        
        # Configurar câmera inicial
        self.switch_camera(self.available_cameras[0])
    
    def switch_camera(self, camera_index: int) -> bool:
        """Trocar câmera ativa"""
        if camera_index not in self.available_cameras and not self.config.camera.use_test_image:
            logger.warning(f"Câmera {camera_index} não disponível")
            return False
        
        try:
            # Fechar câmera atual se houver
            self.camera_manager.close_all()
            
            # Configurar nova câmera
            camera_config = CameraConfig(
                index=camera_index,
                width=self.config.camera.width,
                height=self.config.camera.height,
                fps=self.config.camera.fps,
                use_test_image=self.config.camera.use_test_image
            )
            
            if self.camera_manager.add_camera(camera_config):
                self.current_camera_index = camera_index
                logger.info(f"✅ Câmera {camera_index} ativada")
                return True
            else:
                logger.error(f"❌ Falha ao ativar câmera {camera_index}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao trocar câmera: {e}")
            return False
    
    def analyze_frame(self) -> Optional[AnalysisFrame]:
        """Análise completa de um frame"""
        try:
            # Capturar frame
            frame = self.camera_manager.read_frame()
            if frame is None:
                return None
            
            # Análise de profundidade
            depth_map = self.depth_estimator.estimate_depth(frame)
            
            # Análise de navegação
            nav_result = self.navigator.navigate(depth_map, NavigationMode.HYBRID)
            
            # Criar grids
            strategic_grid = self.navigator.zone_mapper.create_strategic_grid(depth_map)
            reactive_grid = self.navigator.zone_mapper.create_reactive_grid(depth_map)
            
            # Renderizar visualização
            visualization = self.render_pipeline.render_complete_view(
                depth_map, strategic_grid, nav_result
            )
            
            # Criar frame de análise
            analysis_frame = AnalysisFrame(
                timestamp=time.time(),
                frame_id=int(time.time() * 1000),
                rgb_image=frame,
                depth_map=depth_map,
                strategic_grid=strategic_grid,
                reactive_grid=reactive_grid,
                navigation_result=nav_result,
                depth_colored=visualization
            )
            
            return analysis_frame
            
        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            return None
    
    def save_analysis(self, analysis_frame: AnalysisFrame, 
                     output_dir: str = "output_images") -> str:
        """Salvar análise com persistência"""
        try:
            # Criar diretório
            timestamp = int(analysis_frame.timestamp * 1000)
            session_dir = f"cam{self.current_camera_index}_{time.strftime('%Y%m%d_%H%M%S')}"
            full_dir = os.path.join(output_dir, session_dir)
            os.makedirs(full_dir, exist_ok=True)
            
            # Salvar imagens
            cv2.imwrite(os.path.join(full_dir, "original.jpg"), analysis_frame.rgb_image)
            cv2.imwrite(os.path.join(full_dir, "depth.jpg"), analysis_frame.depth_colored)
            
            # Salvar dados de navegação
            nav_data = {
                "timestamp": analysis_frame.timestamp,
                "frame_id": analysis_frame.frame_id,
                "camera_index": self.current_camera_index,
                "navigation_mode": analysis_frame.navigation_result.mode.value,
                "strategic": {
                    "target_yaw_delta": float(analysis_frame.navigation_result.strategic.target_yaw_delta),
                    "confidence": float(analysis_frame.navigation_result.strategic.confidence),
                    "min_distance_ahead": float(analysis_frame.navigation_result.strategic.min_distance_ahead),
                    "recommended_speed": float(analysis_frame.navigation_result.strategic.recommended_speed)
                } if analysis_frame.navigation_result.strategic else None,
                "reactive": {
                    "yaw_delta": float(analysis_frame.navigation_result.reactive.yaw_delta),
                    "forward_scale": float(analysis_frame.navigation_result.reactive.forward_scale),
                    "emergency_brake": bool(analysis_frame.navigation_result.reactive.emergency_brake),
                    "urgency": float(analysis_frame.navigation_result.reactive.urgency)
                } if analysis_frame.navigation_result.reactive else None
            }
            
            with open(os.path.join(full_dir, "analysis.json"), "w") as f:
                json.dump(nav_data, f, indent=2)
            
            logger.info(f"💾 Análise salva: {full_dir}")
            return full_dir
            
        except Exception as e:
            logger.error(f"Erro ao salvar análise: {e}")
            return ""
    
    def run_interactive_session(self):
        """Sessão interativa de análise"""
        print("\n🎯 TOFcam Interactive Analyzer")
        print("=" * 40)
        print("📋 Comandos:")
        print("  SPACE - Analisar frame atual")
        print("  s     - Salvar análise")
        print("  c     - Trocar câmera")
        print("  ESC   - Sair")
        print()
        
        current_analysis = None
        frame_count = 0
        
        while True:
            try:
                # Capturar e mostrar frame atual
                frame = self.camera_manager.read_frame()
                if frame is not None:
                    # Mostrar frame
                    cv2.imshow(f"TOFcam - Camera {self.current_camera_index}", frame)
                    
                    # Mostrar análise se disponível
                    if current_analysis and current_analysis.depth_colored is not None:
                        cv2.imshow("Análise", current_analysis.depth_colored)
                
                # Processar teclas
                key = cv2.waitKey(1) & 0xFF
                
                if key == 27:  # ESC
                    break
                elif key == ord(' '):  # SPACE
                    print(f"🔍 Analisando frame {frame_count + 1}...")
                    current_analysis = self.analyze_frame()
                    
                    if current_analysis:
                        frame_count += 1
                        nav = current_analysis.navigation_result
                        print(f"✅ Frame {frame_count} analisado")
                        
                        if nav.strategic:
                            yaw_deg = np.rad2deg(nav.strategic.target_yaw_delta)
                            print(f"  Strategic: Yaw={yaw_deg:.1f}°, Conf={nav.strategic.confidence:.3f}")
                        
                        if nav.reactive:
                            print(f"  Reactive: Yaw={nav.reactive.yaw_delta:.3f}, Emergency={nav.reactive.emergency_brake}")
                    else:
                        print("❌ Falha na análise")
                
                elif key == ord('s'):  # Salvar
                    if current_analysis:
                        saved_path = self.save_analysis(current_analysis)
                        if saved_path:
                            print(f"💾 Análise salva em: {saved_path}")
                    else:
                        print("⚠️ Nenhuma análise para salvar. Pressione SPACE primeiro.")
                
                elif key == ord('c'):  # Trocar câmera
                    current_idx = self.available_cameras.index(self.current_camera_index)
                    next_idx = (current_idx + 1) % len(self.available_cameras)
                    next_camera = self.available_cameras[next_idx]
                    
                    if self.switch_camera(next_camera):
                        print(f"📹 Câmera trocada para: {next_camera}")
                    else:
                        print(f"❌ Falha ao trocar para câmera: {next_camera}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Erro na sessão: {e}")
                time.sleep(1)
        
        # Limpeza
        self.camera_manager.close_all()
        cv2.destroyAllWindows()
        print(f"\n✅ Sessão encerrada. Frames analisados: {frame_count}")

def main():
    """Função principal"""
    print("🚀 TOFcam Persistent Analyzer (tofcam.lib)")
    print("=" * 50)
    
    try:
        # Criar configuração
        config = TOFConfig()
        config.save_frames = True
        config.output_dir = "output_images"
        
        # Criar analisador
        analyzer = PersistentAnalyzer(config)
        
        # Menu principal
        print("\n📋 Escolha o modo:")
        print("1. Sessão interativa")
        print("2. Análise único frame")
        print("3. Análise contínua (10 frames)")
        
        choice = input("Opção (1-3): ").strip()
        
        if choice == "1":
            analyzer.run_interactive_session()
            
        elif choice == "2":
            print("🔍 Analisando frame único...")
            analysis = analyzer.analyze_frame()
            if analysis:
                saved_path = analyzer.save_analysis(analysis)
                print(f"✅ Análise concluída e salva em: {saved_path}")
            else:
                print("❌ Falha na análise")
                
        elif choice == "3":
            print("🔄 Análise contínua - 10 frames...")
            for i in range(10):
                print(f"Frame {i+1}/10...")
                analysis = analyzer.analyze_frame()
                if analysis:
                    analyzer.save_analysis(analysis)
                time.sleep(0.5)
            print("✅ Análise contínua concluída")
        
        else:
            print("❌ Opção inválida")
    
    except Exception as e:
        logger.error(f"Erro na aplicação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()