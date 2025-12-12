# ⚡ Quick Start - TOFcam

**Comandos essenciais organizados por categoria de usuário.**

## 🆕 **Para Iniciantes**

### Executar Sistema Completo
```bash
# Desktop: 4 janelas (Camera, Depth, Strategic, Reactive)
python main.py

# Web: Interface no browser
python run.py
# → http://localhost:8081
```

### Demos Interativos
```bash
# Menu com todos os demos
python demos/run_demos.py

# Demo básico direto
python demos/basic_usage.py
```

**📖 Próximo passo:** [User Guide](user-guide.md) para entender o que você está vendo.

---

## 💻 **Para Desenvolvedores**

### Teste da API
```bash
# Testes automatizados
python tests/run_tests.py

# Teste simples da biblioteca
python test_library_simple.py
```

### Desenvolvimento
```bash
# Análise com persistência para debug
python main_analyzer.py

# Configuração de display para desenvolvimento remoto
python setup_display.py
```

**📖 Próximo passo:** [API Reference](api-reference.md) para integração.

---

## 🔬 **Para Pesquisadores**

### Coleta de Dados
```bash
# Análise interativa com salvamento automático
python main_analyzer_lib.py

# Análise batch contínua
echo "3" | python main_analyzer_lib.py  # 10 frames automáticos
```

### Análise Detalhada
```bash
# Comparação de algoritmos
python demos/algorithm_comparison.py

# Análise completa com salvamento categorizado
python main_analyzer.py
```

**📖 Próximo passo:** [User Guide](user-guide.md) para interpretar resultados.

---

## ⚙️ **Para Administradores**

### Setup Inicial
```bash
# Verificar ambiente completo
python setup_display.py

# Ativação do ambiente
conda activate opencv
```

### Troubleshooting
```bash
# Verificar câmeras disponíveis
python -c "from tofcam.lib import discover_cameras; print(discover_cameras())"

# Teste de display
python setup_display.py  # Escolher opção 2 (teste básico)
```

**📖 Próximo passo:** [Installation Guide](installation.md) para setup completo.

---

## 🔥 **Comandos Mais Usados**

| Comando | O que faz | Quando usar |
|---------|-----------|-------------|
| `python main.py` | 4 janelas desktop | Análise visual interativa |
| `python run.py` | Interface web | Demos, apresentações |
| `python demos/run_demos.py` | Menu de demos | Exploração, aprendizado |
| `python main_analyzer.py` | Análise + salvamento | Coleta de dados, pesquisa |
| `python setup_display.py` | Config display | Problemas de visualização |

---

## 🎯 **Por Objetivo**

### Quero ver o sistema funcionando rapidamente
```bash
python demos/run_demos.py
# → Escolha opção 2 (Uso básico)
```

### Quero coletar dados para análise
```bash
python main_analyzer_lib.py
# → Escolha opção 3 (Análise contínua)
```

### Quero apresentar/demonstrar
```bash
python run.py
# → Acesse http://localhost:8081
```

### Quero desenvolver/integrar
```bash
python test_library_simple.py  # Teste básico
python tests/run_tests.py      # Teste completo
```

### Tenho problemas de display
```bash
python setup_display.py
# → Escolha opção 1 (Setup completo)
```

---

## 🚨 **Problemas Comuns**

| Erro | Solução Rápida | Documentação |
|------|----------------|--------------|
| `No display` | `python setup_display.py` | [Display Setup](display-setup.md) |
| `ModuleNotFoundError` | `conda activate opencv` | [Installation](installation.md) |
| `Camera not found` | Verificar USB, permissões | [User Guide](user-guide.md#cameras) |
| `Web server failed` | Usar porta diferente | [User Guide](user-guide.md#web) |

---

## 📖 **Documentação Relacionada**

- **[📚 User Guide](user-guide.md)** - Manual completo com exemplos
- **[⚙️ Installation](installation.md)** - Setup do ambiente
- **[🖥️ Display Setup](display-setup.md)** - Configuração gráfica
- **[🏗️ Architecture](architecture.md)** - Como o sistema funciona
- **[📖 API Reference](api-reference.md)** - Referência da biblioteca

**[↑ Voltar ao índice da documentação](README.md)**