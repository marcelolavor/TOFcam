#!/usr/bin/env python3
"""
Teste específico para câmera 2
"""

import cv2
import time

print("🔍 Testando câmera 2 especificamente...")

# Tentar diferentes configurações para câmera 2
for backend in [cv2.CAP_V4L2, cv2.CAP_GSTREAMER, cv2.CAP_ANY]:
    print(f"\n📹 Testando com backend {backend}...")
    
    cap = cv2.VideoCapture(2, backend)
    
    if cap.isOpened():
        print("✅ Conexão estabelecida")
        
        # Configurar propriedades básicas
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Tentar ler frame com timeout maior
        for i in range(5):
            print(f"   Tentativa {i+1}/5...")
            ret, frame = cap.read()
            
            if ret and frame is not None:
                print(f"   ✅ Frame capturado: {frame.shape}, média: {frame.mean():.1f}")
                break
            else:
                print(f"   ⚠️ Falhou na tentativa {i+1}")
                time.sleep(0.5)
        
        cap.release()
    else:
        print("❌ Falha na conexão")

print(f"\n🏁 Teste específico concluído!")