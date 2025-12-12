# 🖥️ Guia de Visualização para VS Code

## 🎯 **3 Soluções para Ver Imagens em Tempo Real**

### 1️⃣ **Solução Recomendada: Web Viewer** 🌐
```bash
# Execute o visualizador web
python web_viewer.py

# Abra no navegador: http://localhost:8080
```

**Vantagens:**
- ✅ Funciona em qualquer VS Code (local, remoto, WSL)
- ✅ Interface moderna e responsiva
- ✅ Não depende de configurações X11
- ✅ Visualização lado a lado dos algoritmos

---

### 2️⃣ **Configuração X11 (Linux/WSL)** 🐧
```bash
# Execute o configurador automático
python setup_display.py

# Escolha opção 1 (configuração completa)
# Depois execute:
./run_tofcam.sh
```

**Para WSL especificamente:**
```bash
# Instalar X11 server no Windows (VcXsrv ou Xming)
# No WSL:
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
python main_analyzer.py
```

---

### 3️⃣ **Salvamento de Imagens** 💾
```bash
# Sistema salva automaticamente imagens
python main_analyzer.py

# Visualize as imagens salvas em:
# output_images/complete_analysis/
```

## 🚀 **Instruções Passo a Passo**

### **Opção 1: Web Viewer (Mais Fácil)**

1. **Execute o servidor web:**
   ```bash
   python web_viewer.py
   ```

2. **Abra o navegador:**
   - No VS Code: `Ctrl+Shift+P` → "Simple Browser: Show"
   - Digite: `http://localhost:8080`

3. **Pronto!** Você verá:
   - Stream de vídeo em tempo real
   - Visualização 2x2: Original, Depth, Strategic, Reactive
   - Estatísticas em tempo real

### **Opção 2: Configuração X11**

1. **Execute o configurador:**
   ```bash
   python setup_display.py
   ```

2. **Escolha "1" para configuração completa**

3. **Teste com:**
   ```bash
   ./run_tofcam.sh
   ```

4. **Se não funcionar, tente manual:**
   ```bash
   # Instalar dependências
   sudo apt install x11-apps xauth
   
   # Configurar display
   export DISPLAY=:0
   # Ou para WSL:
   export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
   
   # Testar
   xeyes  # Deve abrir uma janela
   
   # Executar TOFcam
   python main_analyzer.py
   ```

## 🔧 **Troubleshooting**

### **"No display available"**
- ✅ Use Web Viewer: `python web_viewer.py`
- ✅ Configure X11: `python setup_display.py`

### **"Connection refused"**
- Para WSL: Instale VcXsrv no Windows
- Para Linux: `xhost +local:`

### **Janelas não aparecem no VS Code**
- ✅ **Melhor solução:** Use Web Viewer
- ✅ Use Simple Browser no VS Code

### **Performance baixa**
- Reduza FPS no web viewer (linha 80: `time.sleep(0.2)`)
- Use qualidade JPEG menor (linha 115: `JPEG_QUALITY, 70`)

## 💡 **Dicas**

### **VS Code Simple Browser**
1. `Ctrl+Shift+P`
2. Digite: "Simple Browser: Show"
3. URL: `http://localhost:8080`

### **Para Apresentações**
- Use Web Viewer: interface limpa e profissional
- Funciona em qualquer dispositivo na rede

### **Para Desenvolvimento**
- Web Viewer para debug visual
- Imagens salvas para análise posterior

---

## 🎯 **Resumo Rápido**

**Quer ver rapidamente?**
```bash
python web_viewer.py
# Abra http://localhost:8080 no navegador
```

**Quer configuração completa?**
```bash
python setup_display.py  # Opção 1
./run_tofcam.sh
```

**Sem pressa?**
```bash
python main_analyzer.py
# Veja as imagens em output_images/
```