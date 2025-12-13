# 📚 User Guide - TOFcam

**Manual completo do sistema TOFcam com exemplos práticos e casos de uso.**

## 📋 **Índice**

1. [Visão Geral do Sistema](#visão-geral)
2. [Modos de Execução](#modos-de-execução)
3. [Interface Desktop (4 Janelas)](#interface-desktop)
4. [Interface Web](#interface-web)
5. [Análise com Persistência](#análise-com-persistência)
6. [Sistema de Navegação](#sistema-de-navegação)
7. [Configurações Avançadas](#configurações-avançadas)
8. [Interpretação de Resultados](#interpretação-de-resultados)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 **Visão Geral do Sistema** {#visão-geral}

O TOFcam é um sistema de análise de profundidade em tempo real que combina:

### **🧠 Estimação de Profundidade**
- **MiDaS Neural Network** para análise precisa de profundidade
- **Mapas de calor** coloridos para visualização intuitiva
- **Processamento otimizado** CPU/GPU automático

### **🧭 Algoritmos de Navegação**
- **Strategic Navigation:** Planejamento global de rota
- **Reactive Avoidance:** Desvio reativo de obstáculos
- **Hybrid Mode:** Combinação inteligente automática

### **🖥️ Múltiplas Interfaces**
- **Desktop:** 4 janelas especializadas para análise detalhada
- **Web:** Interface moderna acessível via browser
- **API:** Biblioteca `tofcam.lib` para desenvolvimento

---

## 🚀 **Modos de Execução** {#modos-de-execução}

### **1. Sistema Completo (Recomendado)**
```bash
python main.py
```

**O que faz:**
- Abre 4 janelas de visualização simultâneas
- Processamento em tempo real com MiDaS
- Navegação híbrida (strategic + reactive)
- Métricas detalhadas no terminal

**Quando usar:**
- Análise interativa e visual
- Desenvolvimento e debug
- Demonstrações presenciais

### **2. Interface Web**
```bash
python run.py
```

**O que faz:**
- Servidor web em `http://localhost:8081`
- Streaming de vídeo em tempo real
- Interface responsiva e moderna
- Controles interativos

**Quando usar:**
- Apresentações remotas
- Acesso via browser
- Ambientes sem display X11

### **3. Análise com Salvamento**
```bash
python main.py --analysis
```

**O que faz:**
- Visualização em 4 janelas
- Salvamento automático categorizado
- Análise contínua configurável
- Persistência de dados e métricas

**Quando usar:**
- Coleta de dados para pesquisa
- Análise offline posterior
- Documentação de resultados

### **4. Demos e Testes**
```bash
python demos/run_demos.py
```

**O que faz:**
- Menu interativo com todas as demonstrações
- Testes de funcionalidades específicas
- Comparação de algoritmos
- Verificação de configuração

**Quando usar:**
- Primeiros passos no sistema
- Verificação de instalação
- Exploração de funcionalidades

---

## 🖥️ **Interface Desktop (4 Janelas)** {#interface-desktop}

### **Layout das Janelas**
```
┌─────────────────┬─────────────────┐
│  Camera Feed    │   Depth Map     │
│  (Original)     │  (Colorizado)   │
├─────────────────┼─────────────────┤
│ Strategic Grid  │ Reactive Grid   │
│ (Planejamento)  │ (Obstáculos)    │
└─────────────────┴─────────────────┘
```

### **1. Camera Feed (Superior Esquerda)**
**Conteúdo:** Stream original da câmera
```python
# Características
- Resolução: 640x480 (configurável)
- FPS: 30 (padrão, configurável)
- Formato: RGB colorido
```

**Overlays:**
- Frame counter no canto superior
- Timestamp de captura
- Status da câmera

### **2. Depth Map (Superior Direita)** {#midas}
**Conteúdo:** Mapa de profundidade MiDaS colorizado
```python
# Características  
- Colormap: PLASMA (roxo = perto, amarelo = longe)
- Range: 0.1m - 10m+ (estimado)
- Resolução: 256x256 → upscaled para display
```

**Interpretação:**
- 🟣 **Roxo/Azul:** Objetos próximos (0-2m)
- 🟢 **Verde:** Distância média (2-5m)  
- 🟡 **Amarelo:** Objetos distantes (5m+)
- ⚫ **Preto:** Áreas sem dados válidos

### **3. Strategic Grid (Inferior Esquerda)** {#strategic}
**Conteúdo:** Análise estratégica para planejamento de rota
```python
# Grid Configuration
- Tamanho: 8x12 células (configurável)
- Análise: Por coluna (12 colunas)
- Objetivo: Encontrar melhor corredor livre
```

**Visualização:**
- 🟢 **Verde:** Células livres (distância > threshold)
- 🟡 **Amarelo:** Células de alerta  
- 🔴 **Vermelho:** Células com obstáculos
- ➡️ **Seta azul:** Direção recomendada

**Como funciona:**
1. Divide campo de visão em grid 8x12
2. Calcula profundidade média por célula
3. Identifica coluna com mais células livres
4. Converte para ângulo de direção (±40°)

### **4. Reactive Grid (Inferior Direita)** {#reactive}
**Conteúdo:** Análise reativa para desvio de obstáculos
```python
# Reactive Configuration
- Foco: Região central da imagem
- Análise: Célula por célula
- Objetivo: Desvio imediato de obstáculos
```

**Visualização:**
- 🟢 **Verde:** Espaço livre para movimento
- 🟡 **Amarelo:** Áreas de atenção
- 🔴 **Vermelho:** Obstáculos diretos
- ⚠️ **Emergency:** Indicator de frenagem

**Como funciona:**
1. Analisa região central (zona crítica)
2. Detecta obstáculos próximos (<1m)
3. Calcula correção imediata de direção
4. Ativa emergency brake se necessário

### **Controles de Teclado**
```bash
ESC     # Sair do sistema
SPACE   # Pausar/retomar processamento  
s       # Screenshot das 4 janelas
r       # Reset das métricas
c       # Trocar câmera (se múltiplas)
```

---

## 🌐 **Interface Web** {#interface-web}

### **Acesso**
```bash
# Iniciar servidor
python run.py

# Acessar no browser
http://localhost:8081
```

### **Funcionalidades Web**
- **📹 Video Stream:** Câmera original em tempo real
- **🎨 Depth Visualization:** Mapa de profundidade colorizado
- **📊 Navigation Metrics:** Dados de navegação atualizados
- **⚙️ Controls:** Play/pause, câmera selection, configurações

### **Interface Responsiva**
```html
<!-- Layout adaptável -->
Desktop: Side-by-side layout
Tablet:  Stacked layout
Mobile:  Single stream focus
```

### **API Endpoints**
```bash
GET  /                    # Interface principal
GET  /video_feed          # Stream de vídeo
GET  /depth_feed          # Stream de profundidade  
POST /api/config          # Alterar configurações
GET  /api/metrics         # Dados de navegação atual
```

---

## 💾 **Análise com Persistência** {#análise-com-persistência}

### **Estrutura de Salvamento**
```bash
output_images/
├── camera_original/      # Frames originais da câmera
├── depth_maps/          # Mapas de profundidade
├── strategic_navigation/ # Visualização estratégica
├── reactive_avoidance/   # Visualização reativa
└── complete_analysis/    # Análise combinada
```

### **Sessões de Análise**
```bash
# Exemplo de sessão
python main.py --analysis

# Menu de opções:
# 1. Sessão interativa (controle manual)
# 2. Análise único frame 
# 3. Análise contínua (N frames automático)
```

### **Dados Salvos por Frame**
```json
{
  "timestamp": 1639337472.123,
  "frame_id": 123456789,
  "camera_index": 0,
  "navigation_mode": "hybrid",
  "strategic": {
    "target_yaw_delta": 0.234,
    "confidence": 0.892,
    "min_distance_ahead": 3.45,
    "recommended_speed": 0.8
  },
  "reactive": {
    "yaw_delta": -0.123,
    "forward_scale": 0.9,
    "emergency_brake": false,
    "urgency": 0.3
  }
}
```

---

## 🧭 **Sistema de Navegação** {#sistema-de-navegação}

### **Strategic Navigation (Navegação Estratégica)**

**Objetivo:** Planejamento de rota baseado na análise global do ambiente.

**Processo:**
1. **Grid Analysis:** Divide imagem em grid 8x12
2. **Column Scoring:** Calcula score de navegabilidade por coluna
3. **Best Path:** Identifica melhor corredor livre
4. **Angle Conversion:** Converte para ângulo de direção

**Métricas:**
```python
strategic_result = {
    'target_yaw_delta': 0.234,     # Ângulo target em radianos
    'confidence': 0.892,           # Confiança na decisão (0-1)
    'min_distance_ahead': 3.45,    # Distância mínima à frente
    'recommended_speed': 0.8       # Velocidade recomendada (0-1)
}
```

**Interpretação:**
- **target_yaw_delta:** Direção recomendada em radianos (±0.7 = ±40°)
- **confidence:** Quão certa está a decisão (>0.7 = boa)
- **min_distance_ahead:** Distância até obstáculo à frente
- **recommended_speed:** Velocidade segura (1.0 = máxima)

### **Reactive Avoidance (Evitação Reativa)**

**Objetivo:** Desvio imediato de obstáculos próximos.

**Processo:**
1. **Critical Zone:** Foca na região central da imagem
2. **Obstacle Detection:** Identifica obstáculos próximos
3. **Immediate Correction:** Calcula correção de direção
4. **Emergency Response:** Ativa freio se necessário

**Métricas:**
```python
reactive_result = {
    'yaw_delta': -0.123,          # Correção imediata de direção
    'forward_scale': 0.9,         # Fator de velocidade (0-1)
    'emergency_brake': False,     # Freio de emergência
    'urgency': 0.3               # Nível de urgência (0-1)
}
```

**Interpretação:**
- **yaw_delta:** Correção imediata (-1 a +1)
- **forward_scale:** Redução de velocidade por segurança
- **emergency_brake:** True = parar imediatamente
- **urgency:** Nível de perigo (>0.8 = crítico)

### **Hybrid Mode (Modo Híbrido)** {#hybrid}

**Como funciona:**
1. **Strategic** fornece direção geral
2. **Reactive** aplica correções de segurança
3. **Hybrid** combina ambos inteligentemente

**Lógica de Combinação:**
```python
if reactive.emergency_brake:
    # Prioridade total para reactive
    final_command = reactive_only()
elif reactive.urgency > 0.7:
    # Reactive dominante, strategic como referência
    final_command = weighted_reactive(0.8) + weighted_strategic(0.2)
else:
    # Strategic dominante, reactive como correção
    final_command = weighted_strategic(0.7) + weighted_reactive(0.3)
```

---

## ⚙️ **Configurações Avançadas** {#configurações-avançadas}

### **Configuração de Câmera**
```python
from tofcam.lib import TOFConfig, CameraConfig

config = TOFConfig()
config.camera.width = 1280        # Resolução horizontal
config.camera.height = 720        # Resolução vertical  
config.camera.fps = 30            # Frames por segundo
config.camera.use_test_image = False  # Usar imagem sintética
```

### **Configuração MiDaS**
```python
config.midas.model_type = "MiDaS_small"  # ou "DPT_Large"
config.midas.device = "cuda"             # ou "cpu"  
config.midas.optimize = True             # Otimizações de velocidade
```

### **Configuração de Navegação**
```python
config.navigation.grid_size = (8, 12)    # Linhas x Colunas
config.navigation.safe_distance = 1.5    # Distância segura (metros)
config.navigation.strategic_weight = 0.7 # Peso strategic vs reactive
config.navigation.emergency_threshold = 0.5  # Threshold para emergency brake
```

### **Configuração de Visualização**
```python
config.visualization.show_grids = True       # Mostrar grids
config.visualization.show_metrics = True     # Mostrar métricas
config.visualization.colormap = "plasma"     # Colormap para depth
config.visualization.overlay_alpha = 0.6     # Transparência dos overlays
```

---

## 📊 **Interpretação de Resultados** {#interpretação-de-resultados}

### **Métricas de Qualidade**

#### **Strategic Confidence**
- **0.9 - 1.0:** Excelente - Caminho muito claro
- **0.7 - 0.9:** Boa - Caminho identificado com segurança
- **0.5 - 0.7:** Regular - Caminho incerto
- **0.0 - 0.5:** Ruim - Ambiente muito obstruído

#### **Reactive Urgency**
- **0.8 - 1.0:** Crítico - Obstáculo iminente
- **0.5 - 0.8:** Alto - Atenção necessária
- **0.2 - 0.5:** Médio - Situação sob controle
- **0.0 - 0.2:** Baixo - Ambiente livre

### **Padrões de Navegação**

#### **Navegação Livre**
```
Strategic: confidence > 0.8, target_yaw ~= 0
Reactive:  urgency < 0.3, emergency_brake = false
Hybrid:    Movimento suave e direto
```

#### **Corredor Estreito**
```
Strategic: confidence 0.5-0.7, target_yaw oscilante
Reactive:  urgency 0.3-0.6, forward_scale reduzido
Hybrid:    Movimento cuidadoso com correções
```

#### **Ambiente Obstruído**
```
Strategic: confidence < 0.5, target_yaw erático
Reactive:  urgency > 0.7, emergency_brake frequente
Hybrid:    Movimento lento ou parado
```

### **Debugging Visual**

#### **Depth Map Quality**
- **Definição clara:** MiDaS funcionando bem
- **Bordas borradas:** Iluminação inadequada
- **Ruído excessivo:** Câmera de baixa qualidade
- **Áreas pretas:** Superfícies reflexivas/transparentes

#### **Grid Consistency**
- **Grids alinhados:** Calibração correta
- **Grids divergentes:** Problema de profundidade
- **Células piscando:** Threshold inadequado

---

## 🔧 **Troubleshooting** {#troubleshooting}

### **Problemas Comuns**

#### **1. Nenhuma Câmera Detectada**
```bash
# Diagnóstico
python -c "from tofcam.lib import discover_cameras; print(discover_cameras())"

# Soluções
sudo usermod -a -G video $USER  # Adicionar permissões
ls /dev/video*                  # Verificar devices
```

#### **2. Erro de Display/X11**
```bash
# Problema: Can't open display
# Solução 1: Configurar display
python setup_display.py

# Solução 2: Usar web interface
python run.py
```

#### **3. MiDaS Muito Lento**
```bash
# Problema: FPS muito baixo
# Solução 1: Usar modelo menor
export MIDAS_MODEL=MiDaS_small

# Solução 2: Forçar CPU
export CUDA_VISIBLE_DEVICES=""
```

#### **4. Câmera com Qualidade Ruim**
```python
# Ajustar configurações
config = TOFConfig()
config.camera.width = 640      # Reduzir resolução
config.camera.height = 480
config.midas.optimize = True   # Ativar otimizações
```

#### **5. Navegação Errática**
```python
# Ajustar sensibilidade
config.navigation.safe_distance = 2.0     # Aumentar distância
config.navigation.emergency_threshold = 0.3  # Reduzir threshold
```

### **Logs e Debugging**
```bash
# Ativar logs detalhados
export TOFCAM_DEBUG=1
python main.py

# Logs específicos
export TOFCAM_LOG_LEVEL=DEBUG
export TOFCAM_LOG_FILE=tofcam.log
```

### **Performance Monitoring**
```python
# Métricas em tempo real
import time

start = time.time()
analysis = analyze_frame()
processing_time = time.time() - start

print(f"FPS: {1.0/processing_time:.1f}")
print(f"Processing: {processing_time*1000:.1f}ms")
```

---

## 📚 **Próximos Passos**

### **Para Usuários Iniciantes**
1. **[Quick Start](quick-start.md)** - Comandos essenciais
2. **[Display Setup](display-setup.md)** - Se tiver problemas visuais
3. **Prática:** Execute `python demos/run_demos.py`

### **Para Usuários Avançados**
1. **[API Reference](api-reference.md)** - Integração com a biblioteca
2. **[Architecture](architecture.md)** - Como o sistema funciona
3. **Experimentação:** Modifique configurações e compare resultados

### **Para Desenvolvimento**
1. **[Architecture](architecture.md)** - Design do sistema
2. **[API Reference](api-reference.md)** - Documentação técnica
3. **Contribuição:** Implemente novos algoritmos ou melhorias

---

**[↑ Voltar ao índice da documentação](README.md)**