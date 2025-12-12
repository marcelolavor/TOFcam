#!/usr/bin/env python3
"""
Display Setup for TOFcam - Refactored with tofcam.lib
======================================================

Configurador de display inteligente usando tofcam.lib.
Detecta automaticamente o melhor método de visualização.
"""

import os
import subprocess
import sys
import cv2
import numpy as np
import time
from typing import Dict, Optional, Tuple

# Imports da biblioteca centralizada
from tofcam.lib import (
    create_camera_manager, create_depth_estimator,
    create_render_pipeline, discover_cameras, 
    CameraConfig, TOFConfig, logger
)

class DisplaySetup:
    """Configurador inteligente de display usando tofcam.lib"""
    
    def __init__(self):
        self.config = TOFConfig()
        self.environment_info = {}
        
    def check_display_environment(self) -> Dict:
        """Verificar ambiente de display atual"""
        print("🖥️  VERIFICAÇÃO DO AMBIENTE DE DISPLAY")
        print("=" * 50)
        
        # Verificar variáveis de ambiente
        display = os.environ.get('DISPLAY')
        wayland_display = os.environ.get('WAYLAND_DISPLAY')
        xdg_session_type = os.environ.get('XDG_SESSION_TYPE')
        
        print(f"DISPLAY: {display}")
        print(f"WAYLAND_DISPLAY: {wayland_display}")
        print(f"XDG_SESSION_TYPE: {xdg_session_type}")
        print(f"Sistema: {os.uname().sysname}")
        
        # Verificar WSL
        is_wsl = False
        try:
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower():
                    is_wsl = True
                    print("🐧 WSL detectado!")
        except:
            pass
        
        # Verificar SSH
        is_ssh = bool(os.environ.get('SSH_CLIENT') or os.environ.get('SSH_TTY'))
        if is_ssh:
            print("🔗 Conexão SSH detectada")
        
        self.environment_info = {
            'display': display,
            'wayland': wayland_display,
            'session_type': xdg_session_type,
            'is_wsl': is_wsl,
            'is_ssh': is_ssh
        }
        
        return self.environment_info
    
    def setup_x11_forwarding(self) -> bool:
        """Configurar X11 forwarding"""
        print("\\n🔧 CONFIGURANDO X11 FORWARDING")
        print("-" * 30)
        
        try:
            # Verificar se xauth está instalado
            subprocess.run(['which', 'xauth'], check=True, capture_output=True)
            print("✅ xauth encontrado")
        except subprocess.CalledProcessError:
            print("❌ xauth não encontrado. Instalando...")
            try:
                subprocess.run(['sudo', 'apt', 'update'], check=True)
                subprocess.run(['sudo', 'apt', 'install', '-y', 'xauth'], check=True)
                print("✅ xauth instalado")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erro ao instalar xauth: {e}")
                return False
        
        # Configurar DISPLAY se necessário
        if not os.environ.get('DISPLAY'):
            if self.environment_info.get('is_wsl'):
                # WSL2 específico
                try:
                    result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
                    host_ip = result.stdout.strip().split()[0]
                    os.environ['DISPLAY'] = f"{host_ip}:0.0"
                    print(f"✅ DISPLAY definido para WSL: {os.environ['DISPLAY']}")
                except Exception as e:
                    print(f"⚠️ Erro ao configurar DISPLAY WSL: {e}")
                    os.environ['DISPLAY'] = ':0.0'
            else:
                # SSH padrão
                os.environ['DISPLAY'] = ':10.0'
                print(f"✅ DISPLAY definido para SSH: {os.environ['DISPLAY']}")
        
        return True
    
    def test_opencv_display(self) -> bool:
        """Testar capacidade de display do OpenCV"""
        print("\\n🧪 TESTANDO OPENCV DISPLAY")
        print("-" * 25)
        
        try:
            # Criar imagem de teste
            test_img = np.zeros((200, 300, 3), dtype=np.uint8)
            cv2.putText(test_img, "TOFcam Test", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Tentar mostrar
            cv2.namedWindow("Display Test", cv2.WINDOW_NORMAL)
            cv2.imshow("Display Test", test_img)
            
            print("✅ Janela de teste criada")
            print("⏱️ Aguarde 3 segundos ou pressione qualquer tecla...")
            
            key = cv2.waitKey(3000)
            cv2.destroyAllWindows()
            
            if key != -1:
                print("✅ Interação detectada - display funcionando!")
            else:
                print("⚠️ Timeout - mas janela foi criada")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste de display: {e}")
            cv2.destroyAllWindows()
            return False
    
    def test_camera_display(self) -> bool:
        """Testar display com câmera real usando tofcam.lib"""
        print("\\n📹 TESTANDO DISPLAY COM CÂMERA")
        print("-" * 30)
        
        try:
            # Descobrir câmeras
            cameras = discover_cameras()
            if not cameras:
                print("⚠️ Nenhuma câmera física, testando com imagem sintética")
                self.config.camera.use_test_image = True
                cameras = [0]
            else:
                print(f"✅ Câmeras encontradas: {cameras}")
            
            # Criar gerenciador de câmera
            camera_manager = create_camera_manager()
            camera_config = CameraConfig(
                index=cameras[0],
                width=640,
                height=480,
                fps=30,
                use_test_image=self.config.camera.use_test_image
            )
            
            if not camera_manager.add_camera(camera_config):
                print("❌ Falha ao inicializar câmera")
                return False
            
            print("✅ Câmera inicializada")
            print("⏱️ Capturando 5 frames de teste...")
            
            # Janela de display
            cv2.namedWindow("Camera Test - tofcam.lib", cv2.WINDOW_NORMAL)
            
            # Capturar alguns frames
            for i in range(5):
                frame = camera_manager.read_frame()
                if frame is not None:
                    # Adicionar overlay de teste
                    cv2.putText(frame, f"Frame {i+1}/5", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.imshow("Camera Test - tofcam.lib", frame)
                    
                    key = cv2.waitKey(500)  # 500ms por frame
                    if key == 27:  # ESC
                        break
                else:
                    print(f"⚠️ Frame {i+1} inválido")
            
            # Limpeza
            camera_manager.close_all()
            cv2.destroyAllWindows()
            
            print("✅ Teste de câmera concluído!")
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste de câmera: {e}")
            try:
                camera_manager.close_all()
                cv2.destroyAllWindows()
            except:
                pass
            return False
    
    def test_depth_visualization(self) -> bool:
        """Testar visualização de profundidade usando tofcam.lib"""
        print("\\n🎯 TESTANDO VISUALIZAÇÃO DE PROFUNDIDADE")
        print("-" * 40)
        
        try:
            # Criar componentes
            camera_manager = create_camera_manager()
            depth_estimator = create_depth_estimator()
            render_pipeline = create_render_pipeline()
            
            # Configurar câmera
            cameras = discover_cameras()
            if not cameras:
                self.config.camera.use_test_image = True
                cameras = [0]
            
            camera_config = CameraConfig(
                index=cameras[0],
                use_test_image=self.config.camera.use_test_image
            )
            
            if not camera_manager.add_camera(camera_config):
                print("❌ Falha ao configurar câmera para teste depth")
                return False
            
            print("✅ Componentes de profundidade criados")
            print("⏱️ Testando estimativa MiDaS...")
            
            # Janelas de teste
            cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
            cv2.namedWindow("Depth Map", cv2.WINDOW_NORMAL)
            
            # Posicionar janelas
            cv2.moveWindow("Original", 0, 0)
            cv2.moveWindow("Depth Map", 350, 0)
            
            # Capturar e processar 3 frames
            for i in range(3):
                frame = camera_manager.read_frame()
                if frame is None:
                    continue
                
                print(f"  Processando frame {i+1}/3...")
                
                # Estimativa de profundidade
                depth_map = depth_estimator.estimate_depth(frame)
                depth_colored = render_pipeline.render_depth_colored(depth_map)
                
                # Adicionar overlays informativos
                cv2.putText(frame, f"Original {i+1}/3", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(depth_colored, f"Depth {i+1}/3", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                # Mostrar
                cv2.imshow("Original", frame)
                cv2.imshow("Depth Map", depth_colored)
                
                key = cv2.waitKey(1500)  # 1.5s por frame
                if key == 27:
                    break
            
            # Limpeza
            camera_manager.close_all()
            cv2.destroyAllWindows()
            
            print("✅ Teste de visualização de profundidade concluído!")
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste de profundidade: {e}")
            import traceback
            traceback.print_exc()
            try:
                camera_manager.close_all()
                cv2.destroyAllWindows()
            except:
                pass
            return False
    
    def run_complete_setup(self):
        """Executar setup completo do display"""
        print("🚀 SETUP COMPLETO DO DISPLAY TOFCAM")
        print("=" * 50)
        
        # 1. Verificar ambiente
        env_info = self.check_display_environment()
        
        # 2. Configurar X11 se necessário
        if env_info.get('is_ssh') or env_info.get('is_wsl'):
            if not self.setup_x11_forwarding():
                print("⚠️ Falha no X11 forwarding, mas continuando...")
        
        # 3. Teste básico OpenCV
        print("\\n" + "="*50)
        basic_test = self.test_opencv_display()
        
        # 4. Teste com câmera
        print("\\n" + "="*50)
        camera_test = self.test_camera_display()
        
        # 5. Teste de profundidade
        print("\\n" + "="*50)
        depth_test = self.test_depth_visualization()
        
        # Resultado final
        print("\\n" + "="*50)
        print("📊 RESULTADO FINAL")
        print("-" * 20)
        print(f"✅ Display básico:      {'✅ OK' if basic_test else '❌ FALHOU'}")
        print(f"📹 Câmera:              {'✅ OK' if camera_test else '❌ FALHOU'}")
        print(f"🎯 Profundidade:        {'✅ OK' if depth_test else '❌ FALHOU'}")
        
        if all([basic_test, camera_test, depth_test]):
            print("\\n🎉 SETUP COMPLETO! TOFcam pronto para visualização!")
            print("\\n💡 Dicas:")
            print("   - Use main.py para visualização completa")
            print("   - Use main_analyzer.py para análise detalhada")
            print("   - Pressione ESC para sair das janelas")
        else:
            print("\\n⚠️ Alguns testes falharam. TOFcam funcionará em modo console.")
            print("\\n💡 Troubleshooting:")
            if not basic_test:
                print("   - Verifique conexão X11/display")
            if not camera_test:
                print("   - Verifique permissões de câmera")
            if not depth_test:
                print("   - Verifique instalação MiDaS")

def main():
    """Função principal do configurador"""
    print("🎯 TOFcam Display Setup (tofcam.lib)")
    print("=" * 50)
    
    setup = DisplaySetup()
    
    print("\\n📋 Opções:")
    print("1. Setup completo")
    print("2. Apenas teste básico")
    print("3. Apenas teste câmera")
    print("4. Apenas teste profundidade")
    print("5. Verificar ambiente")
    
    choice = input("\\nEscolha (1-5): ").strip()
    
    if choice == "1":
        setup.run_complete_setup()
    elif choice == "2":
        setup.check_display_environment()
        setup.test_opencv_display()
    elif choice == "3":
        setup.check_display_environment()
        setup.test_camera_display()
    elif choice == "4":
        setup.check_display_environment()
        setup.test_depth_visualization()
    elif choice == "5":
        setup.check_display_environment()
    else:
        print("❌ Opção inválida")

if __name__ == "__main__":
    main()