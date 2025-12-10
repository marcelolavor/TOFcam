# 🧪 Testes do Sistema TOFcam

Esta pasta contém todos os testes e validações para o sistema TOFcam.

## 📁 Estrutura de Testes

### 🎯 Testes Principais
- **`test_arrows.py`** - Validação das direções das setas de navegação
- **`test_algorithms.py`** - Comparação entre algoritmos Strategic e Reactive
- **`test_cameras.py`** - Teste de detecção e funcionamento das câmeras
- **`run_tests.py`** - Script principal para executar todos os testes

## 🚀 Como Executar

### Executar Todos os Testes
```bash
cd tests/
python run_tests.py all
```

### Testes Específicos
```bash
# Teste das direções das setas
python run_tests.py arrows

# Teste dos algoritmos
python run_tests.py algorithms

# Menu interativo
python run_tests.py
```

### Testes Individuais
```bash
# Validação das setas
python test_arrows.py

# Comparação de algoritmos
python test_algorithms.py

# Teste de câmeras
python test_cameras.py
```

## 📊 Tipos de Teste

### 1️⃣ **Teste de Setas** (`test_arrows.py`)
- Valida a fórmula matemática: `angle = -π/2 - yaw_delta`
- Testa valores extremos (-2.0 a +2.0)
- Confirma direções lógicas (esquerda, centro, direita)

### 2️⃣ **Teste de Algoritmos** (`test_algorithms.py`)
- Compara comportamento Strategic vs Reactive
- Testa cenários: obstáculo esquerda/direita/centro, corredor, caminho livre
- Valida casos extremos e gradientes

### 3️⃣ **Teste de Câmeras** (`test_cameras.py`)
- Detecta câmeras disponíveis no sistema
- Testa captura de frames
- Valida resolução e qualidade

## ✅ Resultados Esperados

### Direções das Setas
- **Valores negativos** → Seta aponta para esquerda ⬅️
- **Valor zero** → Seta aponta para frente ⬆️  
- **Valores positivos** → Seta aponta para direita ➡️

### Algoritmos
- **Strategic**: Navegação otimizada baseada no campo de visão completo
- **Reactive**: Evasão rápida baseada em obstáculos próximos
- **Concordância**: Algoritmos devem concordar em cenários simples
- **Divergência**: É normal divergir em cenários complexos

## 🏆 Critérios de Sucesso

✅ **Teste Aprovado** quando:
- Todas as setas apontam na direção correta
- Algoritmos produzem valores lógicos
- Sistema não apresenta erros ou exceções
- Câmeras são detectadas e funcionam

❌ **Teste Reprovado** quando:
- Setas apontam na direção errada
- Algoritmos produzem valores inconsistentes  
- Erros ou crashes durante execução
- Câmeras não funcionam corretamente

---
💡 **Dica**: Execute `python run_tests.py` para o menu interativo com todas as opções!