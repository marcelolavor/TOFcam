# TOFcam - Guia de Uso

Este guia demonstra como usar o sistema TOFcam para análise de profundidade e navegação em tempo real.

## 🚀 Início Rápido

### 1. Ativação do Ambiente
```bash
# Ativar ambiente conda
conda activate opencv

# Verificar se está no diretório correto
cd /home/lavor/projects/TOFcam
```

### 2. Executar Demonstrações
```bash
# Modo interativo (recomendado para iniciantes)
python demos/run_demos.py

# Execução direta de demos específicos
python demos/basic_usage.py
python demos/algorithm_comparison.py
python demos/library/demo_lib.py
python demos/camera_selection/camera_selector.py
```

## 📋 Modos de Uso

### 🎬 Modo Demonstrações (Recomendado)

O **gerenciador interativo** é a forma mais fácil de explorar todas as funcionalidades:

```bash
python demos/run_demos.py
```

**Menu disponível:**
```
📁 Biblioteca Centralizada:
  1. Demo configurações biblioteca
  
📁 Algoritmos & Comparação:
  2. Uso básico - Biblioteca
  3. Comparação algoritmos
  
📁 Interface & Cameras:
  4. Seleção de câmeras
```

### 🌐 Modo Web Interface

Para análise via browser com interface web:

```bash
# Web viewer usando biblioteca centralizada
python web_viewer_lib.py

# Web viewer original
python web_viewer.py
```

Acesse: `http://localhost:8080`

### 💾 Modo Análise e Persistência

Para processar frames e salvar resultados:

```bash
# Usando biblioteca centralizada (recomendado)
python main_analyzer_lib.py

# Analisador original 
python main_analyzer.py
```

### 🧪 Modo Testes

Para validação e desenvolvimento:

```bash
# Gerenciador interativo de testes
python tests/run_tests.py

# Testes específicos
python tests/test_camera.py
python tests/test_algorithms.py
python tests/test_library.py
```

## 🔧 Configurações Avançadas

### Configuração da Biblioteca Centralizada

```python
from analyzer_lib import TOFAnalyzer, AnalysisConfig

# Configuração para Web (Base64, sem persistir)
config_web = AnalysisConfig(
    save_frames=False,
    web_format=True,
    output_dir="output_images"
)

# Configuração para Persistência (salvar arquivos)
config_persist = AnalysisConfig(
    save_frames=True,
    web_format=False,
    output_dir="demo_output"
)

# Configuração Simples (análise básica)
config_simple = AnalysisConfig(
    use_sophisticated_analysis=False,
    save_frames=False
)

# Inicializar analisador
analyzer = TOFAnalyzer(config=config_web)
```

### Configuração de Câmeras

```python
from camera import CameraSource

# Câmera específica
camera = CameraSource(index=0)  # ou index=2
camera.open()

# Modo teste (sem câmera física)
camera_test = CameraSource(use_test_image=True)
camera_test.open()
```

### Configuração de Algoritmos

```python
from mapping import StrategicNavigationAlgorithm, ReactiveAvoidanceAlgorithm

# Strategic (planejamento)
strategic = StrategicNavigationAlgorithm()
strategic.sensitivity = 0.8  # Mais sensível

# Reactive (evitação)
reactive = ReactiveAvoidanceAlgorithm()
reactive.threshold = 1.5  # Distância de ativação
```

## 📊 Interpretação dos Resultados

### Direções de Navegação
- **Yaw > +0.2°** → ➡️ Virar à direita
- **Yaw < -0.2°** → ⬅️ Virar à esquerda  
- **Yaw ≈ 0.0°** → ⬆️ Seguir em frente

### Mapa de Profundidade (Cores)
- **🔴 Vermelho** → Obstáculos próximos (< 1m)
- **🟡 Amarelo** → Distância média (1-3m)
- **🔵 Azul** → Objetos distantes (> 3m)

### Algoritmos
- **Strategic** → Planejamento baseado em zonas
- **Reactive** → Evitação imediata de obstáculos

## ⌨️ Controles Interativos

### Demos com OpenCV
- **`q`** → Sair
- **`SPACE`** → Pausar/Continuar
- **`s`** → Salvar frame atual (quando disponível)

### Interface Web
- **Câmera** → Seleção de câmera ativa
- **Start/Stop** → Controlar análise
- **Download** → Baixar imagens de análise

## 📁 Estrutura de Saídas

