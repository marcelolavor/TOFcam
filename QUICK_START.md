# TOFcam - Início Rápido ⚡

## 🚀 Executar Agora (3 comandos)

```bash
# 1. Ativar ambiente (OBRIGATÓRIO)
conda activate opencv

# 2. Escolher modo de execução:
python main.py --web                # Interface navegador (RECOMENDADO)
python tofcam/web.py               # Servidor web direto
python main.py --desktop          # Interface desktop (4 janelas)
python main.py --analysis         # Background + salvamento

# 3. Acessar: http://localhost:8082
```

## 🎯 Web Interface (Mais Popular)

```bash
conda activate opencv && python tofcam/web.py
```

**URL:** http://localhost:8082  
**Features:** MiDaS neural network, controles em tempo real, esquema de cores intuitivo

## 📊 Controles Web
- **MiDaS**: 87% (estimação neural)
- **Gradiente**: 58% (detecção bordas)  
- **Cores**: 🔴=Próximo, 🟡=Médio, 🟢=Distante

## 📖 Documentação Completa
- [README.md](README.md) - Visão geral completa
- [docs/](docs/) - Documentação detalhada
- [demos/](demos/) - Exemplos práticos