#!/usr/bin/env python3
"""
Configurador de display para VS Code - TOFcam
Permite visualização em tempo real das imagens no VS Code
"""

import os
import subprocess
import sys
import cv2
import numpy as np

def check_display_environment():
    """Verificar ambiente de display atual."""
    
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
    
    # Verificar se estamos em WSL
    is_wsl = False
    try:
        with open('/proc/version', 'r') as f:
            if 'microsoft' in f.read().lower():
                is_wsl = True
                print("🐧 WSL detectado!")
    except:
        pass
    
    return {
        'display': display,
        'wayland': wayland_display,
        'session_type': xdg_session_type,
        'is_wsl': is_wsl
    }

def setup_x11_forwarding():
    """Configurar X11 forwarding para VS Code."""
    
    print("\n🔧 CONFIGURANDO X11 FORWARDING")
    print("-" * 30)
    
    # Verificar se xauth está disponível
    try:
        subprocess.run(['which', 'xauth'], check=True, capture_output=True)
        print("✅ xauth encontrado")
    except subprocess.CalledProcessError:
        print("❌ xauth não encontrado - instalando...")
        os.system("sudo apt update && sudo apt install -y xauth")
    
    # Configurar DISPLAY se não estiver definido
    if not os.environ.get('DISPLAY'):
        print("🔧 Configurando DISPLAY...")
        os.environ['DISPLAY'] = ':10.0'
        print(f"DISPLAY definido como: {os.environ['DISPLAY']}")
    
    # Verificar conexão X11
    try:
        result = subprocess.run(['xdpyinfo'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Conexão X11 funcionando")
            return True
        else:
            print("❌ Conexão X11 com problemas")
    except:
        print("⚠️  Não foi possível testar conexão X11")
    
    return False

def test_opencv_display():
    """Testar se OpenCV consegue criar janelas."""
    
    print("\n🧪 TESTANDO DISPLAY DO OPENCV")
    print("-" * 30)
    
    try:
        # Criar uma janela de teste
        test_img = np.zeros((300, 400, 3), dtype=np.uint8)
        cv2.putText(test_img, 'TOFcam Display Test', (50, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.namedWindow('TOFcam Test', cv2.WINDOW_NORMAL)
        cv2.imshow('TOFcam Test', test_img)
        
        print("✅ Janela de teste criada!")
        print("📋 Pressione qualquer tecla na janela ou 'q' para continuar...")
        
        key = cv2.waitKey(5000)  # Esperar 5 segundos ou tecla
        cv2.destroyAllWindows()
        
        if key != -1:
            print("✅ Interação com janela funcionando!")
            return True
        else:
            print("⚠️  Timeout - janela pode estar invisível")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao criar janela: {e}")
        return False

def setup_vscode_display():
    """Configurar display específico para VS Code."""
    
    print("\n🎯 CONFIGURAÇÃO PARA VS CODE")
    print("-" * 30)
    
    # Verificar se estamos no VS Code
    vscode_term = os.environ.get('TERM_PROGRAM')
    if vscode_term == 'vscode':
        print("✅ Executando no terminal do VS Code")
    else:
        print("⚠️  Não detectado terminal do VS Code")
    
    # Configurações para diferentes cenários
    setup_commands = []
    
    # WSL + VS Code
    if check_display_environment()['is_wsl']:
        print("🐧 Configuração para WSL...")
        setup_commands.extend([
            "export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0",
            "export LIBGL_ALWAYS_INDIRECT=1"
        ])
    
    # Linux nativo
    else:
        print("🐧 Configuração para Linux nativo...")
        setup_commands.extend([
            "export DISPLAY=:0",
            "xhost +local:"
        ])
    
    # Executar configurações
    for cmd in setup_commands:
        print(f"🔧 {cmd}")
        if cmd.startswith('export'):
            # Aplicar variável de ambiente
            var, value = cmd.replace('export ', '').split('=', 1)
            os.environ[var] = value
        else:
            # Executar comando do sistema
            os.system(cmd)
    
    return True

def create_vscode_launcher():
    """Criar script launcher para VS Code."""
    
    launcher_content = '''#!/bin/bash
# TOFcam Launcher para VS Code

echo "🚀 Iniciando TOFcam com display configurado..."

# Detectar ambiente
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "🐧 WSL detectado"
    export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
    export LIBGL_ALWAYS_INDIRECT=1
else
    echo "🐧 Linux nativo detectado"
    export DISPLAY=:0
    xhost +local: 2>/dev/null
fi

# Ativar ambiente conda
source ~/miniconda3/etc/profile.d/conda.sh
conda activate opencv

# Executar aplicação
python main_analyzer.py

echo "✅ TOFcam finalizado"
'''
    
    with open('run_tofcam.sh', 'w') as f:
        f.write(launcher_content)
    
    os.chmod('run_tofcam.sh', 0o755)
    print("✅ Launcher criado: run_tofcam.sh")

def install_display_dependencies():
    """Instalar dependências necessárias para display."""
    
    print("\n📦 INSTALANDO DEPENDÊNCIAS DE DISPLAY")
    print("-" * 40)
    
    dependencies = [
        "x11-apps",      # xeyes, xclock para teste
        "x11-xserver-utils",  # xdpyinfo, xwininfo
        "xauth",         # Autenticação X11
        "mesa-utils"     # glxinfo, glxgears
    ]
    
    for dep in dependencies:
        print(f"📦 Instalando {dep}...")
        result = os.system(f"sudo apt install -y {dep}")
        if result == 0:
            print(f"✅ {dep} instalado")
        else:
            print(f"❌ Erro ao instalar {dep}")

def main():
    """Função principal de configuração."""
    
    print("🎯 CONFIGURADOR DE DISPLAY - TOFcam")
    print("=" * 60)
    print("Este script configura o display para visualização")
    print("em tempo real no VS Code\n")
    
    # Verificar ambiente atual
    env_info = check_display_environment()
    
    # Menu de opções
    print("\n🎮 OPÇÕES DE CONFIGURAÇÃO:")
    print("1 - Configuração automática completa")
    print("2 - Apenas testar display atual")
    print("3 - Instalar dependências")
    print("4 - Criar launcher script")
    print("5 - Configuração manual passo a passo")
    print("0 - Sair")
    
    choice = input("\nEscolha uma opção (0-5): ").strip()
    
    if choice == "1":
        print("\n🔄 CONFIGURAÇÃO AUTOMÁTICA")
        install_display_dependencies()
        setup_vscode_display()
        setup_x11_forwarding()
        create_vscode_launcher()
        test_opencv_display()
        
    elif choice == "2":
        test_opencv_display()
        
    elif choice == "3":
        install_display_dependencies()
        
    elif choice == "4":
        create_vscode_launcher()
        
    elif choice == "5":
        print("\n📋 CONFIGURAÇÃO MANUAL:")
        print("1. Instale dependências: sudo apt install x11-apps xauth")
        print("2. Configure DISPLAY: export DISPLAY=:0")
        print("3. Para WSL: export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0")
        print("4. Teste: xeyes (deve abrir janela)")
        print("5. Execute: python main_analyzer.py")
        
    elif choice == "0":
        print("👋 Saindo...")
        
    else:
        print("❌ Opção inválida!")
        return main()
    
    print("\n" + "=" * 60)
    print("🎯 Configuração concluída!")
    print("💡 Para executar o TOFcam: ./run_tofcam.sh")
    print("💡 Ou diretamente: python main_analyzer.py")

if __name__ == "__main__":
    main()