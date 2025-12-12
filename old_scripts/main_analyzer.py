#!/usr/bin/env python3
"""
TOFcam Main Analyzer - Refactored with tofcam.lib
=================================================

Análise completa com visualização e salvamento usando tofcam.lib.
Preserva todas as funcionalidades originais:
- 4 janelas de visualização (Camera, Depth, Strategic, Reactive)
- Sistema de percepção MiDaS
- Zone mapping estratégico e reativo
- Salvamento organizado por categoria
- Detecção automática de display
"""

import cv2
import os
import sys
import subprocess
import numpy as np
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Imports da biblioteca centralizada
from tofcam.lib import (
    create_camera_manager, create_depth_estimator, create_navigator,
    create_render_pipeline, discover_cameras, CameraConfig, 
    NavigationMode, TOFConfig, logger, AnalysisFrame
)

def check_display():
    """Verifica se há display X11 disponível para visualização"""
    try:
        display = os.environ.get('DISPLAY', '')
        if not display:
            return False
        
        result = subprocess.run(['xset', 'q'], 
                              capture_output=True, 
                              timeout=2)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

HAS_DISPLAY = check_display()

class TOFCamVisualizer:
    """Visualizador completo do TOFcam usando tofcam.lib"""
    
    def __init__(self, output_dir="output_images"):
        self.base_dir = Path(output_dir)
        
        # Configuração
        self.config = TOFConfig()
        
        # Componentes da biblioteca
        self.camera_manager = create_camera_manager()
        self.depth_estimator = create_depth_estimator()
        self.navigator = create_navigator(self.config.navigation)
        self.render_pipeline = create_render_pipeline()
        
        # Detectar câmeras
        self.available_cameras = discover_cameras()
        if not self.available_cameras:
            logger.warning("Usando modo de teste")
            self.available_cameras = [0]
            self.config.camera.use_test_image = True
        
        # Configurar câmera principal
        camera_config = CameraConfig(
            index=self.available_cameras[0],
            width=self.config.camera.width,
            height=self.config.camera.height,
            fps=self.config.camera.fps,
            use_test_image=self.config.camera.use_test_image
        )
        
        if not self.camera_manager.add_camera(camera_config):
            raise RuntimeError("❌ Falha ao inicializar câmera")
        
        # Estrutura de pastas por tipo
        self.folders = {
            'camera': self.base_dir / 'camera_original',
            'depth': self.base_dir / 'depth_maps', 
            'strategic': self.base_dir / 'strategic_navigation',
            'reactive': self.base_dir / 'reactive_avoidance',
            'analysis': self.base_dir / 'complete_analysis'
        }
        
        # Criar todas as pastas
        for folder in self.folders.values():
            folder.mkdir(parents=True, exist_ok=True)
        
        self.setup_windows()
    
    def setup_windows(self):
        """Configura as 4 janelas de visualização se display disponível"""
        if not HAS_DISPLAY:
            print("⚠️ Nenhum display detectado - modo somente salvamento")
            return
            
        try:
            # Criar 4 janelas específicas
            cv2.namedWindow("TOFCam - Camera Feed", cv2.WINDOW_NORMAL)
            cv2.namedWindow("TOFCam - Depth Map", cv2.WINDOW_NORMAL)
            cv2.namedWindow("TOFCam - Strategic Grid", cv2.WINDOW_NORMAL)
            cv2.namedWindow("TOFCam - Reactive Grid", cv2.WINDOW_NORMAL)
            
            # Redimensionar para visualização otimizada
            cv2.resizeWindow("TOFCam - Camera Feed", 320, 240)
            cv2.resizeWindow("TOFCam - Depth Map", 320, 240)
            cv2.resizeWindow("TOFCam - Strategic Grid", 320, 240)
            cv2.resizeWindow("TOFCam - Reactive Grid", 320, 240)
            
            # Posicionamento em grade 2x2
            cv2.moveWindow("TOFCam - Camera Feed", 0, 0)
            cv2.moveWindow("TOFCam - Depth Map", 340, 0)
            cv2.moveWindow("TOFCam - Strategic Grid", 0, 280)
            cv2.moveWindow("TOFCam - Reactive Grid", 340, 280)
            
            print("✅ 4 janelas de visualização configuradas")
            
        except Exception as e:
            print(f"⚠️ Erro ao configurar janelas: {e}")
            print("🔄 Modo somente salvamento ativado")
    
    def save_frame_analysis(self, frame_num: int, analysis: AnalysisFrame):
        """Salva análise completa em pastas organizadas"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        frame_prefix = f"frame_{frame_num:04d}_{timestamp}"
        
        try:
            # 1. Frame original da câmera
            camera_path = self.folders['camera'] / f"{frame_prefix}.jpg"
            cv2.imwrite(str(camera_path), analysis.rgb_image)
            
            # 2. Mapa de profundidade colorizado
            depth_path = self.folders['depth'] / f"{frame_prefix}_depth.jpg"
            cv2.imwrite(str(depth_path), analysis.depth_colored)
            
            # 3. Grid estratégico com overlay
            strategic_viz = self.render_pipeline.render_strategic_overlay(
                analysis.rgb_image, analysis.strategic_grid, analysis.navigation_result
            )
            strategic_path = self.folders['strategic'] / f"{frame_prefix}_strategic.jpg"
            cv2.imwrite(str(strategic_path), strategic_viz)
            
            # 4. Grid reativo com overlay
            reactive_viz = self.render_pipeline.render_reactive_overlay(
                analysis.rgb_image, analysis.reactive_grid, analysis.navigation_result
            )
            reactive_path = self.folders['reactive'] / f"{frame_prefix}_reactive.jpg"
            cv2.imwrite(str(reactive_path), reactive_viz)
            
            # 5. Análise completa combinada
            complete_viz = self.render_pipeline.render_complete_analysis(analysis)
            analysis_path = self.folders['analysis'] / f"{frame_prefix}_complete.jpg"
            cv2.imwrite(str(analysis_path), complete_viz)
            
            # Log do salvamento
            logger.info(f"💾 Frame {frame_num} salvo em 5 categorias")
            
        except Exception as e:
            logger.error(f"Erro ao salvar frame {frame_num}: {e}")
    
    def display_frames(self, analysis: AnalysisFrame):
        """Exibir nas 4 janelas se display disponível"""
        if not HAS_DISPLAY:
            return
        
        try:
            # Janela 1: Camera Feed Original
            cv2.imshow("TOFCam - Camera Feed", analysis.rgb_image)
            
            # Janela 2: Depth Map Colorizado
            cv2.imshow("TOFCam - Depth Map", analysis.depth_colored)
            
            # Janela 3: Strategic Grid
            strategic_viz = self.render_pipeline.render_strategic_overlay(
                analysis.rgb_image, analysis.strategic_grid, analysis.navigation_result
            )
            cv2.imshow("TOFCam - Strategic Grid", strategic_viz)
            
            # Janela 4: Reactive Grid
            reactive_viz = self.render_pipeline.render_reactive_overlay(
                analysis.rgb_image, analysis.reactive_grid, analysis.navigation_result
            )
            cv2.imshow("TOFCam - Reactive Grid", reactive_viz)
            
        except Exception as e:
            logger.error(f"Erro na exibição: {e}")
    
    def analyze_frame(self) -> Optional[AnalysisFrame]:
        """Análise completa usando tofcam.lib"""
        try:
            # Capturar frame
            frame = self.camera_manager.read_frame()
            if frame is None:
                return None
            
            # Estimativa de profundidade MiDaS
            depth_map = self.depth_estimator.estimate_depth(frame)
            
            # Navegação híbrida (strategic + reactive)
            nav_result = self.navigator.navigate(depth_map, NavigationMode.HYBRID)
            
            # Criar grids de zona
            strategic_grid = self.navigator.zone_mapper.create_strategic_grid(depth_map)
            reactive_grid = self.navigator.zone_mapper.create_reactive_grid(depth_map)
            
            # Renderização de profundidade
            depth_colored = self.render_pipeline.render_depth_colored(depth_map)
            
            # Criar frame de análise
            analysis_frame = AnalysisFrame(
                timestamp=time.time(),
                frame_id=int(time.time() * 1000),
                rgb_image=frame,
                depth_map=depth_map,
                strategic_grid=strategic_grid,
                reactive_grid=reactive_grid,
                navigation_result=nav_result,
                depth_colored=depth_colored
            )
            
            return analysis_frame
            
        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            return None
    
    def print_navigation_metrics(self, frame_num: int, nav_result, processing_time: float):
        """Imprimir métricas detalhadas de navegação"""
        print(f"\n📊 Frame {frame_num} - Análise ({processing_time:.3f}s)")
        print("=" * 50)
        
        # Navegação estratégica
        if nav_result.strategic:
            strategic = nav_result.strategic
            yaw_deg = np.rad2deg(strategic.target_yaw_delta)
            print(f"🗺️ Strategic Navigation:")
            print(f"   Target Yaw: {yaw_deg:+7.2f}° ({strategic.target_yaw_delta:+7.4f} rad)")
            print(f"   Confidence: {strategic.confidence:7.3f}")
            print(f"   Min Dist:   {strategic.min_distance_ahead:7.2f}m")
            print(f"   Speed Rec:  {strategic.recommended_speed:7.2f}x")
        
        # Navegação reativa
        if nav_result.reactive:
            reactive = nav_result.reactive
            print(f"⚡ Reactive Avoidance:")
            print(f"   Yaw Delta:  {reactive.yaw_delta:+7.4f} rad")
            print(f"   Forward:    {reactive.forward_scale:7.3f}x")
            print(f"   Emergency:  {reactive.emergency_brake}")
            print(f"   Urgency:    {reactive.urgency:7.3f}")
        
        # Modo combinado
        print(f"🎯 Combined Mode: {nav_result.mode.value}")
    
    def run_continuous_analysis(self, max_frames=None, save_interval=1):
        """Execução de análise contínua com todas as funcionalidades"""
        print(f"\n🚀 TOFcam Continuous Analysis (tofcam.lib)")
        print("=" * 60)
        print(f"📹 Câmera: {self.available_cameras[0]}")
        print(f"💾 Output: {self.base_dir}")
        print(f"🖥️ Display: {'Sim' if HAS_DISPLAY else 'Não'}")
        print(f"📊 Max frames: {max_frames or 'Ilimitado'}")
        print(f"💾 Save a cada: {save_interval} frames")
        print("\n[ESC] para sair, [SPACE] para pausar")
        print("=" * 60)
        
        frame_count = 0
        total_time = 0
        paused = False
        
        try:
            while True:
                # Verificar condição de parada
                if max_frames and frame_count >= max_frames:
                    break
                
                # Processar tecla se display disponível
                if HAS_DISPLAY:
                    key = cv2.waitKey(1) & 0xFF
                    if key == 27:  # ESC
                        break
                    elif key == ord(' '):  # SPACE
                        paused = not paused
                        print(f"{'⏸️ Pausado' if paused else '▶️ Retomado'}")
                        continue
                
                if paused:
                    time.sleep(0.1)
                    continue
                
                # Análise do frame
                start_time = time.time()
                analysis = self.analyze_frame()
                processing_time = time.time() - start_time
                
                if analysis is None:
                    print("⚠️ Frame inválido, tentando novamente...")
                    time.sleep(0.1)
                    continue
                
                frame_count += 1
                total_time += processing_time
                
                # Exibir visualização
                if HAS_DISPLAY:
                    self.display_frames(analysis)
                
                # Salvar análise se necessário
                if frame_count % save_interval == 0:
                    self.save_frame_analysis(frame_count, analysis)
                
                # Métricas detalhadas
                self.print_navigation_metrics(
                    frame_count, analysis.navigation_result, processing_time
                )
                
                # Estatísticas de performance
                avg_fps = frame_count / total_time if total_time > 0 else 0
                print(f"⏱️ FPS médio: {avg_fps:.2f} | Total: {frame_count} frames")
                
        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário")
        
        finally:
            # Limpeza
            self.camera_manager.close_all()
            if HAS_DISPLAY:
                cv2.destroyAllWindows()
            
            # Estatísticas finais
            print(f"\n✅ Análise concluída:")
            print(f"   Frames processados: {frame_count}")
            print(f"   Tempo total: {total_time:.2f}s")
            if total_time > 0:
                print(f"   FPS médio: {frame_count/total_time:.2f}")
            print(f"   Imagens salvas: {frame_count//save_interval}")

def main():
    """Função principal do analisador"""
    print("🎯 TOFcam Main Analyzer (tofcam.lib)")
    print("=" * 50)
    
    try:
        # Criar visualizador
        visualizer = TOFCamVisualizer()
        
        # Opções de execução
        print("\n📋 Modos de análise:")
        print("1. Contínuo (ilimitado)")
        print("2. 50 frames")
        print("3. 100 frames")
        print("4. Single frame")
        
        choice = input("Escolha (1-4): ").strip()
        
        if choice == "1":
            visualizer.run_continuous_analysis()
        elif choice == "2":
            visualizer.run_continuous_analysis(max_frames=50)
        elif choice == "3":
            visualizer.run_continuous_analysis(max_frames=100)
        elif choice == "4":
            print("📸 Analisando single frame...")
            analysis = visualizer.analyze_frame()
            if analysis:
                visualizer.save_frame_analysis(1, analysis)
                if HAS_DISPLAY:
                    visualizer.display_frames(analysis)
                    print("Pressione qualquer tecla para fechar...")
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
                visualizer.print_navigation_metrics(1, analysis.navigation_result, 0.0)
            else:
                print("❌ Falha na análise")
        else:
            print("❌ Opção inválida")
    
    except Exception as e:
        logger.error(f"Erro na aplicação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()