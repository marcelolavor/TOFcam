#!/usr/bin/env python3
"""
Teste simples de servidor de imagem para debug
"""

import cv2
import numpy as np
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import time

class SimpleImageServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            html = '''
<!DOCTYPE html>
<html>
<head><title>Teste Simples</title></head>
<body>
<h1>Teste de Imagem</h1>
<img id="img" src="/image" style="max-width: 800px;" />
<script>
setInterval(() => {
    document.getElementById('img').src = '/image?' + Date.now();
}, 1000);
</script>
</body>
</html>
            '''
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            
        elif self.path.startswith('/image'):
            # Criar imagem simples
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            # Padrão colorido
            img[:, :200] = [255, 0, 0]  # Azul
            img[:, 200:400] = [0, 255, 0]  # Verde
            img[:, 400:] = [0, 0, 255]  # Vermelho
            
            # Timestamp
            timestamp = time.strftime("%H:%M:%S")
            cv2.putText(img, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Codificar
            _, buffer = cv2.imencode('.jpg', img)
            
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(buffer.tobytes())
            
            print(f"📷 Imagem enviada: {len(buffer)} bytes")
        else:
            self.send_error(404)

if __name__ == "__main__":
    server = HTTPServer(('localhost', 8081), SimpleImageServer)
    print("🧪 Servidor de teste: http://localhost:8081")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("🛑 Servidor parado")
        server.shutdown()