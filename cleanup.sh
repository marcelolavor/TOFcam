#!/bin/bash
# Script de limpeza de processos TOFcam

echo "🧹 Limpando processos TOFcam..."

# Matar processos Python relacionados ao TOFcam
pkill -9 -f "python.*run.py"
pkill -9 -f "python.*web_viewer"  
pkill -9 -f "python.*analyzer"
pkill -9 -f "python.*basic_usage"
pkill -9 -f "python.*demo"

# Verificar jobs em background
jobs -p | xargs -r kill -9 2>/dev/null

echo "✅ Processos limpos!"

# Verificar se portas estão livres
if netstat -tlnp 2>/dev/null | grep -E "(8080|8081)" > /dev/null; then
    echo "⚠️  Ainda há processos usando portas 8080/8081"
    netstat -tlnp 2>/dev/null | grep -E "(8080|8081)"
else
    echo "✅ Portas 8080/8081 livres"
fi