#!/usr/bin/env python3
"""
Demo: Uso Básico da Biblioteca Centralizada
Exemplo básico usando analyzer_lib.py para análise em tempo real.
"""

import cv2
import sys
import os

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tofcam.core import TOFAnalyzer, AnalysisConfig

def basic_analysis_example():
    """Exemplo básico de análise usando a biblioteca centralizada."""
    
    print("🚀 DEMO: USO BÁSICO - Biblioteca Centralizada")
    print("=" * 50)
    
    try:
        # Configurar análise para exibição em tempo real (sem persistir)
        config = AnalysisConfig(
            save_frames=False,
            web_format=False,
            output_dir="demos/outputs"
        )
        
        # Inicializar analisador
        print("⚙️  Inicializando TOFAnalyzer...")
        analyzer = TOFAnalyzer(config=config)
        
        print("✅ Sistema pronto!")
        print("\nPressione 'q' para sair ou 'SPACE' para pausar")
        print("Análise em tempo real usando biblioteca centralizada")
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
                    
                # Usar análise da biblioteca centralizada
                result = analyzer.process_frame(frame)
                
                frame_count += 1
                
                # Mostrar informações da análise
                print(f"\r📊 Frame {frame_count}: "
                      f"Strategic={result.strategic_result['target_yaw_delta']:+.3f}°, "
                      f"Reactive={result.reactive_result['yaw_delta']:+.3f}°", end="")
                
                # Exibir janelas (se display disponível)  
                try:
                    cv2.imshow('Original', result.rgb_frame)
                    cv2.imshow('Análise TOF', result.combined_vis)
                except:
                    # Sem display - modo texto apenas
                    pass
            
            # Controles de teclado
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):
                paused = not paused
                if paused:
                    print("\n⏸️ PAUSADO - Pressione SPACE para continuar")
                else:
                    print("▶️ CONTINUANDO...")
                    
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
        print("✅ Demo concluído!")

if __name__ == "__main__":
    basic_analysis_example()