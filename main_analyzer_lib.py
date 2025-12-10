#!/usr/bin/env python3
"""
TOFcam Main Analyzer - Versão refatorada usando analyzer_lib
Análise com persistência usando biblioteca centralizada
"""

import cv2
import numpy as np
import time
import os
from typing import Optional

# Imports locais  
from camera import *
from analyzer_lib import TOFAnalyzer, AnalysisConfig

class PersistentAnalyzer:
    """Analisador com persistência de frames"""
    
    def __init__(self, config: AnalysisConfig, cameras: list = None):
        self.config = config
        self.available_cameras = cameras or self._detect_cameras()
        self.current_camera = None
        self.camera = None
        
        if not self.available_cameras:
            raise RuntimeError("❌ Nenhuma câmera encontrada!")
            
        print(f"📹 Câmeras encontradas: {self.available_cameras}")
        
        # Inicializar analisador
        self.analyzer = TOFAnalyzer(config)
        
        # Criar diretório de saída
        os.makedirs(config.output_dir, exist_ok=True)
        print(f"📁 Diretório de saída: {config.output_dir}")
        
    def _detect_cameras(self):
        """Detectar câmeras disponíveis"""
        print("🔍 Detectando câmeras disponíveis...")
        cameras = []
        
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    h, w = frame.shape[:2]
                    print(f"✅ Câmera {i} disponível - resolução: ({h}, {w}, 3)")
                    cameras.append(i)
                cap.release()
        
        return cameras
    
    def switch_camera(self, camera_id: int) -> bool:
        """Trocar para uma câmera específica"""
        if camera_id not in self.available_cameras:
            print(f"❌ Câmera {camera_id} não disponível")
            return False
            
        print(f"📹 Trocando para câmera {camera_id}...")
        
        # Fechar câmera atual
        if self.camera:
            self.camera.release()
        
        # Abrir nova câmera
        self.camera = cv2.VideoCapture(camera_id)
        if not self.camera.isOpened():
            print(f"❌ Erro ao abrir câmera {camera_id}")
            return False
        
        self.current_camera = camera_id
        print(f"✅ Câmera {camera_id} ativada!")
        return True
    
    def process_single_frame(self) -> Optional[any]:
        """Processar um único frame"""
        if not self.camera or not self.camera.isOpened():
            print("❌ Câmera não está disponível")
            return None
        
        ret, frame = self.camera.read()
        if not ret or frame is None:
            print("❌ Erro ao capturar frame")
            return None
        
        # Processar frame usando a biblioteca
        analysis_result = self.analyzer.process_frame(frame, self.current_camera)
        
        return analysis_result
    
    def run_continuous(self, max_frames: int = None, display: bool = True):
        """Executar análise contínua"""
        if not self.available_cameras:
            print("❌ Nenhuma câmera disponível")
            return
        
        # Iniciar com primeira câmera
        if not self.switch_camera(self.available_cameras[0]):
            return
        
        frame_count = 0
        start_time = time.time()
        
        print("🎬 Iniciando análise contínua...")
        print("🔧 Pressione 'q' para sair, 'c' para trocar câmera, 's' para salvar frame")
        print("-" * 60)
        
        try:
            while True:
                # Verificar limite de frames
                if max_frames and frame_count >= max_frames:
                    print(f"✅ Limite de {max_frames} frames atingido")
                    break
                
                # Processar frame
                analysis_result = self.process_single_frame()
                if analysis_result is None:
                    continue
                
                frame_count += 1
                
                # Log periódico
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    strategic = analysis_result.strategic_result.get('target_yaw_delta', 0.0)
                    reactive = analysis_result.reactive_result.get('yaw_delta', 0.0)
                    
                    print(f"📊 Frame {frame_count} ({fps:.1f} FPS) - "
                          f"Strategic: {strategic:+.2f}, Reactive: {reactive:+.2f}")
                
                # Exibir se solicitado
                if display and analysis_result.combined_vis is not None:
                    cv2.imshow('TOFcam Analysis', analysis_result.combined_vis)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        print("🛑 Saindo...")
                        break
                    elif key == ord('c'):
                        # Trocar câmera
                        current_idx = self.available_cameras.index(self.current_camera)
                        next_idx = (current_idx + 1) % len(self.available_cameras)
                        next_camera = self.available_cameras[next_idx]
                        self.switch_camera(next_camera)
                    elif key == ord('s'):
                        # Força salvamento (mesmo se save_frames=False)
                        self._force_save_frame(analysis_result)
                
        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário")
        
        finally:
            self.cleanup()
            
        print(f"✅ Análise finalizada - {frame_count} frames processados")
    
    def _force_save_frame(self, analysis_result):
        """Forçar salvamento de frame individual"""
        import json
        
        timestamp_str = time.strftime("%Y%m%d_%H%M%S_%f")[:-3]  # milliseconds
        output_subdir = os.path.join(
            self.config.output_dir, 
            f"manual_cam{self.current_camera}_{timestamp_str}"
        )
        os.makedirs(output_subdir, exist_ok=True)
        
        # Salvar imagens
        cv2.imwrite(os.path.join(output_subdir, "original.jpg"), analysis_result.rgb_frame)
        cv2.imwrite(os.path.join(output_subdir, "depth.jpg"), analysis_result.depth_color)
        cv2.imwrite(os.path.join(output_subdir, "combined.jpg"), analysis_result.combined_vis)
        
        # Salvar dados
        analysis_data = {
            'frame_id': analysis_result.frame_id,
            'timestamp': analysis_result.timestamp,
            'camera_id': self.current_camera,
            'strategic': analysis_result.strategic_result,
            'reactive': analysis_result.reactive_result,
            'saved_manually': True
        }
        
        with open(os.path.join(output_subdir, "analysis.json"), 'w') as f:
            json.dump(analysis_data, f, indent=2, default=str)
        
        print(f"💾 Frame salvo manualmente em: {output_subdir}")
    
    def process_image_file(self, image_path: str, save_result: bool = True):
        """Processar arquivo de imagem"""
        if not os.path.exists(image_path):
            print(f"❌ Arquivo não encontrado: {image_path}")
            return None
        
        print(f"🖼️ Processando arquivo: {image_path}")
        
        # Carregar imagem
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"❌ Erro ao carregar imagem: {image_path}")
            return None
        
        # Processar usando a biblioteca
        analysis_result = self.analyzer.process_frame(frame, camera_id=999)  # ID especial para arquivos
        
        if save_result:
            # Salvar resultado
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            timestamp_str = time.strftime("%Y%m%d_%H%M%S")
            output_subdir = os.path.join(self.config.output_dir, f"file_{base_name}_{timestamp_str}")
            os.makedirs(output_subdir, exist_ok=True)
            
            # Salvar processamento
            cv2.imwrite(os.path.join(output_subdir, "original.jpg"), analysis_result.rgb_frame)
            cv2.imwrite(os.path.join(output_subdir, "depth.jpg"), analysis_result.depth_color)
            cv2.imwrite(os.path.join(output_subdir, "combined.jpg"), analysis_result.combined_vis)
            
            print(f"💾 Resultado salvo em: {output_subdir}")
        
        return analysis_result
    
    def cleanup(self):
        """Limpar recursos"""
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()

def main():
    print("🔬 TOFcam Main Analyzer (Lib Version)")
    print("=" * 40)
    
    # Configuração da análise
    config = AnalysisConfig(
        strategic_grid_size=(24, 32),
        reactive_grid_size=(12, 16),
        use_sophisticated_analysis=True,
        save_frames=True,      # Salvar frames automaticamente
        output_dir="output_images",
        web_format=False       # Não precisa de base64
    )
    
    try:
        # Criar analisador
        analyzer = PersistentAnalyzer(config)
        
        # Modo de operação
        import sys
        if len(sys.argv) > 1:
            # Modo arquivo
            image_path = sys.argv[1]
            result = analyzer.process_image_file(image_path)
            
            if result:
                print("✅ Processamento de arquivo concluído")
                strategic = result.strategic_result.get('target_yaw_delta', 0.0)
                reactive = result.reactive_result.get('yaw_delta', 0.0)
                print(f"📊 Strategic: {strategic:+.3f}, Reactive: {reactive:+.3f}")
        else:
            # Modo contínuo
            analyzer.run_continuous(display=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Interrompido")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()