#!/usr/bin/env python3
"""
Teste das câmeras USB2.0
"""

import cv2
import time

print("🔍 Testando câmeras USB2.0...")

for cam_id in [2, 3]:
    print(f"\n📹 Testando /dev/video{cam_id}...")
    
    cap = cv2.VideoCapture(cam_id)
    
    if cap.isOpened():
        print("✅ Conexão estabelecida")
        
        # Configurar propriedades
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduzir buffer
        
        # Descartar alguns frames iniciais
        for i in range(3):
            ret, frame = cap.read()
            time.sleep(0.1)
        
        # Tentar ler frame final
        ret, frame = cap.read()
        
        if ret and frame is not None:
            print(f"   ✅ Frame válido: {frame.shape}, média: {frame.mean():.1f}")
        else:
            print(f"   ❌ Sem frame válido")
        
        cap.release()
    else:
        print("❌ Falha na conexão")

print(f"\n🏁 Teste USB2.0 concluído!")