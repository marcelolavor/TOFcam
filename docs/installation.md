# ⚙️ Installation Guide - TOFcam

**Setup completo do ambiente para desenvolvimento e uso do TOFcam.**

## 📋 **Índice**

1. [Pré-requisitos](#pré-requisitos)
2. [Conda Environment](#conda-environment)
3. [Dependências](#dependências)
4. [Verificação da Instalação](#verificação)
5. [Configuração de GPU](#gpu-setup)
6. [Display Setup](#display-setup)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 **Pré-requisitos**

### Sistema Operacional
- **Linux** (Ubuntu 18.04+, recomendado)
- **WSL2** (Windows Subsystem for Linux)
- **macOS** (limitado, sem suporte GPU)

### Software Base
```bash
# Python 3.8+ (gerenciado via conda)
# Git para clonagem
sudo apt update
sudo apt install git wget curl

# Para desenvolvimento em WSL
sudo apt install x11-apps  # Opcional para display
```

### Hardware
- **Câmera USB** (webcam ou câmera USB)
- **RAM:** 4GB+ (8GB+ recomendado)
- **GPU:** Opcional (CUDA-compatible para aceleração)

---

## 🐍 **Conda Environment**

### 1. Instalar Miniconda (se não instalado)
```bash
# Download e instalação
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Reinicializar shell ou:
source ~/.bashrc
```

### 2. Criar Environment
```bash
# Criar environment específico
conda create -n opencv python=3.8

# Ativar environment
conda activate opencv

# Verificar ativação
which python  # Deve apontar para conda env
```

### 3. Environment sempre ativo (opcional)
```bash
# Adicionar ao ~/.bashrc para auto-ativação
echo "conda activate opencv" >> ~/.bashrc
```

---

## 📦 **Dependências**

### 1. Instalar via requirements.txt
```bash
# No diretório do projeto
cd /path/to/TOFcam
pip install -r requirements.txt
```

### 2. Dependências Principais
```bash
# Core ML/CV
pip install opencv-python torch torchvision timm

# Interface Web
pip install flask flask-socketio

# Análise e processamento
pip install numpy scipy matplotlib

# Opcional: Jupyter para análise
pip install jupyter ipykernel
```

### 3. Verificar Instalação Básica
```bash
python -c "import cv2, torch, numpy; print('✅ Core dependencies OK')"
```

---

## ✅ **Verificação da Instalação** {#verificação}

### 1. Teste Básico da Biblioteca
```bash
# Teste simples da tofcam.lib
python test_library_simple.py

# Saída esperada:
# ✅ tofcam.lib imported successfully
# ✅ Camera manager created
# ✅ MiDaS model loading...
# ✅ Basic test completed
```

### 2. Teste de Câmeras
```bash
# Descobrir câmeras disponíveis
python -c "from tofcam.lib import discover_cameras; print(f'Cameras: {discover_cameras()}')"

# Saída esperada:
# Cameras: [0] ou [0, 2] etc.
```

### 3. Teste de Display
```bash
# Configurador automático
python setup_display.py

# Escolher opção 2 (teste básico)
# Deve abrir janela de teste por 3 segundos
```

### 4. Teste Completo
```bash
# Suite de testes automatizada
python tests/run_tests.py

# Executar demo simples
python demos/basic_usage.py
```

---

## 🚀 **GPU Setup** {#gpu-setup}

### Para NVIDIA GPU (CUDA)
```bash
# Verificar GPU disponível
nvidia-smi

# Instalar PyTorch com CUDA
conda install pytorch torchvision cudatoolkit=11.8 -c pytorch

# Verificar instalação CUDA
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Para AMD/Intel (CPU apenas)
```bash
# PyTorch CPU-only (padrão)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Verificar
python -c "import torch; print(f'Device: {torch.device(\"cuda\" if torch.cuda.is_available() else \"cpu\")}')"
```

### Configuração no TOFcam
```python
# tofcam.lib detecta automaticamente
# Para forçar CPU:
from tofcam.lib import TOFConfig
config = TOFConfig()
config.device = "cpu"  # ou "cuda"
```

---

## 🖥️ **Display Setup** {#display-setup}

### Para Desenvolvimento Local
```bash
# Teste básico de display
python setup_display.py

# Se funcionar, está pronto!
```

### Para WSL2
```bash
# 1. Instalar X Server no Windows (VcXsrv)
# 2. Configurar DISPLAY
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0

# 3. Testar
python setup_display.py
```

### Para SSH/Remote
```bash
# Conexão SSH com X11 forwarding
ssh -X usuario@servidor

# Ou usar interface web (recomendado)
python run.py  # Acesse via browser
```

### Alternativas
- **Interface Web:** `python run.py` (funciona sempre)
- **Salvamento:** Imagens salvas em `output_images/`
- **Headless:** Análise sem display

**📖 Detalhes completos:** [Display Setup Guide](display-setup.md)

---

## 🔧 **Troubleshooting** {#troubleshooting}

### Problemas Comuns

#### 1. ModuleNotFoundError
```bash
# Problema: Módulo não encontrado
# Solução:
conda activate opencv
pip install -r requirements.txt
```

#### 2. Camera Permission Denied
```bash
# Problema: Sem acesso à câmera
# Solução:
sudo usermod -a -G video $USER
# Logout/login necessário
```

#### 3. Display/X11 Errors
```bash
# Problema: Não consegue abrir janelas
# Solução 1: Configurar display
python setup_display.py

# Solução 2: Usar web interface
python run.py
```

#### 4. CUDA Out of Memory
```bash
# Problema: GPU sem memória
# Solução: Forçar CPU
export CUDA_VISIBLE_DEVICES=""
python main.py
```

#### 5. MiDaS Download Issues
```bash
# Problema: Erro ao baixar modelo
# Solução: Download manual
mkdir -p ~/.cache/torch/hub/intel-isl_MiDaS_master/
# Modelo será baixado automaticamente na primeira execução
```

### Verificação de Problemas
```bash
# Checklist rápido
conda activate opencv                    # Environment ativo?
python -c "import tofcam.lib"           # Biblioteca importa?
python -c "import cv2, torch"           # Dependências OK?
python setup_display.py                 # Display funciona?
ls /dev/video*                          # Câmeras detectadas?
```

### Log de Troubleshooting
```bash
# Executar com logs detalhados
export TOFCAM_DEBUG=1
python main.py

# Ou verificar logs do sistema
dmesg | grep video  # Para problemas de câmera
```

---

## 📊 **Verificação Final**

### Checklist de Instalação Completa
- [ ] Conda environment `opencv` criado e ativo
- [ ] Todas dependências instaladas via `requirements.txt`
- [ ] `python test_library_simple.py` executa com sucesso
- [ ] Câmeras detectadas: `discover_cameras()` retorna lista
- [ ] Display funcionando: `python setup_display.py` abre janela
- [ ] Demo básico executa: `python demos/basic_usage.py`
- [ ] Interface web funciona: `python run.py` acessível

### Teste de Integração Final
```bash
# Teste completo do sistema
python main.py

# Deve abrir 4 janelas:
# - TOFCam - Camera Feed
# - TOFCam - Depth Map  
# - TOFCam - Strategic Grid
# - TOFCam - Reactive Grid

# Pressione ESC para sair
```

---

## 🚀 **Próximos Passos**

### Para Usuários
1. **[Quick Start](quick-start.md)** - Comandos essenciais
2. **[User Guide](user-guide.md)** - Manual completo

### Para Desenvolvedores
1. **[API Reference](api-reference.md)** - Documentação da biblioteca
2. **[Architecture](architecture.md)** - Design do sistema

### Em caso de problemas
1. **[Display Setup](display-setup.md)** - Problemas de visualização
2. **[User Guide - Troubleshooting](user-guide.md#troubleshooting)** - Problemas de uso

---

**[↑ Voltar ao índice da documentação](README.md)**