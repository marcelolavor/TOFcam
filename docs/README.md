# 📖 TOFcam Documentation

**Documentação completa do sistema TOFcam - Análise de profundidade e navegação em tempo real.**

## 🚀 Navegação Rápida

### Por Tipo de Usuário

| Usuário | Primeiro Passo | Documentos Relevantes |
|---------|----------------|----------------------|
| **🆕 Iniciante** | [Quick Start](quick-start.md) → [Installation](installation.md) | [User Guide](user-guide.md) |
| **💻 Desenvolvedor** | [API Reference](api-reference.md) → [Architecture](architecture.md) | [Contributing](#) |
| **🔬 Pesquisador** | [User Guide](user-guide.md) → [Advanced Features](#) | [Analysis Tools](#) |
| **⚙️ Admin/Deploy** | [Installation](installation.md) → [Display Setup](display-setup.md) | [Troubleshooting](#) |

### Por Necessidade

| Preciso... | Documento | Tempo |
|------------|-----------|-------|
| **Executar rapidamente** | [Quick Start](quick-start.md) | 2 min |
| **Instalar/configurar** | [Installation](installation.md) | 10-15 min |
| **Entender funcionamento** | [User Guide](user-guide.md) | 20-30 min |
| **Desenvolver/integrar** | [API Reference](api-reference.md) | 45+ min |
| **Resolver problemas** | [Display Setup](display-setup.md) | 10-20 min |
| **Contribuir com código** | [Architecture](architecture.md) | 60+ min |

---

## 📚 Documentação Disponível

### 🚀 **Para Usar o Sistema**

#### [📋 Quick Start](quick-start.md)
**Comandos essenciais para usar imediatamente**
- Menu rápido por categoria (Iniciante, Desenvolvedor, Pesquisador)
- Comandos diretos sem explicação
- Links para documentação detalhada

#### [⚙️ Installation Guide](installation.md)
**Setup completo do ambiente de desenvolvimento**
- Instalação de dependências
- Configuração do conda environment
- Verificação da instalação
- Troubleshooting comum

#### [📚 User Guide](user-guide.md)
**Manual completo com exemplos práticos**
- Todos os modos de execução explicados
- Exemplos de código e saída esperada
- Configurações avançadas
- Análise e interpretação de resultados

#### [🖥️ Display Setup](display-setup.md)
**Configuração de ambiente gráfico**
- Solução para WSL, SSH, e ambientes remotos
- Configuração X11/Wayland
- Alternativas (web viewer, salvamento de imagens)
- Troubleshooting de display

---

### 🔧 **Para Desenvolvedores**

#### [🏗️ Architecture](architecture.md)
**Design e estrutura do sistema**
- Visão geral da arquitetura
- Módulos e responsabilidades
- Fluxo de dados e processamento
- Decisões de design e rationale
- Como contribuir

#### [📖 API Reference](api-reference.md)
**Referência completa da biblioteca tofcam.lib**
- Todas as classes e funções documentadas
- Exemplos de uso para cada módulo
- Configurações disponíveis
- Tipos de dados e enums
- Patterns de uso recomendados

#### [🧪 Testing Guide](testing-guide.md)
**Testes e validação do sistema**
- Como executar a suite de testes
- Criação de novos testes
- Benchmarks e performance
- Validação de algoritmos

---

## 🎯 Fluxos de Uso Recomendados

### 🆕 **Primeira vez usando TOFcam**
1. **[Installation](installation.md)** → Setup do ambiente
2. **[Quick Start](quick-start.md)** → Comandos básicos
3. **[User Guide](user-guide.md)** → Entendimento completo

### 💻 **Desenvolvimento/Integração**
1. **[Architecture](architecture.md)** → Entender o sistema
2. **[API Reference](api-reference.md)** → Conhecer a API
3. **[Testing Guide](testing-guide.md)** → Validar changes

### 🔧 **Troubleshooting**
1. **[Display Setup](display-setup.md)** → Problemas de visualização
2. **[Installation](installation.md)** → Problemas de ambiente
3. **[User Guide](user-guide.md)** → Problemas de uso

---

## 🔍 Busca Rápida por Tópicos

### Instalação e Setup
- [Conda Environment](installation.md#conda-setup)
- [Dependências](installation.md#dependencies)
- [GPU/CPU Config](installation.md#gpu-setup)
- [Display Config](display-setup.md)

### Execução
- [Interface Desktop](quick-start.md#desktop)
- [Interface Web](quick-start.md#web)
- [Análise Batch](quick-start.md#analysis)
- [Demos](quick-start.md#demos)

### Desenvolvimento
- [tofcam.lib API](api-reference.md)
- [Arquitetura](architecture.md#overview)
- [Extending System](architecture.md#extending)
- [Testing](testing-guide.md)

### Algoritmos
- [MiDaS Integration](user-guide.md#midas)
- [Strategic Navigation](user-guide.md#strategic)
- [Reactive Avoidance](user-guide.md#reactive)
- [Hybrid Mode](user-guide.md#hybrid)

---

## 📄 Sobre a Documentação

### 📝 **Estrutura dos Documentos**
- **Quick Start**: Comandos diretos, mínima explicação
- **Installation**: Passo-a-passo detalhado
- **User Guide**: Exemplos práticos e completos
- **API Reference**: Documentação técnica completa
- **Architecture**: Design e contribuição

### 🔗 **Navegação**
Todos os documentos possuem:
- Links internos para navegação rápida
- Referências cruzadas para tópicos relacionados
- Links de volta para este índice
- Seções "Ver também" onde apropriado

### 💡 **Convenções**
- 🚀 Início rápido e comandos essenciais
- ⚙️ Configuração e setup
- 💻 Desenvolvimento e código
- 🔧 Troubleshooting e soluções
- 📊 Dados, métricas e análise
- 🎯 Objetivos e resultados esperados

---

**💡 Dica de Navegação:** Use Ctrl+F para buscar tópicos específicos em qualquer documento. Todos os documentos têm índice navegável no início.