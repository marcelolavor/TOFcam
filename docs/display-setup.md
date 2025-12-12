# 🖥️ Display Setup - TOFcam

**Configuração de ambiente gráfico para visualização em diferentes ambientes.**

## 📋 **Índice**

1. [Soluções Disponíveis](#soluções-disponíveis)
2. [Interface Web (Recomendado)](#interface-web)
3. [Configuração X11/Wayland](#configuração-x11)
4. [WSL/WSL2 Setup](#wsl-setup)
5. [SSH/Remote Setup](#ssh-setup)
6. [Troubleshooting Display](#troubleshooting)
7. [Alternativas sem Display](#alternativas)

---

## 🎯 **Soluções Disponíveis** {#soluções-disponíveis}

### **Ordem de Prioridade (Recomendada)**

| Solução | Compatibilidade | Facilidade | Performance |
|---------|-----------------|------------|-------------|
| 🥇 **[Interface Web](#interface-web)** | Universal | Fácil | Excelente |
| 🥈 **[X11 Local](#configuração-x11)** | Linux nativo | Médio | Máxima |
| 🥉 **[WSL Display](#wsl-setup)** | WSL1/WSL2 | Difícil | Boa |
| 🔧 **[SSH Forwarding](#ssh-setup)** | SSH remoto | Difícil | Variável |
| 💾 **[Salvamento](#alternativas)** | Universal | Fácil | N/A |

---

## 🌐 **Interface Web (Recomendado)** {#interface-web}

### **Por que usar?**
- ✅ **Funciona em qualquer ambiente** (local, WSL, SSH, Docker)
- ✅ **Não depende de X11** ou configurações gráficas
- ✅ **Interface moderna** e responsiva
- ✅ **Acesso remoto** fácil via browser

### **Setup em 30 segundos**
```bash
# 1. Iniciar servidor
python run.py

# 2. Abrir browser
http://localhost:8081

# Para acesso remoto:
python run.py --host 0.0.0.0 --port 8081
# Acesse: http://IP_DO_SERVIDOR:8081
```

### **Funcionalidades Web**
- **📹 Camera Feed:** Stream da câmera original
- **🎨 Depth Map:** Visualização de profundidade MiDaS
- **📊 Metrics:** Dados de navegação em tempo real
- **⚙️ Controls:** Play/pause, seleção de câmera
- **📱 Responsive:** Funciona em desktop, tablet e mobile

### **Configuração Avançada**
```bash
# Configurar porta específica
python run.py --port 8081

# Configurar host para acesso remoto
python run.py --host 0.0.0.0

# Debug mode
python run.py --debug

# Configuração via código
from tofcam.lib import WebServer
server = WebServer(host='0.0.0.0', port=8081)
server.run()
```

---

## 🐧 **Configuração X11/Wayland** {#configuração-x11}

### **Para Linux Nativo (Desktop)**
```bash
# 1. Verificar display atual
echo $DISPLAY
# Saída esperada: :0 ou :1

# 2. Testar X11
xset q
# Se funcionar, está pronto!

# 3. Executar TOFcam
python main.py
```

### **Para Linux via SSH**
```bash
# Conectar com X11 forwarding
ssh -X usuario@servidor

# Ou com compressão (mais rápido)
ssh -XC usuario@servidor

# Testar
python setup_display.py
```

### **Configuração Manual X11**
```bash
# Instalar X11 se necessário
sudo apt update
sudo apt install x11-apps xauth

# Verificar DISPLAY
export DISPLAY=:0.0
xset q

# Se não funcionar, tentar:
export DISPLAY=localhost:10.0
```

### **Para Wayland (Ubuntu 22.04+)**
```bash
# Wayland funciona nativamente
echo $XDG_SESSION_TYPE
# Saída: wayland

# TOFcam funciona diretamente
python main.py
```

---

## 🪟 **WSL/WSL2 Setup** {#wsl-setup}

### **Opção 1: VcXsrv (Recomendado para WSL)**

#### **1. Instalar VcXsrv no Windows**
```bash
# Download: https://sourceforge.net/projects/vcxsrv/
# Instalar XLaunch
```

#### **2. Configurar VcXsrv**
```bash
# Abrir XLaunch com configurações:
# - Multiple windows
# - Display number: 0
# - Start no client
# - DISABLE Access Control ✅ (importante!)
```

#### **3. Configurar WSL**
```bash
# Para WSL1
export DISPLAY=localhost:0.0

# Para WSL2 (IP dinâmico)
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0

# Adicionar ao ~/.bashrc para persistir
echo 'export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0' >> ~/.bashrc
```

#### **4. Testar**
```bash
# Teste básico
xeyes  # Deve abrir janela com olhos

# Teste TOFcam
python setup_display.py
```

### **Opção 2: WSLg (WSL2 com Windows 11)**
```bash
# WSLg já vem configurado no Windows 11
# Verificar se está ativo
echo $WAYLAND_DISPLAY
# Saída esperada: wayland-0

# Executar diretamente
python main.py
```

### **Troubleshooting WSL**
```bash
# Problema: connection refused
# Solução: Verificar Windows Firewall
# Permitir VcXsrv através do firewall

# Problema: DISPLAY vazio  
# Solução: Reconfigurar variável
unset DISPLAY
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
```

---

## 🔗 **SSH/Remote Setup** {#ssh-setup}

### **SSH com X11 Forwarding**
```bash
# Conexão básica
ssh -X usuario@servidor

# Com compressão (recomendado)
ssh -XC usuario@servidor

# Com keep-alive
ssh -XC -o ServerAliveInterval=60 usuario@servidor
```

### **Configuração do Servidor SSH**
```bash
# /etc/ssh/sshd_config
X11Forwarding yes
X11DisplayOffset 10
X11UseLocalhost yes

# Reiniciar SSH
sudo systemctl restart sshd
```

### **Performance Optimization**
```bash
# Conectar com otimizações
ssh -XC -o Compression=yes -o CompressionLevel=6 usuario@servidor

# Para conexões lentas
ssh -X -o Cipher=blowfish usuario@servidor
```

### **Alternativa: VNC/Remote Desktop**
```bash
# Instalar VNC server
sudo apt install tightvncserver

# Iniciar sessão VNC
vncserver :1

# Conectar via VNC client
# Executar TOFcam na sessão VNC
```

---

## 🧪 **Configurador Automático** 

### **Script de Diagnóstico**
```bash
# Executar configurador completo
python setup_display.py

# Menu de opções:
# 1. Setup completo (recomendado)
# 2. Apenas teste básico  
# 3. Apenas teste câmera
# 4. Apenas teste profundidade
# 5. Verificar ambiente
```

### **Testes Automatizados**
```bash
# O script verifica:
✅ Variáveis de ambiente (DISPLAY, XDG_SESSION_TYPE)
✅ Servidor X11 respondendo
✅ OpenCV consegue abrir janelas
✅ Câmera detectada e funcionando
✅ MiDaS carrega e processa
✅ 4 janelas simultâneas funcionam
```

### **Diagnóstico Manual**
```bash
# Verificar ambiente
echo "DISPLAY: $DISPLAY"
echo "Wayland: $WAYLAND_DISPLAY"
echo "Session: $XDG_SESSION_TYPE"

# Teste X11
xset q

# Teste OpenCV
python -c "import cv2; cv2.namedWindow('test'); cv2.waitKey(1000); cv2.destroyAllWindows()"

# Teste câmeras
python -c "from tofcam.lib import discover_cameras; print(discover_cameras())"
```

---

## 🔧 **Troubleshooting Display** {#troubleshooting}

### **Erros Comuns e Soluções**

#### **1. "cannot connect to X server"**
```bash
# Causa: DISPLAY não configurado
# Solução:
export DISPLAY=:0.0
xset q

# Se WSL:
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
```

#### **2. "Permission denied" para X11**
```bash
# Causa: xauth não configurado
# Solução:
xauth generate $DISPLAY . trusted
xauth list
```

#### **3. "OpenCV: Unable to open display"**
```bash
# Causa: OpenCV não consegue acessar display
# Solução 1: Usar web interface
python run.py

# Solução 2: Verificar OpenGL
sudo apt install mesa-utils
glxinfo | grep OpenGL
```

#### **4. Janelas não aparecem**
```bash
# Causa: Window manager issues
# Solução: Verificar se WM está rodando
ps aux | grep -E "(gnome|kde|xfce|i3)"

# Ou usar window manager simples
sudo apt install openbox
openbox &
```

#### **5. "BadWindow" ou "BadDrawable"**
```bash
# Causa: Conflito de versões OpenCV
# Solução: Reinstalar OpenCV
pip uninstall opencv-python
pip install opencv-python==4.8.1.78
```

### **Debugging Avançado**
```bash
# Log detalhado do X11
export DISPLAY=:0.0
xvinfo  # Verificar extensões disponíveis
xlsclients  # Listar clientes X11
xdpyinfo  # Info detalhada do display

# OpenCV debug
export OPENCV_LOG_LEVEL=DEBUG
python main.py
```

---

## 💾 **Alternativas sem Display** {#alternativas}

### **1. Salvamento Automático**
```bash
# Análise com salvamento categorizado
python main_analyzer.py

# Saída organizada:
output_images/
├── camera_original/     # Frames originais
├── depth_maps/         # Mapas MiDaS
├── strategic_navigation/ # Visualização estratégica  
├── reactive_avoidance/   # Visualização reativa
└── complete_analysis/    # Análise combinada
```

### **2. Interface Web (Repetindo)**
```bash
# Solução universal
python run.py
# Acesso: http://localhost:8081
```

### **3. Headless Mode**
```bash
# Análise sem visualização
python -c "
from tofcam.lib import create_camera_manager, create_depth_estimator
cam = create_camera_manager()
depth = create_depth_estimator()
# Processar sem display
"
```

### **4. Terminal Output**
```bash
# Métricas no terminal apenas
python main_analyzer_lib.py
# Escolha: 3 (Análise contínua)
# Output: métricas de navegação detalhadas
```

---

## 📊 **Comparação de Soluções**

| Método | Setup | Performance | Compatibilidade | Recomendado Para |
|--------|-------|-------------|-----------------|------------------|
| **Web Interface** | 🟢 Fácil | 🟢 Excelente | 🟢 Universal | Todos os casos |
| **X11 Local** | 🟢 Fácil | 🟢 Máxima | 🟡 Linux apenas | Desktop Linux |
| **WSL + VcXsrv** | 🟡 Médio | 🟡 Boa | 🟡 WSL apenas | Windows dev |
| **SSH X11** | 🔴 Difícil | 🔴 Variável | 🟡 SSH apenas | Acesso remoto |
| **Salvamento** | 🟢 Fácil | 🟢 Rápida | 🟢 Universal | Análise batch |

---

## ⚡ **Recomendação Final**

### **Para 90% dos Casos: Use Web Interface**
```bash
python run.py
# → http://localhost:8081
```

**Por quê?**
- ✅ Funciona em qualquer ambiente
- ✅ Não requer configuração X11
- ✅ Interface moderna e completa
- ✅ Ideal para apresentações
- ✅ Acesso remoto fácil

### **Para Desenvolvimento Local: X11**
```bash
python main.py  # 4 janelas simultâneas
```

### **Para Análise/Pesquisa: Salvamento**
```bash
python main_analyzer.py  # Persistência automática
```

---

## 📖 **Documentação Relacionada**

- **[Quick Start](quick-start.md)** - Comandos para começar
- **[User Guide](user-guide.md)** - Manual completo
- **[Installation](installation.md)** - Setup do ambiente
- **[Architecture](architecture.md)** - Como o sistema funciona

**[↑ Voltar ao índice da documentação](README.md)**