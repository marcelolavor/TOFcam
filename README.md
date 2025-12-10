# TOFcam

Sistema de análise de profundidade e navegação em tempo real usando câmeras RGB e estimação de profundidade com MiDaS.

## 🚀 Início Rápido

```bash
# 1. Ativar ambiente
conda activate opencv

# 2. Executar demonstrações interativas
python demos/run_demos.py

# 3. Interface web (alternativa)
python web_viewer_lib.py
```

📖 **Guia Completo**: [docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md) | **Início Rápido**: [docs/HOW_TO_USE.md](docs/HOW_TO_USE.md) | **📚 Documentação**: [docs/](docs/)

## ⚡ Funcionalidades

- ✅ **Estimação de profundidade** usando MiDaS neural network
- ✅ **Algoritmos de navegação** (Strategic Planning + Reactive Avoidance)  
- ✅ **Interface web** para análise em tempo real
- ✅ **Sistema modular** com biblioteca centralizada
- ✅ **Suporte multi-câmera** com detecção automática
- ✅ **Análise sofisticada** com ZoneMappers configuráveis

## 🎯 Sistema de Navegação Dual

O TOFcam implementa dois algoritmos complementares de análise e navegação:

### 📊 **Strategic Navigation (Navegação Estratégica)**

**Objetivo:** Planejamento de rota de longo prazo baseado na análise global do ambiente.

**Como Funciona:**
- Analisa **todo o campo de visão** da câmera
- Calcula profundidade média de **cada coluna** do grid
- Encontra o **melhor corredor** livre considerando:
  - Quantidade de células livres
  - Distância média dos obstáculos
  - Caminho com maior "score" de navegabilidade
- Converte a coluna escolhida em **ângulo de direção** (`target_yaw_delta`)

**Características:**
- **Visão ampla:** Considera panorama completo
- **Planejamento:** Busca o melhor caminho geral
- **Estabilidade:** Mudanças graduais de direção
- **Range:** Tipicamente ±40° (-0.7 a +0.7 rad)

**Saída Típica:**
```
Strategic: +0.698° → Recomenda virar 40° para ESQUERDA
Strategic: -0.563° → Recomenda virar 32° para DIREITA
```

---

### ⚡ **Reactive Avoidance (Evasão Reativa)**

**Objetivo:** Resposta imediata a obstáculos próximos na zona crítica frontal.

**Como Funciona:**
- Monitora apenas as **primeiras 4 fileiras** do grid (zona crítica)
- Compara obstáculos **esquerda vs direita** na área imediata
- Calcula score baseado em células livres vs bloqueadas
- Gera comando de **evasão instantânea** (`yaw_delta`)

**Características:**
- **Foco frontal:** Apenas zona de perigo imediato
- **Resposta rápida:** Decisões binárias de evasão
- **Emergência:** Prioriza segurança sobre otimização
- **Range:** Fixo ±34.4° (-0.6/+0.6 rad) ou neutro (0°)

**Saída Típica:**
```
Reactive: +0.600° → EVASÃO para ESQUERDA (obstáculo à direita)
Reactive: -0.600° → EVASÃO para DIREITA (obstáculo à esquerda)
Reactive: 0.000° → SEM OBSTÁCULOS imediatos
```

---

### 🔄 **Interação entre os Sistemas**

**Cenários Comuns:**

1. **🟢 Acordo (Harmonia):**
   ```
   Strategic: +0.4°, Reactive: +0.6° → Ambos recomendam ESQUERDA
   ```

2. **🟡 Conflito (Cenário Complexo):**
   ```
   Strategic: +0.7°, Reactive: -0.6° → Strategic ← vs Reactive →
   ```
   *Interpretação: Melhor rota geral à esquerda, mas obstáculo imediato à direita*

3. **🔵 Strategic Ativo, Reactive Neutro:**
   ```
   Strategic: -0.5°, Reactive: 0.0° → Planejamento sem emergência
   ```

**Controle de Velocidade:**
- `forward_scale = 0.00` → **PARADA** (emergência detectada)
- `forward_scale = 0.30` → **REDUÇÃO** (atenção necessária)  
- `forward_scale = 1.00` → **NORMAL** (caminho livre)

