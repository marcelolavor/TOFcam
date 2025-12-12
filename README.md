# TOFcam

**Sistema de análise de profundidade e navegação em tempo real com MiDaS neural network.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)](https://opencv.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-MiDaS-orange.svg)](https://pytorch.org)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

## 🚀 Início Rápido

```bash
# 1. Ativar ambiente
conda activate opencv

# 2. Executar TOFcam (modo interativo)
python main.py

# 3. Ou usar modo específico:
python main.py --desktop    # Interface 4 janelas
python main.py --web       # Interface navegador  
python main.py --analysis  # Processamento background
```

**🔗 Links Rápidos:** [📖 Documentação Completa](docs/) | [⚡ Como Usar](docs/quick-start.md) | [🧪 Demos](demos/) | [⚙️ Setup](docs/installation.md)

---

## ⚡ Principais Funcionalidades

### 🎯 **Estimação de Profundidade**
- **MiDaS Neural Network** para análise precisa
- **Processamento em tempo real** com otimizações CPU/GPU
- **Mapas de calor** com visualização intuitiva

### 🧭 **Sistema de Navegação Dual**
- **Strategic Navigation:** Planejamento global de rota
- **Reactive Avoidance:** Desvio reativo de obstáculos
- **Hybrid Mode:** Combinação inteligente de estratégias

### 🖥️ **Interfaces Múltiplas**
- **Desktop:** 4 janelas especializadas (Camera, Depth, Strategic, Reactive)
- **Web:** Interface moderna acessível via browser
- **API:** Biblioteca `tofcam.lib` para integração

### 📊 **Análise Avançada**
- **Zone Mapping** configurável para análise espacial
- **Persistência automática** de análises e métricas
- **Multi-câmera** com detecção automática

---

## 📖 Documentação

| Documento | Descrição | Para Quem |
|-----------|-----------|-----------|
| **[📋 Quick Start](docs/quick-start.md)** | Comandos essenciais por categoria | Todos |
| **[📚 Manual Completo](docs/user-guide.md)** | Guia detalhado com exemplos | Usuários |
| **[🔧 API Reference](docs/api-reference.md)** | Documentação da biblioteca | Desenvolvedores |
| **[🏗️ Architecture](docs/architecture.md)** | Estrutura e design do sistema | Contribuidores |
| **[⚙️ Installation](docs/installation.md)** | Setup completo e troubleshooting | Todos |
| **[🖥️ Display Setup](docs/display-setup.md)** | Configuração de ambiente gráfico | WSL/SSH users |

---

## 🎮 Exemplos de Uso

### Interface Desktop
```bash
# Sistema completo com 4 janelas
python main.py
```

### Análise com Persistência
```bash
# Análise interativa com salvamento
python main_analyzer.py
```

### Interface Web
```bash
# Servidor web com streaming
python run.py
```

### Demonstrações
```bash
# Menu interativo com todos os demos
python demos/run_demos.py
```

---

## 🏗️ Arquitetura do Sistema

```
TOFcam/
├── 🚀 Aplicações Principais
│   ├── main.py              # Sistema completo (4 janelas)
│   ├── main_analyzer.py     # Análise com salvamento
│   ├── run.py               # Interface web
│   └── setup_display.py     # Configurador de display
│
├── 📚 Biblioteca Centralizada
│   └── tofcam/lib/          # Biblioteca modular
│       ├── camera.py        # Gestão de câmeras
│       ├── depth.py         # Estimação MiDaS
│       ├── navigation.py    # Algoritmos de navegação
│       ├── visualization.py # Renderização e UI
│       ├── web.py           # Interface web
│       └── utils.py         # Utilitários
│
├── 🧪 Demos & Testes
│   ├── demos/               # Demonstrações interativas
│   └── tests/               # Suite de testes
│
└── 📖 Documentação
    └── docs/                # Guias e referências
```

---

## 🎯 Para Diferentes Usuários

### 👤 **Primeiro uso?**
1. Veja [Installation Guide](docs/installation.md)
2. Execute `python demos/run_demos.py`
3. Consulte [Quick Start](docs/quick-start.md)

### 💻 **Desenvolvedor?**
1. Estude [Architecture](docs/architecture.md)
2. Explore [API Reference](docs/api-reference.md)
3. Execute `python tests/run_tests.py`

### 🔬 **Pesquisador?**
1. Use `python main_analyzer.py` para coleta
2. Veja [User Guide](docs/user-guide.md) para análise
3. Configure [Display Setup](docs/display-setup.md) se necessário

---

## 🤝 Contribuição

Veja nossa [documentação completa](docs/) para:
- **[Installation Guide](docs/installation.md)** - Setup do ambiente
- **[Architecture](docs/architecture.md)** - Como contribuir
- **[API Reference](docs/api-reference.md)** - Referência técnica

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para detalhes.

---

**💡 Dica:** Para navegação rápida, sempre comece com [docs/](docs/) - toda documentação está organizada e interligada!