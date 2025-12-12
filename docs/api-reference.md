# 📖 API Reference - TOFcam

**Documentação técnica completa da biblioteca tofcam.lib para desenvolvedores.**

## 📋 **Índice**

1. [Visão Geral da API](#visão-geral)
2. [Factory Functions](#factory-functions)
3. [Módulo Camera](#módulo-camera)
4. [Módulo Depth](#módulo-depth)
5. [Módulo Navigation](#módulo-navigation)
6. [Módulo Visualization](#módulo-visualization)
7. [Módulo Web](#módulo-web)
8. [Configurações](#configurações)
9. [Tipos de Dados](#tipos-de-dados)
10. [Exemplos de Integração](#exemplos)

---

## 🎯 **Visão Geral da API** {#visão-geral}

### **Design Philosophy**
A `tofcam.lib` foi projetada com foco em:
- **Simplicidade:** Factory functions para uso rápido
- **Flexibilidade:** Classes completas para customização
- **Consistência:** Padrões uniformes em toda a API
- **Performance:** Otimizações automáticas

### **Import Patterns**
```python
# Recommended: Factory functions
from tofcam.lib import (
    create_camera_manager,
    create_depth_estimator,
    create_navigator,
    create_render_pipeline,
    TOFConfig
)

# Advanced: Direct imports
from tofcam.lib.camera import CameraManager, CameraConfig
from tofcam.lib.depth import MidasDepthEstimator
from tofcam.lib.navigation import HybridNavigator, NavigationConfig
```

---

## 🏭 **Factory Functions** {#factory-functions}

### **create_camera_manager()**
```python
def create_camera_manager(config: TOFConfig = None) -> CameraManager
```

**Descrição:** Cria gerenciador de câmeras com configuração automática.

**Parâmetros:**
- `config` (optional): Configuração personalizada

**Retorna:** Instância de `CameraManager`

**Exemplo:**
```python
from tofcam.lib import create_camera_manager

# Uso básico
camera_manager = create_camera_manager()

# Com configuração
config = TOFConfig()
config.camera.width = 1280
camera_manager = create_camera_manager(config)
```

### **create_depth_estimator()**
```python
def create_depth_estimator(config: TOFConfig = None) -> MidasDepthEstimator
```

**Descrição:** Cria estimador de profundidade MiDaS otimizado.

**Parâmetros:**
- `config` (optional): Configuração do MiDaS

**Retorna:** Instância de `MidasDepthEstimator`

**Exemplo:**
```python
# Básico (CPU/GPU automático)
depth_estimator = create_depth_estimator()

# Forçar CPU
config = TOFConfig()
config.midas.device = "cpu"
depth_estimator = create_depth_estimator(config)
```

### **create_navigator()**
```python
def create_navigator(navigation_config: NavigationConfig = None) -> HybridNavigator
```

**Descrição:** Cria navegador híbrido (strategic + reactive).

**Parâmetros:**
- `navigation_config` (optional): Configuração de navegação

**Retorna:** Instância de `HybridNavigator`

**Exemplo:**
```python
# Padrão
navigator = create_navigator()

# Customizado
nav_config = NavigationConfig()
nav_config.grid_size = (10, 16)
nav_config.safe_distance = 2.0
navigator = create_navigator(nav_config)
```

### **create_render_pipeline()**
```python
def create_render_pipeline(config: TOFConfig = None) -> RenderPipeline
```

**Descrição:** Cria pipeline de renderização otimizado.

**Exemplo:**
```python
render_pipeline = create_render_pipeline()

# Renderizar depth map colorizado
depth_colored = render_pipeline.render_depth_colored(depth_map)
```

### **discover_cameras()**
```python
def discover_cameras() -> List[int]
```

**Descrição:** Descobre câmeras USB disponíveis no sistema.

**Retorna:** Lista de índices de câmeras funcionais

**Exemplo:**
```python
from tofcam.lib import discover_cameras

cameras = discover_cameras()
print(f"Câmeras encontradas: {cameras}")  # [0, 2]
```

---

## 📹 **Módulo Camera** {#módulo-camera}

### **CameraManager**

#### **Construtor**
```python
class CameraManager:
    def __init__(self)
```

#### **Métodos Principais**

##### **add_camera()**
```python
def add_camera(self, config: CameraConfig) -> bool
```

**Descrição:** Adiciona e configura nova câmera.

**Parâmetros:**
- `config`: Configuração da câmera

**Retorna:** `True` se sucesso, `False` se falha

**Exemplo:**
```python
camera_config = CameraConfig(
    index=0,
    width=640,
    height=480,
    fps=30
)
success = camera_manager.add_camera(camera_config)
```

##### **read_frame()**
```python
def read_frame(self, camera_id: int = None) -> Optional[np.ndarray]
```

**Descrição:** Captura frame da câmera especificada.

**Parâmetros:**
- `camera_id` (optional): ID da câmera (None = primeira disponível)

**Retorna:** Frame RGB ou `None` se falha

**Exemplo:**
```python
frame = camera_manager.read_frame()
if frame is not None:
    print(f"Frame shape: {frame.shape}")  # (480, 640, 3)
```

##### **close_all()**
```python
def close_all(self) -> None
```

**Descrição:** Fecha todas as câmeras abertas.

### **CameraConfig**
```python
@dataclass
class CameraConfig:
    index: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30
    use_test_image: bool = False
```

**Campos:**
- `index`: Índice da câmera USB
- `width/height`: Resolução desejada
- `fps`: Frames por segundo
- `use_test_image`: Usar imagem sintética para testes

---

## 🧠 **Módulo Depth** {#módulo-depth}

### **MidasDepthEstimator**

#### **estimate_depth()**
```python
def estimate_depth(self, image: np.ndarray) -> np.ndarray
```

**Descrição:** Estima profundidade usando MiDaS neural network.

**Parâmetros:**
- `image`: Imagem RGB (H, W, 3)

**Retorna:** Mapa de profundidade normalizado (H, W)

**Exemplo:**
```python
# Capturar e processar
frame = camera_manager.read_frame()
depth_map = depth_estimator.estimate_depth(frame)

# depth_map shape: (480, 640)
# Valores: 0.0 (próximo) a 1.0 (distante)
```

#### **preprocess_image()**
```python
def preprocess_image(self, image: np.ndarray) -> torch.Tensor
```

**Descrição:** Pré-processamento para entrada no MiDaS.

#### **postprocess_depth()**
```python
def postprocess_depth(self, depth: torch.Tensor) -> np.ndarray
```

**Descrição:** Pós-processamento da saída do MiDaS.

### **Configuração MiDaS**
```python
@dataclass
class MidasConfig:
    model_type: str = "MiDaS_small"  # ou "DPT_Large"
    device: str = "auto"             # "cpu", "cuda", "auto"
    optimize: bool = True            # Otimizações de velocidade
    input_size: Tuple[int, int] = (256, 256)
```

---

## 🧭 **Módulo Navigation** {#módulo-navigation}

### **HybridNavigator**

#### **navigate()**
```python
def navigate(self, depth_map: np.ndarray, mode: NavigationMode = NavigationMode.HYBRID) -> NavigationResult
```

**Descrição:** Executa navegação híbrida em mapa de profundidade.

**Parâmetros:**
- `depth_map`: Mapa de profundidade normalizado
- `mode`: Modo de navegação (STRATEGIC, REACTIVE, HYBRID)

**Retorna:** Resultado completo da navegação

**Exemplo:**
```python
# Navegação híbrida (recomendado)
nav_result = navigator.navigate(depth_map, NavigationMode.HYBRID)

# Acessar resultados
strategic = nav_result.strategic
reactive = nav_result.reactive

print(f"Strategic yaw: {np.rad2deg(strategic.target_yaw_delta):.1f}°")
print(f"Reactive urgency: {reactive.urgency:.3f}")
```

### **ZoneMapper**

#### **create_strategic_grid()**
```python
def create_strategic_grid(self, depth_map: np.ndarray) -> ZoneGrid
```

**Descrição:** Cria grid estratégico para planejamento.

#### **create_reactive_grid()**
```python
def create_reactive_grid(self, depth_map: np.ndarray) -> ZoneGrid
```

**Descrição:** Cria grid reativo para desvio de obstáculos.

### **NavigationResult**
```python
@dataclass
class NavigationResult:
    mode: NavigationMode
    strategic: Optional[StrategicPlan] = None
    reactive: Optional[ReactiveCommand] = None
    timestamp: float = field(default_factory=time.time)
```

### **StrategicPlan**
```python
@dataclass
class StrategicPlan:
    target_yaw_delta: float      # Radianos, ±π
    confidence: float            # 0.0 - 1.0
    min_distance_ahead: float    # Metros
    recommended_speed: float     # 0.0 - 1.0
    best_column: int            # Coluna escolhida no grid
    column_scores: List[float]   # Scores de todas as colunas
```

### **ReactiveCommand**
```python
@dataclass
class ReactiveCommand:
    yaw_delta: float            # Correção de direção
    forward_scale: float        # Fator de velocidade 0.0-1.0
    emergency_brake: bool       # Freio de emergência
    urgency: float             # Nível de urgência 0.0-1.0
```

---

## 🎨 **Módulo Visualization** {#módulo-visualization}

### **RenderPipeline**

#### **render_depth_colored()**
```python
def render_depth_colored(self, depth_map: np.ndarray, colormap: str = "plasma") -> np.ndarray
```

**Descrição:** Renderiza mapa de profundidade com cores.

**Parâmetros:**
- `depth_map`: Mapa de profundidade normalizado
- `colormap`: Nome do colormap OpenCV

**Retorna:** Imagem colorizada (H, W, 3)

#### **render_strategic_overlay()**
```python
def render_strategic_overlay(self, 
    image: np.ndarray, 
    grid: ZoneGrid, 
    nav_result: NavigationResult
) -> np.ndarray
```

**Descrição:** Renderiza overlay estratégico sobre imagem.

#### **render_complete_analysis()**
```python
def render_complete_analysis(self, analysis_frame: AnalysisFrame) -> np.ndarray
```

**Descrição:** Renderiza análise completa em uma imagem.

### **Colormaps Disponíveis**
- `"plasma"`: Roxo → Amarelo (padrão)
- `"viridis"`: Azul → Verde → Amarelo
- `"hot"`: Preto → Vermelho → Amarelo
- `"jet"`: Azul → Verde → Amarelo → Vermelho
- `"gray"`: Escala de cinza

---

## 🌐 **Módulo Web** {#módulo-web}

### **WebServer**

#### **Construtor**
```python
class WebServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8081)
```

#### **run()**
```python
def run(self, debug: bool = False) -> None
```

**Descrição:** Inicia servidor web Flask.

### **WebIntegration**
```python
class WebIntegration:
    def __init__(self, tof_analyzer: TOFAnalyzer)
    
    def get_video_stream(self) -> bytes
    def get_depth_stream(self) -> bytes
    def get_metrics(self) -> Dict
```

**Exemplo de Uso:**
```python
from tofcam.lib.web import WebServer
from tofcam.lib import create_tof_analyzer

# Criar analyzer
analyzer = create_tof_analyzer()

# Configurar servidor web
server = WebServer(host="0.0.0.0", port=8081)
server.set_analyzer(analyzer)

# Iniciar servidor
server.run()
```

---

## ⚙️ **Configurações** {#configurações}

### **TOFConfig (Principal)**
```python
@dataclass
class TOFConfig:
    camera: CameraConfig = field(default_factory=CameraConfig)
    midas: MidasConfig = field(default_factory=MidasConfig)
    navigation: NavigationConfig = field(default_factory=NavigationConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    save_frames: bool = False
    output_dir: str = "output_images"
    device: str = "auto"
```

### **NavigationConfig**
```python
@dataclass
class NavigationConfig:
    grid_size: Tuple[int, int] = (8, 12)  # (rows, cols)
    safe_distance: float = 1.5            # metros
    strategic_weight: float = 0.7         # peso strategic vs reactive
    emergency_threshold: float = 0.5      # threshold para emergency brake
    min_confidence: float = 0.3           # confiança mínima strategic
    max_yaw_rate: float = 0.1             # rad/s máximo
```

### **VisualizationConfig**
```python
@dataclass
class VisualizationConfig:
    show_grids: bool = True
    show_metrics: bool = True
    colormap: str = "plasma"
    overlay_alpha: float = 0.6
    grid_line_width: int = 2
    font_scale: float = 0.7
```

---

## 📊 **Tipos de Dados** {#tipos-de-dados}

### **Enums**

#### **NavigationMode**
```python
class NavigationMode(Enum):
    STRATEGIC = "strategic"
    REACTIVE = "reactive"
    HYBRID = "hybrid"
```

#### **CellState**
```python
class CellState(Enum):
    FREE = "free"
    OCCUPIED = "occupied"
    WARNING = "warning"
    UNKNOWN = "unknown"
```

#### **ZoneStatus**
```python
class ZoneStatus(Enum):
    SAFE = "safe"
    CAUTION = "caution"
    DANGER = "danger"
    EMERGENCY = "emergency"
```

### **Data Structures**

#### **AnalysisFrame**
```python
@dataclass
class AnalysisFrame:
    timestamp: float
    frame_id: int
    rgb_image: np.ndarray
    depth_map: np.ndarray
    strategic_grid: ZoneGrid
    reactive_grid: ZoneGrid
    navigation_result: NavigationResult
    depth_colored: Optional[np.ndarray] = None
```

#### **ZoneGrid**
```python
@dataclass
class ZoneGrid:
    cells: np.ndarray           # Grid de células (H, W)
    cell_size: Tuple[int, int]  # Tamanho de cada célula
    grid_shape: Tuple[int, int] # Shape do grid (rows, cols)
    timestamp: float
```

#### **ZoneCell**
```python
@dataclass
class ZoneCell:
    state: CellState
    distance: float
    confidence: float
    position: Tuple[int, int]
```

---

## 🔧 **Exemplos de Integração** {#exemplos}

### **Exemplo 1: Pipeline Básico**
```python
from tofcam.lib import (
    create_camera_manager,
    create_depth_estimator,
    create_navigator,
    TOFConfig
)

# Setup
config = TOFConfig()
camera_manager = create_camera_manager(config)
depth_estimator = create_depth_estimator(config)
navigator = create_navigator(config.navigation)

# Pipeline
frame = camera_manager.read_frame()
depth_map = depth_estimator.estimate_depth(frame)
nav_result = navigator.navigate(depth_map)

# Resultados
print(f"Yaw target: {np.rad2deg(nav_result.strategic.target_yaw_delta):.1f}°")
print(f"Confidence: {nav_result.strategic.confidence:.3f}")
```

### **Exemplo 2: Loop de Processamento**
```python
import time

def processing_loop():
    # Setup (uma vez)
    camera_manager = create_camera_manager()
    depth_estimator = create_depth_estimator()
    navigator = create_navigator()
    
    # Loop principal
    while True:
        start_time = time.time()
        
        # Pipeline
        frame = camera_manager.read_frame()
        if frame is None:
            continue
            
        depth_map = depth_estimator.estimate_depth(frame)
        nav_result = navigator.navigate(depth_map, NavigationMode.HYBRID)
        
        # Métricas
        processing_time = time.time() - start_time
        fps = 1.0 / processing_time
        
        print(f"FPS: {fps:.1f} | Strategic: {nav_result.strategic.confidence:.3f}")
        
        # Controle de taxa
        time.sleep(max(0, 1/30 - processing_time))  # 30 FPS target

# Executar
processing_loop()
```

### **Exemplo 3: Análise com Salvamento**
```python
from tofcam.lib import AnalysisFrame
import cv2
import json

def analyze_and_save(output_dir="analysis_output"):
    # Setup
    camera_manager = create_camera_manager()
    depth_estimator = create_depth_estimator()
    navigator = create_navigator()
    render_pipeline = create_render_pipeline()
    
    frame_count = 0
    
    for i in range(100):  # 100 frames
        # Análise
        frame = camera_manager.read_frame()
        depth_map = depth_estimator.estimate_depth(frame)
        nav_result = navigator.navigate(depth_map)
        
        # Criar grids
        strategic_grid = navigator.zone_mapper.create_strategic_grid(depth_map)
        reactive_grid = navigator.zone_mapper.create_reactive_grid(depth_map)
        
        # AnalysisFrame
        analysis = AnalysisFrame(
            timestamp=time.time(),
            frame_id=frame_count,
            rgb_image=frame,
            depth_map=depth_map,
            strategic_grid=strategic_grid,
            reactive_grid=reactive_grid,
            navigation_result=nav_result,
            depth_colored=render_pipeline.render_depth_colored(depth_map)
        )
        
        # Salvar
        frame_dir = f"{output_dir}/frame_{frame_count:04d}"
        os.makedirs(frame_dir, exist_ok=True)
        
        cv2.imwrite(f"{frame_dir}/original.jpg", frame)
        cv2.imwrite(f"{frame_dir}/depth.jpg", analysis.depth_colored)
        
        # Metadata
        metadata = {
            "frame_id": frame_count,
            "timestamp": analysis.timestamp,
            "strategic": {
                "target_yaw_delta": float(nav_result.strategic.target_yaw_delta),
                "confidence": float(nav_result.strategic.confidence)
            } if nav_result.strategic else None,
            "reactive": {
                "urgency": float(nav_result.reactive.urgency),
                "emergency_brake": bool(nav_result.reactive.emergency_brake)
            } if nav_result.reactive else None
        }
        
        with open(f"{frame_dir}/metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        frame_count += 1
        print(f"Frame {frame_count}/100 processado")

analyze_and_save()
```

### **Exemplo 4: Configuração Customizada**
```python
from tofcam.lib.config import *

# Configuração completa customizada
config = TOFConfig()

# Câmera alta resolução
config.camera.width = 1280
config.camera.height = 720
config.camera.fps = 15  # Reduzir FPS para alta resolução

# MiDaS otimizado
config.midas.model_type = "MiDaS_small"  # Mais rápido
config.midas.device = "cuda"  # Forçar GPU
config.midas.optimize = True

# Navegação sensitiva
config.navigation.grid_size = (10, 16)    # Grid maior
config.navigation.safe_distance = 2.0     # Distância maior
config.navigation.emergency_threshold = 0.3  # Mais sensitivo

# Visualização customizada
config.visualization.colormap = "viridis"
config.visualization.overlay_alpha = 0.8
config.visualization.show_metrics = True

# Usar configuração
camera_manager = create_camera_manager(config)
depth_estimator = create_depth_estimator(config)
navigator = create_navigator(config.navigation)
```

---

## 🔍 **Debugging e Profiling**

### **Logs Detalhados**
```python
import logging
from tofcam.lib.utils import logger

# Ativar debug logs
logger.setLevel(logging.DEBUG)

# Ou via environment variable
import os
os.environ['TOFCAM_LOG_LEVEL'] = 'DEBUG'
```

### **Performance Profiling**
```python
import cProfile
import time

def profile_analysis():
    # Setup
    camera_manager = create_camera_manager()
    depth_estimator = create_depth_estimator()
    navigator = create_navigator()
    
    def single_analysis():
        frame = camera_manager.read_frame()
        depth_map = depth_estimator.estimate_depth(frame)
        nav_result = navigator.navigate(depth_map)
        return nav_result
    
    # Profile
    cProfile.run('single_analysis()', 'tofcam_profile.prof')
    
    # Timing individual
    start = time.time()
    frame = camera_manager.read_frame()
    print(f"Camera: {(time.time() - start)*1000:.1f}ms")
    
    start = time.time()
    depth_map = depth_estimator.estimate_depth(frame)
    print(f"MiDaS: {(time.time() - start)*1000:.1f}ms")
    
    start = time.time()
    nav_result = navigator.navigate(depth_map)
    print(f"Navigation: {(time.time() - start)*1000:.1f}ms")

profile_analysis()
```

---

## 📚 **Documentação Relacionada**

- **[User Guide](user-guide.md)** - Manual de uso com exemplos práticos
- **[Architecture](architecture.md)** - Design e arquitetura do sistema
- **[Quick Start](quick-start.md)** - Comandos essenciais
- **[Installation](installation.md)** - Setup do ambiente

**[↑ Voltar ao índice da documentação](README.md)**