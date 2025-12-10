# Demos TOFcam - Documentação

Esta pasta contém demonstrações organizadas do sistema TOFcam.

## 📖 Documentação Completa

Para documentação detalhada do projeto, consulte:

**[📚 docs/README.md](../docs/README.md)** - Índice completo da documentação

## 🎬 Demos Disponíveis

Execute o gerenciador interativo:
```bash
python run_demos.py
```

## Estrutura

```
demos/
├── run_demos.py              # Gerenciador interativo de demos
├── basic_usage.py             # Demo: Uso básico da biblioteca centralizada
├── algorithm_comparison.py    # Demo: Comparação de algoritmos
├── README.md                  # Este arquivo
├── library/
│   └── demo_lib.py           # Demo: Configurações da biblioteca
├── camera_selection/
│   └── camera_selector.py    # Demo: Interface para seleção de câmeras
└── outputs/
    └── (resultados dos demos com persistência)
```

## Como Usar

### Modo Interativo (Recomendado)
```bash
python demos/run_demos.py
```

### Execução Direta
```bash
# Demo básico com biblioteca centralizada
python demos/basic_usage.py

# Comparação de algoritmos
python demos/algorithm_comparison.py

# Configurações da biblioteca
python demos/library/demo_lib.py

# Seleção de câmeras via web
python demos/camera_selection/camera_selector.py
```

## Descrição dos Demos

### 1. **basic_usage.py**
- **Propósito**: Demonstra uso básico da biblioteca centralizada `analyzer_lib.py`
- **Características**: 
  - Análise em tempo real
  - Interface simples via OpenCV
  - Configuração para não persistir frames

### 2. **algorithm_comparison.py**
- **Propósito**: Comparação visual entre algoritmos Strategic, Reactive e biblioteca centralizada
- **Características**:
  - Visualização lado a lado
  - Métricas de diferença entre algoritmos
  - Salvamento de frames para análise

### 3. **library/demo_lib.py**
- **Propósito**: Demonstra diferentes configurações da biblioteca centralizada
- **Características**:
  - Modo web vs modo persistência
  - Configurações customizáveis
  - Exemplos de parâmetros

### 4. **camera_selection/camera_selector.py**
- **Propósito**: Interface web simplificada para testar diferentes câmeras
- **Características**:
  - Interface web básica
  - Teste de múltiplas câmeras
  - Validação de funcionalidade

## Dependências

Todos os demos utilizam as mesmas dependências do projeto principal:
- OpenCV (`cv2`)
- PyTorch (para MiDaS)
- NumPy
- Bibliotecas internas: `analyzer_lib`, `camera`, `mapping`, etc.


## 📖 Documentação de Uso

- **Como usar demos**: [../docs/HOW_TO_USE.md](../docs/HOW_TO_USE.md)
- **Guia completo**: [../docs/USAGE_GUIDE.md](../docs/USAGE_GUIDE.md)
- **Estrutura do projeto**: [../docs/PROJECT_STRUCTURE.md](../docs/PROJECT_STRUCTURE.md)
