#!/usr/bin/env python3
"""
TOFcam com visualização em tempo real e salvamento de imagens para avaliação
"""
import cv2
import os
import sys
import subprocess
import numpy as np
from datetime import datetime
from pathlib import Path
from camera import CameraSource, PerceptionSystem
from depth_estimator import MidasDepthEstimator
from mapping import ZoneMapper, StrategicPlanner, ReactiveAvoider
from modules import ObstacleAnalyzer
from view import depth_to_color, draw_zone_grid, draw_yaw_arrow

# Verificar se há display X11 disponível
def check_display():
    """Verifica se há display X11 disponível para visualização"""
    try:
        # Verifica variável DISPLAY
        display = os.environ.get('DISPLAY', '')
        if not display:
            return False
        
        # Testa se o servidor X11 está respondendo
        result = subprocess.run(['xset', 'q'], 
                              capture_output=True, 
                              timeout=2)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

HAS_DISPLAY = check_display()

class TOFCamVisualizer:
    def __init__(self, output_dir="output_images"):
        self.base_dir = Path(output_dir)
        
        # Criar estrutura de pastas por tipo
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
        
        # Configurar janelas de visualização
        self.setup_windows()
        
    def setup_windows(self):
        """Configura as janelas de visualização se display disponível"""
        if not HAS_DISPLAY:
            print("⚠️ Nenhum display detectado - modo somente salvamento")
            return
            
        try:
            cv2.namedWindow("TOFCam - Camera Feed", cv2.WINDOW_NORMAL)
            cv2.namedWindow("TOFCam - Depth Map", cv2.WINDOW_NORMAL)
            cv2.namedWindow("TOFCam - Strategic Grid", cv2.WINDOW_NORMAL)
            cv2.namedWindow("TOFCam - Reactive Grid", cv2.WINDOW_NORMAL)
            
            # Redimensionar janelas para caber na tela
            cv2.resizeWindow("TOFCam - Camera Feed", 320, 240)
            cv2.resizeWindow("TOFCam - Depth Map", 320, 240)
            cv2.resizeWindow("TOFCam - Strategic Grid", 320, 240)
            cv2.resizeWindow("TOFCam - Reactive Grid", 320, 240)
            
            # Posicionar janelas
            cv2.moveWindow("TOFCam - Camera Feed", 0, 0)
            cv2.moveWindow("TOFCam - Depth Map", 340, 0)
            cv2.moveWindow("TOFCam - Strategic Grid", 0, 280)
            cv2.moveWindow("TOFCam - Reactive Grid", 340, 280)
            
            print("✅ Janelas de visualização configuradas")
            
        except Exception as e:
            print(f"⚠️ Erro ao configurar janelas: {e}")
            print("🔄 Mudando para modo somente salvamento")
        
    def save_frame_analysis(self, frame_num, frame, depth_map, strategic_grid, 
                           reactive_grid, strategic_mapper, reactive_mapper,
                           strategic_plan, reactive_cmd):
        """Salva análise completa de um frame em pastas organizadas"""
        
        # Criar timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        frame_prefix = f"frame_{frame_num:04d}_{timestamp}"
        
        # 1. Frame original da câmera
        camera_path = self.folders['camera'] / f"{frame_prefix}.jpg"
        cv2.imwrite(str(camera_path), frame)
        
        # 2. Mapa de profundidade
        depth_color = depth_to_color(depth_map)
        depth_path = self.folders['depth'] / f"{frame_prefix}.jpg"
        cv2.imwrite(str(depth_path), depth_color)
        
        # 3. Grid estratégico com seta direcional
        strategic_img = draw_zone_grid(
            depth_color.copy(),
            strategic_grid,
            strategic_mapper.roi
        )
        # Adicionar seta estratégica (verde)
        strategic_img = draw_yaw_arrow(
            strategic_img, 
            strategic_plan.target_yaw_delta, 
            color=(0, 255, 0),
            label="Strategic"
        )
        strategic_path = self.folders['strategic'] / f"{frame_prefix}.jpg"
        cv2.imwrite(str(strategic_path), strategic_img)
        
        # 4. Grid reativo com seta direcional
        reactive_img = draw_zone_grid(
            depth_color.copy(),
            reactive_grid,
            reactive_mapper.roi
        )
        # Adicionar seta reativa (laranja)
        reactive_img = draw_yaw_arrow(
            reactive_img, 
            reactive_cmd.yaw_delta, 
            color=(0, 165, 255),
            label="Reactive"
        )
        reactive_path = self.folders['reactive'] / f"{frame_prefix}.jpg"
        cv2.imwrite(str(reactive_path), reactive_img)
        
        # 5. Criar imagem combinada para análise
        combined = self.create_combined_analysis(
            frame, depth_color, strategic_img, reactive_img,
            strategic_plan, reactive_cmd, frame_num
        )
        combined_path = self.folders['analysis'] / f"{frame_prefix}.jpg"
        cv2.imwrite(str(combined_path), combined)
        
        return {
            'frame_num': frame_num,
            'timestamp': timestamp,
            'files': {
                'camera': camera_path,
                'depth': depth_path,
                'strategic': strategic_path,
                'reactive': reactive_path,
                'analysis': combined_path
            },
            'strategic_plan': {
                'yaw_delta': strategic_plan.target_yaw_delta,
                'confidence': strategic_plan.confidence,
                'min_distance': strategic_plan.min_distance_ahead
            },
            'reactive_cmd': {
                'yaw_delta': reactive_cmd.yaw_delta,
                'forward_scale': reactive_cmd.forward_scale,
                'emergency_brake': reactive_cmd.emergency_brake
            }
        }
    
    def create_combined_analysis(self, frame, depth, strategic, reactive, 
                               strategic_plan, reactive_cmd, frame_num):
        """Cria imagem combinada com todas as análises e dados"""
        h, w = frame.shape[:2]
        
        # Criar canvas 2x2
        combined = np.zeros((h*2 + 60, w*2, 3), dtype=np.uint8)
        
        # Posicionar imagens
        combined[0:h, 0:w] = frame  # Superior esquerdo
        combined[0:h, w:w*2] = depth  # Superior direito
        combined[h+60:h*2+60, 0:w] = strategic  # Inferior esquerdo
        combined[h+60:h*2+60, w:w*2] = reactive  # Inferior direito
        
        # Adicionar texto de análise
        text_area = combined[h:h+60, :]
        text_area.fill(40)  # Fundo cinza escuro
        
        # Textos informativos
        texts = [
            f"Frame: {frame_num} | Strategic Yaw: {strategic_plan.target_yaw_delta:.3f}° | Confidence: {strategic_plan.confidence:.2f}",
            f"Reactive Yaw: {reactive_cmd.yaw_delta:.3f}° | Forward Scale: {reactive_cmd.forward_scale:.2f} | Emergency: {reactive_cmd.emergency_brake}",
            f"Min Distance: {strategic_plan.min_distance_ahead:.2f}m"
        ]
        
        for i, text in enumerate(texts):
            cv2.putText(combined, text, (10, h + 20 + i*15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return combined
    
    def show_realtime(self, frame, depth_map, strategic_grid, reactive_grid,
                     strategic_mapper, reactive_mapper, strategic_plan, reactive_cmd):
        """Exibe visualização em tempo real se display disponível"""
        
        if not HAS_DISPLAY:
            # Modo texto - apenas imprimir dados
            return 0  # Nenhuma tecla pressionada
        
        try:
            # Preparar imagens
            depth_color = depth_to_color(depth_map)
            
            strategic_img = draw_zone_grid(
                depth_color.copy(),
                strategic_grid,
                strategic_mapper.roi
            )
            
            reactive_img = draw_zone_grid(
                depth_color.copy(),
                reactive_grid,
                reactive_mapper.roi
            )
            
            # Desenhar setas direcionais
            # Seta verde para planejamento estratégico
            strategic_img = draw_yaw_arrow(
                strategic_img, 
                strategic_plan.target_yaw_delta, 
                color=(0, 255, 0),  # Verde
                label="Strategic"
            )
            
            # Seta laranja para sistema reativo
            reactive_img = draw_yaw_arrow(
                reactive_img, 
                reactive_cmd.yaw_delta, 
                color=(0, 165, 255),  # Laranja
                label="Reactive"
            )
            
            # Adicionar informações de texto nas imagens
            frame_with_info = frame.copy()
            cv2.putText(frame_with_info, f"TOFCam Live Feed", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            depth_with_info = depth_color.copy()
            cv2.putText(depth_with_info, f"Depth Map", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            strategic_with_info = strategic_img.copy()
            cv2.putText(strategic_with_info, f"Strategic: {strategic_plan.target_yaw_delta:.2f}°", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(strategic_with_info, f"Conf: {strategic_plan.confidence:.2f}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            reactive_with_info = reactive_img.copy()
            cv2.putText(reactive_with_info, f"Reactive: {reactive_cmd.yaw_delta:.2f}°", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            cv2.putText(reactive_with_info, f"Scale: {reactive_cmd.forward_scale:.2f}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            
            # Exibir nas janelas
            cv2.imshow("TOFCam - Camera Feed", frame_with_info)
            cv2.imshow("TOFCam - Depth Map", depth_with_info)
            cv2.imshow("TOFCam - Strategic Grid", strategic_with_info)
            cv2.imshow("TOFCam - Reactive Grid", reactive_with_info)
            
            # Retornar tecla pressionada
            return cv2.waitKey(1) & 0xFF
            
        except Exception as e:
            print(f"⚠️ Erro na visualização: {e}")
            return 0
    
    def close_windows(self):
        """Fecha todas as janelas"""
        cv2.destroyAllWindows()

def main():
    print("🚀 TOFcam - ANÁLISE COM VISUALIZAÇÃO EM TEMPO REAL")
    print("=" * 60)
    
    # Inicializar visualizador
    visualizer = TOFCamVisualizer("output_images")
    
    # Detectar câmera
    print("🔍 Detectando câmeras...")
    working_cameras = []
    for i in [0, 2]:
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    working_cameras.append(i)
                    print(f"✅ Câmera {i} detectada")
            cap.release()
        except:
            pass
    
    if not working_cameras:
        print("⚠️ Usando modo sintético")
        camera = CameraSource(0, use_test_image=True)
    else:
        # Priorizar câmera 2 se disponível
        if 2 in working_cameras:
            camera_index = 2
        else:
            camera_index = working_cameras[0]
        print(f"📹 Usando câmera {camera_index}")
        camera = CameraSource(camera_index, use_test_image=False)
    
    camera.open()
    
    # Inicializar sistema
    print("🧠 Carregando componentes...")
    depth_estimator = MidasDepthEstimator(model_type="MiDaS_small")
    
    strategic_mapper = ZoneMapper(
        grid_h=24, grid_w=32,
        warn_threshold=0.35, emergency_threshold=0.20,
        roi=(0.10, 1.00, 0.10, 0.90)
    )
    
    reactive_mapper = ZoneMapper(
        grid_h=12, grid_w=16,
        warn_threshold=0.25, emergency_threshold=0.12,
        roi=(0.50, 1.00, 0.25, 0.75)
    )
    
    planner = StrategicPlanner()
    avoider = ReactiveAvoider()
    
    system = PerceptionSystem(
        camera, depth_estimator, strategic_mapper,
        reactive_mapper, planner, avoider
    )
    
    print("✅ Sistema pronto!")
    print("=" * 60)
    
    if HAS_DISPLAY:
        print("▶️ CONTROLES (MODO VISUAL):")
        print("   ESC ou Q: Sair")
        print("   S: Salvar frame atual para análise") 
        print("   ESPAÇO: Pausar/Continuar")
        print("🖼️ Visualização em tempo real nas janelas")
    else:
        print("▶️ MODO SALVAMENTO (SEM DISPLAY):")
        print("   Ctrl+C: Sair")
        print("   Auto-save: A cada 20 frames")
        print("💾 Apenas salvamento de imagens")
    
    print("📂 Imagens organizadas em: output_images/")
    print("   📁 camera_original/     - Imagens da câmera")
    print("   📁 depth_maps/          - Mapas de profundidade")
    print("   📁 strategic_navigation/ - Navegação estratégica")
    print("   📁 reactive_avoidance/   - Evasão reativa")
    print("   📁 complete_analysis/    - Análise completa")
    print("=" * 60)
    
    frame_count = 0
    saved_frames = []
    paused = False
    
    try:
        while True:
            if not paused:
                # Processar frame
                output = system.process_once()
                if output is None:
                    print("⚠️ Falha ao processar frame")
                    break
                
                frame_count += 1
            
            # Visualização em tempo real (se disponível)
            key = visualizer.show_realtime(
                output.frame, output.depth_map,
                output.strategic_grid, output.reactive_grid,
                strategic_mapper, reactive_mapper,
                output.strategic_plan, output.reactive_cmd
            )
            
            # Feedback no modo sem display
            if not HAS_DISPLAY and frame_count % 10 == 0:
                print(f"📊 Frame {frame_count}: Strategic={output.strategic_plan.target_yaw_delta:.3f}°, "
                      f"Reactive={output.reactive_cmd.yaw_delta:.3f}°, Scale={output.reactive_cmd.forward_scale:.2f}")
            
            # Controles do teclado
            if key == 27 or key == ord('q'):  # ESC ou Q
                break
            elif key == ord('s'):  # Salvar frame
                print(f"\n💾 Salvando análise do frame {frame_count}...")
                analysis = visualizer.save_frame_analysis(
                    frame_count, output.frame, output.depth_map,
                    output.strategic_grid, output.reactive_grid,
                    strategic_mapper, reactive_mapper,
                    output.strategic_plan, output.reactive_cmd
                )
                saved_frames.append(analysis)
                print(f"✅ Frame {frame_count} salvo! Total salvos: {len(saved_frames)}")
            elif key == ord(' ') and HAS_DISPLAY:  # Pausar/Continuar (só no modo visual)
                paused = not paused
                status = "PAUSADO" if paused else "RODANDO"
                print(f"⏸️ Status: {status}")
            
            # Auto-salvar (mais frequente no modo sem display)
            save_interval = 20 if not HAS_DISPLAY else 100
            if frame_count % save_interval == 0 and frame_count > 0:
                print(f"\n📊 Auto-salvando frame {frame_count} para análise...")
                analysis = visualizer.save_frame_analysis(
                    frame_count, output.frame, output.depth_map,
                    output.strategic_grid, output.reactive_grid,
                    strategic_mapper, reactive_mapper,
                    output.strategic_plan, output.reactive_cmd
                )
                saved_frames.append(analysis)
                
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário")
    
    finally:
        # Limpeza
        camera.release()
        visualizer.close_windows()
        
        # Relatório final
        print(f"\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL:")
        print(f"   📹 Frames processados: {frame_count}")
        print(f"   💾 Frames salvos para análise: {len(saved_frames)}")
        print(f"   📂 Pasta de saída: output_images/")
        
        if saved_frames:
            print("\n🔍 AMOSTRAS SALVAS:")
            for i, analysis in enumerate(saved_frames[-5:]):  # Últimas 5
                print(f"   {i+1}. Frame {analysis['frame_num']} - {analysis['timestamp']}")
                print(f"      Strategic: {analysis['strategic_plan']['yaw_delta']:.3f}°")
                print(f"      Reactive: {analysis['reactive_cmd']['yaw_delta']:.3f}°")
        
        print("\n✅ Análise concluída!")

if __name__ == "__main__":
    main()