# TOFcam - Professional Structure

✅ **Estrutura Modular Reorganizada com Convenção Profissional**

## 📁 Nova Arquitetura

```
TOFcam/
├── 📦 tofcam/                 # Biblioteca principal
│   ├── __init__.py           # Exports principais
│   ├── core.py              # Análise central (ex: analyzer_lib.py)
│   ├── web.py               # Servidor web (ex: web_viewer_lib.py)
│   ├── depth.py             # Estimação profundidade (ex: depth_estimator.py)
│   ├── nav.py               # Navegação (ex: mapping.py)
│   ├── types.py             # Tipos e estruturas (ex: tofcam_types.py)
│   └── camera.py            # Gestão câmeras
│
├── 🚀 run.py                 # Entry point principal
├── 📚 docs/                  # Documentação
├── 🧪 demos/                 # Demonstrações
├── ✅ tests/                 # Testes
└── 📋 requirements.txt       # Dependências
```

## 🎯 Naming Convention Adotada

| Antes | Depois | Função |
|-------|--------|---------|
| `analyzer_lib.py` | `core.py` | Análise central |
| `web_viewer_lib.py` | `web.py` | Interface web |
| `depth_estimator.py` | `depth.py` | Estimação profundidade |
| `mapping.py` | `nav.py` | Algoritmos navegação |
| `tofcam_types.py` | `types.py` | Definições de tipos |

## 🚀 Como Usar

### Executar Interface Web
```bash
conda activate opencv
python run.py
```

### Usar como Biblioteca
```python
from tofcam import WebServer, AnalysisConfig

# Configuração
config = AnalysisConfig(
    use_sophisticated_analysis=True,
    save_frames=False
)

# Servidor web
server = WebServer(config=config)
server.run()
```

### Usar Componentes Individuais
```python
from tofcam.core import TOFAnalyzer
from tofcam.depth import DepthEstimator
from tofcam.nav import StrategicPlanner

# Análise customizada
analyzer = TOFAnalyzer(config)
depth_estimator = DepthEstimator()
planner = StrategicPlanner()
```

## 📊 Acesso à Interface

🌐 **Interface Web:** http://localhost:8081

## ✅ Benefícios da Nova Estrutura

1. **🏗️ Modularidade** - Componentes independentes
2. **📝 Naming Convention** - Nomes claros e profissionais  
3. **🔧 Facilidade de Import** - Estrutura Python padrão
4. **🎯 Responsabilidade Única** - Cada módulo tem função específica
5. **⚡ Performance** - Imports otimizados
6. **🧪 Testabilidade** - Módulos isolados para testes

## 🔄 Compatibilidade

- ✅ **Interface web mantida** - Funcionalidade 100% preservada
- ✅ **Algoritmos intactos** - MiDaS + navegação sofisticada  
- ✅ **Performance igual** - Mesma velocidade de processamento
- ✅ **APIs preservadas** - Endpoints web funcionais

**Status:** 🎉 **Sistema totalmente operacional com nova estrutura profissional!**