---

### 🎨 **Visualização**

**Cores do Mapa de Profundidade:**
- 🔴 **Vermelho:** Obstáculos próximos (0-2m)
- 🟡 **Amarelo:** Distância intermediária (2-4m)
- 🟢 **Verde:** Zona de transição (4-6m)
- 🔵 **Azul:** Objetos distantes/seguros (>6m)

**Setas Direcionais:**
- 🟢 **Verde:** Direção Strategic Navigation
- 🟠 **Laranja:** Direção Reactive Avoidance  
- **Tamanho/Posição:** Centro inferior da imagem
- **Ângulo:** Representa exatamente o valor calculado

---

## 📁 **Estrutura do Projeto**

```
TOFcam/
├── 🔧 Core Modules
│   ├── main_analyzer.py      # Sistema principal de análise
│   ├── camera.py            # Gerenciamento de câmeras  
│   ├── midas.py             # Estimação de profundidade MiDaS
│   ├── mapping.py           # Algoritmos Strategic/Reactive
│   ├── view.py              # Visualização e rendering
│   └── tofcam_types.py       # Tipos de dados
├── 🧪 tests/
│   ├── run_tests.py         # Menu principal de testes
│   ├── test_arrows.py       # Validação direções das setas
│   ├── test_algorithms.py   # Comparação de algoritmos
│   └── test_cameras.py      # Teste de hardware
├── 🚀 examples/
│   ├── basic_usage.py       # Exemplo básico de uso
│   └── algorithm_comparison.py # Comparação visual
└── 📚 Documentation
    ├── README.md            # Este arquivo
    ├── requirements.txt     # Dependências
    └── LICENSE              # Licença MIT
```

---

### 📂 **Estrutura de Saída**

```
output_images/
├── 📁 camera_original/     - Imagens brutas da câmera
├── 📁 depth_maps/          - Mapas de profundidade coloridos  
├── 📁 strategic_navigation/ - Grid + seta verde (Strategic)
├── 📁 reactive_avoidance/   - Grid + seta laranja (Reactive)
└── 📁 complete_analysis/    - Análise combinada com dados
```

**Convenção de Nomes:**
```
frame_XXXX_YYYYMMDD_HHMMSS.jpg
```

---

### 🚀 **Como Usar o Sistema Organizado**

#### 📦 **Instalação e Configuração**
```bash
# Clonar o repositório
git clone https://github.com/marcelolavor/TOFcam.git
cd TOFcam

# Criar ambiente conda
conda create -n opencv python=3.12 -y
conda activate opencv

# Instalar dependências
pip install -r requirements.txt
```

#### 🎮 **Executar Sistema Principal**
```bash
# Modo demonstrações interativas (recomendado)
python demos/run_demos.py

# Interface web para análise
python web_viewer_lib.py

# Análise com coleta de dados
python main_analyzer_lib.py
```

#### 🧪 **Executar Testes**
```bash
# Menu interativo de testes
python tests/run_tests.py

# Testes específicos
python tests/test_camera.py        # Teste de câmeras
python tests/test_algorithms.py    # Teste de algoritmos  
python tests/test_library.py       # Teste biblioteca centralizada
```

#### 📚 **Exemplos Práticos**
```bash
# Uso básico com biblioteca centralizada
python demos/basic_usage.py

# Comparação visual de algoritmos
python demos/algorithm_comparison.py

# Configurações da biblioteca
python demos/library/demo_lib.py
```

**Interpretação dos Logs:**
```
📊 Frame 42: Strategic=+0.698°, Reactive=-0.600°, Scale=0.30
```
- **Strategic:** Planeja ir 40° à esquerda
- **Reactive:** Detecta obstáculo, evade 34° à direita  
- **Scale:** Reduz velocidade para 30% (cautela)
- **Conflito:** Situação complexa requiring decisão híbrida

📚 **Documentação Organizada**: [docs/](docs/) | **Demos**: [demos/](demos/) | **Testes**: [tests/](tests/)
