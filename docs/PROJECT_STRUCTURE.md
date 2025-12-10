# 📁 Estrutura do Projeto TOFcam

```
TOFcam/
├── 📄 LICENSE                    # Licença do projeto
├── 📄 README.md                  # Documentação principal
├── 📄 requirements.txt           # Dependências do projeto
├── 📄 .gitignore                # Arquivos ignorados pelo Git
│
├── 🧠 MÓDULOS PRINCIPAIS
│   ├── 📄 main.py               # Script principal de execução
│   ├── 📄 main_analyzer.py      # Analisador completo com auto-save
│   ├── 📄 camera.py             # Gerenciamento de câmeras
│   ├── 📄 midas.py              # Estimação de profundidade MiDaS
│   ├── 📄 mapping.py            # Algoritmos Strategic e Reactive
│   ├── 📄 view.py               # Visualização e debugging
│   ├── 📄 types.py              # Tipos de dados customizados
│   └── 📄 modules.py            # Módulos auxiliares
│
├── 🧪 TESTES
│   ├── 📁 tests/
│   │   ├── 📄 README.md         # Documentação dos testes
│   │   ├── 📄 run_tests.py      # Script principal de testes
│   │   ├── 📄 test_arrows.py    # Teste de direções das setas
│   │   ├── 📄 test_algorithms.py # Teste de algoritmos
│   │   └── 📄 test_cameras.py   # Teste de câmeras
│   │
│   └── 🚀 EXEMPLOS
│       ├── 📁 examples/
│       │   ├── 📄 README.md           # Documentação dos exemplos
│       │   ├── 📄 basic_usage.py      # Uso básico do sistema
│       │   └── 📄 algorithm_comparison.py # Comparação visual
│       │
│       └── 📁 output_images/          # Gerado automaticamente
│           ├── 📁 camera_original/    # Imagens originais
│           ├── 📁 depth_maps/         # Mapas de profundidade
│           ├── 📁 strategic_navigation/ # Navegação estratégica
│           ├── 📁 reactive_avoidance/   # Evasão reativa
│           └── 📁 complete_analysis/    # Análise completa
```

## 🎯 Scripts Principais

### Execução do Sistema
```bash
# Sistema completo com auto-save
python main_analyzer.py

# Sistema básico
python main.py
```

### Testes e Validação
```bash
# Executar todos os testes
cd tests/
python run_tests.py all

# Menu interativo de testes
python run_tests.py
```

### Exemplos Práticos
```bash
# Uso básico
cd examples/
python basic_usage.py

# Comparação de algoritmos
python algorithm_comparison.py
```

## 📦 Organização dos Módulos

### 🧠 **Módulos Principais**
- **`camera.py`** - Detecção e gerenciamento de câmeras
- **`midas.py`** - Estimação de profundidade usando MiDaS
- **`mapping.py`** - Algoritmos de navegação Strategic/Reactive
- **`view.py`** - Visualização, colormaps e debugging
- **`types.py`** - Estruturas de dados customizadas

### 🔧 **Scripts de Execução**
- **`main.py`** - Interface básica do sistema
- **`main_analyzer.py`** - Sistema completo com auto-save organizado

### 🧪 **Sistema de Testes**
- **`tests/run_tests.py`** - Coordenador de todos os testes
- **`tests/test_*.py`** - Testes específicos por componente
- **`examples/*.py`** - Exemplos práticos de uso

## 📊 Fluxo de Dados

```
📹 Câmera → 🧠 MiDaS → 🗺️ Algoritmos → 🎨 Visualização → 💾 Auto-save
    ↓           ↓           ↓              ↓              ↓
 camera.py   midas.py   mapping.py     view.py    main_analyzer.py
```

## 🎨 Outputs Organizados

O sistema salva automaticamente em `output_images/` com estrutura organizada:

- **📁 `camera_original/`** - Frames originais da câmera
- **📁 `depth_maps/`** - Mapas de profundidade (colormap JET invertido)
- **📁 `strategic_navigation/`** - Navegação estratégica com setas amarelas
- **📁 `reactive_avoidance/`** - Evasão reativa com setas magentas  
- **📁 `complete_analysis/`** - Análise completa combinada

## ✨ Características da Organização

✅ **Modularidade** - Cada componente em arquivo separado
✅ **Testabilidade** - Testes organizados e automatizados
✅ **Documentação** - READMEs específicos para cada seção
✅ **Exemplos** - Casos de uso práticos bem documentados
✅ **Limpeza** - Arquivos temporários e duplicados removidos
✅ **Git-Ready** - `.gitignore` configurado adequadamente

---

🚀 **Sistema totalmente organizado e pronto para uso!**