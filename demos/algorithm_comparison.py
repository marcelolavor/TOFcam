#!/usr/bin/env python3
"""
Demo: Comparação de Algoritmos
Exemplo visual comparando algoritmos Strategic e Reactive usando biblioteca centralizada.
"""

import cv2
import numpy as np
import sys
import os

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer_lib import TOFAnalyzer, AnalysisConfig
from mapping import StrategicNavigationAlgorithm, ReactiveAvoidanceAlgorithm
from view import create_depth_colormap, draw_yaw_arrow

def create_comparison_view(frame, depth_map, strategic_result, reactive_result):
    """Criar visualização comparativa lado a lado."""
    
    # Criar mapa de profundidade colorido
    depth_colored = create_depth_colormap(depth_map)
    
    # Criar versões com setas
    strategic_vis = depth_colored.copy()
    reactive_vis = depth_colored.copy()
    
    h, w = frame.shape[:2]
    
    # Desenhar setas com cores diferentes
    draw_yaw_arrow(strategic_vis, strategic_result['target_yaw_delta'], w, h, 
                   color=(0, 255, 255), thickness=3)  # Amarelo ciano
    draw_yaw_arrow(reactive_vis, reactive_result['yaw_delta'], w, h, 
                   color=(255, 0, 255), thickness=3)  # Magenta
    
    # Adicionar textos informativos
    strategic_text = f"STRATEGIC: {strategic_result['target_yaw_delta']:+.3f}°"
    reactive_text = f"REACTIVE: {reactive_result['yaw_delta']:+.3f}°"
    
    cv2.putText(strategic_vis, strategic_text, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(reactive_vis, reactive_text, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
    
    # Criar visualização combinada (2x2)
    top_row = np.hstack([frame, depth_colored])
    bottom_row = np.hstack([strategic_vis, reactive_vis])
    combined = np.vstack([top_row, bottom_row])
    
    # Adicionar labels
    h_combined, w_combined = combined.shape[:2]
    
    # Labels para cada quadrante
    labels = [
        ("CAMERA ORIGINAL", 10, 25),
        ("DEPTH MAP", w//2 + 10, 25),
        ("STRATEGIC NAVIGATION", 10, h//2 + 25),
        ("REACTIVE AVOIDANCE", w//2 + 10, h//2 + 25)
    ]
    
    for label, x, y in labels:
        cv2.putText(combined, label, (x, y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    return combined

def algorithm_comparison_demo():
    """Demo comparativo usando a biblioteca centralizada mais algoritmos individuais."""
    
    print("🔄 DEMO: COMPARAÇÃO DE ALGORITMOS")
    print("=" * 50)
    
    try:
        # Configuração básica sem persistir 
        config = AnalysisConfig(
            save_frames=False,
            web_format=False,
            output_dir="demos/outputs"
        )
        
        print("⚙️ Inicializando TOFAnalyzer + algoritmos individuais...")
        analyzer = TOFAnalyzer(config=config)
        
        # Algoritmos para comparação individual
        strategic = StrategicNavigationAlgorithm()
        reactive = ReactiveAvoidanceAlgorithm()
        
        print("✅ Sistema pronto!")
        print("\nControles:")
        print("  'q': Sair")
        print("  's': Salvar frame atual") 
        print("  'SPACE': Pausar/Continuar")
        print("-" * 50)
        
        frame_count = 0
        paused = False
        
        while True:
            if not paused:
                # Capturar frame da câmera
                frame = analyzer.camera_manager.read()
                if frame is None:
                    print("❌ Erro ao capturar frame")
                    break
                    
                # Análise principal usando biblioteca
                result = analyzer.process_frame(frame)
                
                frame_count += 1
                
                # Análises individuais para comparação
                strategic_result = strategic.process(result.depth_map)
                reactive_result = reactive.process(result.depth_map)
                
                # Criar visualização comparativa personalizada
                comparison_view = create_comparison_view(
                    result.rgb_frame, result.depth_map, 
                    strategic_result, reactive_result)
                
                # Informações no terminal com comparações
                lib_strategic_yaw = result.strategic_result['target_yaw_delta']
                lib_reactive_yaw = result.reactive_result['yaw_delta']
                strategic_yaw = strategic_result['target_yaw_delta']
                reactive_yaw = reactive_result['yaw_delta']
                
                diff_strategic = abs(lib_strategic_yaw - strategic_yaw)
                diff_reactive = abs(lib_reactive_yaw - reactive_yaw)
                diff_algorithms = abs(strategic_yaw - reactive_yaw)
                
                if diff_algorithms < 0.1:
                    agreement = "✅"
                elif diff_algorithms < 0.3:
                    agreement = "🟡"
                else:
                    agreement = "🔴"
                
                print(f"\r📊 Frame {frame_count}: "
                      f"Lib-S={lib_strategic_yaw:+.3f}°, "
                      f"Strategic={strategic_yaw:+.3f}°, "
                      f"Reactive={reactive_yaw:+.3f}°, "
                      f"Diff={diff_algorithms:.3f}° {agreement}", end="")
                
                # Exibir comparação
                try:
                    cv2.imshow('TOFcam - Algorithm Comparison', comparison_view)
                    cv2.imshow('TOFcam - Library Result', result.combined_vis)
                except:
                    # Sem display disponível
                    pass
            
            # Controles de teclado
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):
                paused = not paused
                status = "PAUSADO" if paused else "CONTINUANDO"
                print(f"\n{status}...")
            elif key == ord('s'):
                # Salvar frame atual
                filename = f"comparison_frame_{frame_count:04d}.jpg"
                cv2.imwrite(filename, comparison_view)
                print(f"\n💾 Salvo: {filename}")
                    
    except KeyboardInterrupt:
        print("\n\n🛑 Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    finally:
        print("\n🔧 Limpando recursos...")
        try:
            analyzer.cleanup()
        except:
            pass
        cv2.destroyAllWindows()
        print("✅ Demo comparação concluído!")

if __name__ == "__main__":
    algorithm_comparison_demo()