### Demos
```
demos/outputs/
├── cam0_YYYYMMDD_HHMMSS/
│   ├── original.jpg      # Frame original
│   ├── depth.jpg         # Mapa de profundidade
│   ├── combined.jpg      # Visualização combinada
│   └── analysis.json     # Dados da análise
```

### Web Interface
```
web_output/
├── frame_XXXXXXX.jpg     # Frame original
├── depth_XXXXXXX.jpg     # Mapa de profundidade
└── combined_XXXXXXX.jpg  # Análise combinada
```

### Análise Principal
```
output_images/
├── cam0_YYYYMMDD_HHMMSS/
│   ├── frames/           # Frames originais
│   ├── depth_maps/       # Mapas de profundidade
│   ├── visualizations/   # Visualizações
│   └── metadata.json     # Metadados da sessão
```

## 🛠️ Solução de Problemas

### Câmera não detectada
```bash
# Verificar câmeras disponíveis
python demos/camera_selection/camera_selector.py

# Usar modo teste
# Modifique o código para: use_test_image=True
```

### Erro de dependências
```bash
# Reinstalar dependências
pip install -r requirements.txt

# Verificar ambiente
conda activate opencv
```

### Performance lenta
```bash
# Verificar se GPU está disponível
python -c "import torch; print('CUDA:', torch.cuda.is_available())"

# Usar análise simplificada
# Configure: use_sophisticated_analysis=False
```

### Porta em uso (Web)
```bash
# Matar processos existentes
pkill -f web_viewer
pkill -f web_viewer_lib

# Verificar portas
netstat -tlnp | grep 8080
```

## 📖 Exemplos de Uso

### 1. Análise Básica
```python
from analyzer_lib import TOFAnalyzer, AnalysisConfig

config = AnalysisConfig(save_frames=False)
analyzer = TOFAnalyzer(config=config)

# Processar um frame
frame = analyzer.camera_manager.read()
result = analyzer.process_frame(frame)

print(f"Strategic: {result.strategic_result['yaw_delta']:.3f}°")
print(f"Reactive: {result.reactive_result['yaw_delta']:.3f}°")

analyzer.cleanup()
```

### 2. Comparação de Algoritmos
```python
from analyzer_lib import TOFAnalyzer, AnalysisConfig
from mapping import StrategicNavigationAlgorithm, ReactiveAvoidanceAlgorithm

# Biblioteca centralizada
config = AnalysisConfig(save_frames=False)
analyzer = TOFAnalyzer(config=config)

# Algoritmos individuais
strategic = StrategicNavigationAlgorithm()
reactive = ReactiveAvoidanceAlgorithm()

# Comparar resultados
frame = analyzer.camera_manager.read()
lib_result = analyzer.process_frame(frame)
strategic_result = strategic.process(lib_result.depth_map)
reactive_result = reactive.process(lib_result.depth_map)

print(f"Biblioteca Strategic: {lib_result.strategic_result['yaw_delta']:.3f}°")
print(f"Individual Strategic: {strategic_result['yaw_delta']:.3f}°")
print(f"Individual Reactive: {reactive_result['yaw_delta']:.3f}°")

analyzer.cleanup()
```

### 3. Salvamento de Dados
```python
from analyzer_lib import TOFAnalyzer, AnalysisConfig

# Configurar para salvar
config = AnalysisConfig(
    save_frames=True,
    output_dir="minha_analise"
)
analyzer = TOFAnalyzer(config=config)

# Processar e salvar automaticamente
frame = analyzer.camera_manager.read()
result = analyzer.process_frame(frame, camera_id=0)

# Arquivos salvos em: minha_analise/cam0_TIMESTAMP/
analyzer.cleanup()
```

## 🎯 Casos de Uso Práticos

### 🤖 Robótica Móvel
Use o modo análise em tempo real para navegação autônoma:
```bash
python demos/basic_usage.py
```

### 📊 Pesquisa e Desenvolvimento
Use comparação de algoritmos para validar melhorias:
```bash
python demos/algorithm_comparison.py
```

### 🌐 Demonstrações e Apresentações
Use interface web para demos interativas:
```bash
python web_viewer_lib.py
```

### 💾 Coleta de Dados
Use modo persistência para criar datasets:
```bash
python main_analyzer_lib.py
```

### 🧪 Teste de Hardware
Use seletor de câmeras para validar setup:
```bash
python demos/camera_selection/camera_selector.py
```

---

💡 **Dica**: Comece sempre com `python demos/run_demos.py` para explorar todas as funcionalidades de forma interativa!