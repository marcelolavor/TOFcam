#!/usr/bin/env python3
"""
Teste simples de signal handling
"""
import signal
import sys
import time
import os

def test_signal_handler(sig, frame):
    print(f"🛑 Recebido sinal {sig}")
    print("🚨 Forçando saída...")
    os._exit(0)

# Setup signal handler
signal.signal(signal.SIGINT, test_signal_handler)
signal.signal(signal.SIGTERM, test_signal_handler)

print("🚀 Teste de signal handler iniciado")
print("🛑 Pressione Ctrl+C para testar")

try:
    for i in range(30):  # 30 segundos
        print(f"⏰ Segundo {i+1}/30")
        time.sleep(1)
except KeyboardInterrupt:
    print("KeyboardInterrupt capturado!")
    sys.exit(0)

print("✅ Teste concluído normalmente")