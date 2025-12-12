# 🧪 Sistema de Testes TOFcam

Sistema organizador de testes interativo para validação completa do projeto TOFcam.

## 📂 Estrutura de Testes

### 📹 Hardware
- **test_cameras.py** - Detecta e testa todas as câmeras disponíveis
- **test_camera0_only.py** - Servidor web completo com análise de profundidade usando câmera 0

### 🧠 Algoritmos
- **test_algorithms.py** - Validação dos algoritmos Strategic e Reactive
- **test_arrows.py** - Teste de cálculo e exibição de direções

### 🔬 Integração
- **test_integration.py** - Teste de integração completa do sistema
- **test_performance.py** - Benchmark de performance e velocidade

### 🧪 Biblioteca
- **demo_lib.py** - Demonstração da biblioteca centralizada com diferentes configurações
- **main_analyzer_lib.py** - Teste do analyzer com persistência usando a biblioteca  
- **web_viewer_lib.py** - Teste da interface web refatorada

## 🚀 Como Usar

### Modo Interativo
```bash
cd tests/
python run_tests.py
```

Apresenta um menu interativo onde você pode:
- Executar testes individuais
- Executar todos os testes
- Executar por categoria
- Ver descrição detalhada de cada teste

### Modo Linha de Comando

**Listar todos os testes:**
```bash
python run_tests.py --list
```

**Executar todos os testes:**
```bash
python run_tests.py --all
```

### Exemplos de Uso

**Teste rápido de câmeras:**
```bash
python run_tests.py
# Escolher opção 1: Testa acesso às câmeras
```

**Validação completa do sistema:**
```bash
python run_tests.py --all
```

**Teste específico de uma categoria:**
```bash
python run_tests.py
# Escolher opção 12: Executar por categoria
# Escolher categoria desejada
```

## ✅ Resultados Esperados

### 📹 Testes de Hardware
- Detecção automática de câmeras funcionais
- Validação de resolução e FPS
- Teste de captura contínua
- Verificação de qualidade da imagem

### 🧠 Testes de Algoritmos  
- Validação de cálculos de navegação
- Teste de casos extremos
- Comparação entre algoritmos Strategic e Reactive
- Verificação de precisão das direções

### 🌐 Testes de Interface
- Validação do streaming HTTP
- Teste de diferentes formatos de imagem
- Verificação da API web

### 🧪 Testes de Biblioteca
- Validação da arquitetura centralizada
- Teste de diferentes configurações
- Verificação de consistência entre componentes

## 🔧 Configuração do Ambiente

**Requisitos:**
- Python 3.12+
- Conda environment "opencv" 
- Câmeras conectadas (para testes de hardware)

**Setup:**
```bash
conda activate opencv
cd /home/lavor/projects/TOFcam/tests/
python run_tests.py --list  # Verificar testes disponíveis
```

## 📊 Interpretando Resultados

### ✅ Teste Passou
- Todas as funcionalidades validadas
- Sistema operacional

### ⚠️ Aviso
- Funcionalidade parcial
- Possíveis problemas menores
- Sistema ainda utilizável

### ❌ Falhou
- Funcionalidade crítica não funciona
- Requer investigação
- Sistema pode não operar corretamente

## 🛠️ Troubleshooting

### Problemas Comuns

**Câmeras não detectadas:**
```bash
# Verificar permissões
sudo usermod -a -G video $USER
# Logout/login necessário

# Verificar dispositivos
ls /dev/video*
```

**Ambiente conda não ativo:**
```bash
conda activate opencv
pip install -r ../requirements.txt
```

**Importação de módulos falha:**
```bash
cd /home/lavor/projects/TOFcam/
export PYTHONPATH=$PWD:$PYTHONPATH
cd tests/
python run_tests.py
```

## 🎯 Desenvolvimento

### Adicionando Novos Testes

1. Criar arquivo `test_nome.py` na categoria apropriada
2. Editar `run_tests.py` e adicionar à categoria correspondente
3. Implementar testes seguindo o padrão existente

### Estrutura de Teste Padrão

```python
#!/usr/bin/env python3
"""
Descrição do teste
"""

def test_funcionalidade():
    """Função de teste principal"""
    print("🧪 Iniciando teste...")
    
    # Lógica do teste
    resultado = realizar_teste()
    
    if resultado:
        print("✅ Teste passou!")
        return True
    else:
        print("❌ Teste falhou!")
        return False

if __name__ == "__main__":
    success = test_funcionalidade()
    exit(0 if success else 1)
```

## 📈 Histórico

- **v1.0** - Testes básicos individuais
- **v2.0** - Sistema organizado com run_tests.py
- **v3.0** - Gerenciador interativo com categorias
- **v4.0** - Integração com biblioteca centralizada