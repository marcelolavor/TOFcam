#!/usr/bin/env python3
"""
Demo: Seleção de Câmeras
Interface web simplificada para testar diferentes câmeras
"""

import cv2
import numpy as np
import base64
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Servidor HTTP com threading."""
    allow_reuse_address = True

class SimpleTOFcamViewer:
    """Visualizador simplificado."""
    
    def __init__(self):
        self.camera_source = None
        self.is_running = False
        self.current_frame = None
        self.current_data = {}
        self.current_camera = 0
        self.available_cameras = []
        
    def find_available_cameras(self):
        """Detectar câmeras disponíveis."""
        cameras = []
        print("🔍 Testando câmeras...")
        for i in range(5):  # Testar apenas 5 para ser mais rápido
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cameras.append(i)
                print(f"✅ Câmera {i} detectada")
                cap.release()
        self.available_cameras = cameras
        return cameras
        
    def initialize_components(self):
        """Inicializar componentes."""
        self.find_available_cameras()
        
        if not self.available_cameras:
            raise Exception("Nenhuma câmera encontrada!")
            
        print(f"📹 Usando câmera {self.current_camera}")
        self.camera_source = cv2.VideoCapture(self.current_camera)
        
        if not self.camera_source.isOpened():
            raise Exception(f"Falha ao abrir câmera {self.current_camera}")
            
        print("✅ Componentes prontos!")
        
    def switch_camera(self, camera_id):
        """Trocar câmera."""
        if camera_id not in self.available_cameras:
            return False
            
        print(f"📹 Trocando para câmera {camera_id}...")
        
        # Parar captura
        was_running = self.is_running
        if was_running:
            self.stop_capture()
            
        # Fechar câmera atual
        if self.camera_source:
            self.camera_source.release()
            
        # Abrir nova câmera
        self.camera_source = cv2.VideoCapture(camera_id)
        if self.camera_source.isOpened():
            self.current_camera = camera_id
            
            # Reiniciar captura
            if was_running:
                self.start_capture()
                
            print(f"✅ Câmera {camera_id} ativada!")
            return True
        else:
            print(f"❌ Falha ao abrir câmera {camera_id}")
            return False
    
    def process_frame(self):
        """Processar frame simples."""
        if not self.camera_source or not self.camera_source.isOpened():
            return None
            
        ret, frame = self.camera_source.read()
        if not ret:
            return None
            
        # Apenas redimensionar
        frame = cv2.resize(frame, (640, 480))
        
        # Adicionar informações
        cv2.putText(frame, f"Camera {self.current_camera}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, time.strftime("%H:%M:%S"), (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return {
            'combined': frame,
            'camera': self.current_camera,
            'timestamp': time.time()
        }
    
    def capture_loop(self):
        """Loop de captura."""
        frame_count = 0
        while self.is_running:
            try:
                result = self.process_frame()
                if result:
                    # Converter para base64
                    _, buffer = cv2.imencode('.jpg', result['combined'], [cv2.IMWRITE_JPEG_QUALITY, 70])
                    img_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    self.current_frame = img_base64
                    self.current_data = {
                        'camera': result['camera'],
                        'frame_count': frame_count,
                        'timestamp': result['timestamp']
                    }
                    
                    frame_count += 1
                    if frame_count % 50 == 0:
                        print(f"📊 Frame {frame_count} - Câmera {self.current_camera}")
                        
                time.sleep(0.1)  # 10 FPS
                
            except Exception as e:
                print(f"❌ Erro: {e}")
                time.sleep(1)
    
    def start_capture(self):
        """Iniciar captura."""
        self.is_running = True
        self.capture_thread = threading.Thread(target=self.capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
    
    def stop_capture(self):
        """Parar captura."""
        self.is_running = False
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join(timeout=2)

# Instância global
viewer = SimpleTOFcamViewer()

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_html()
        elif self.path.startswith('/stream'):
            self.serve_stream()
        elif self.path == '/data':
            self.serve_data()
        elif self.path == '/cameras':
            self.serve_cameras()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/switch_camera':
            self.handle_camera_switch()
        else:
            self.send_error(404)
    
    def serve_html(self):
        html = '''<!DOCTYPE html>
<html>
<head>
    <title>TOFcam - Seletor de Câmera</title>
    <style>
        body { font-family: Arial; background: #1a1a1a; color: white; margin: 0; padding: 20px; }
        .container { display: flex; flex-direction: column; align-items: center; }
        .camera-controls { 
            margin: 20px; padding: 20px; background: #2a2a2a; 
            border-radius: 10px; display: flex; align-items: center; gap: 15px; 
        }
        select { padding: 8px; background: #1a1a1a; color: white; border: 1px solid #555; border-radius: 5px; }
        #status { color: #00ff00; }
        img { max-width: 800px; border: 2px solid #333; border-radius: 10px; }
        .stats { display: flex; gap: 20px; margin: 20px; }
        .stat-box { padding: 15px; background: #2a2a2a; border-radius: 8px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 TOFcam - Teste de Câmeras</h1>
        
        <div class="camera-controls">
            <label>📹 Câmera:</label>
            <select id="cameraSelect" onchange="switchCamera()"></select>
            <span id="status">Carregando...</span>
        </div>
        
        <img id="videoStream" src="" alt="Camera Stream" />
        
        <div class="stats">
            <div class="stat-box">
                <div id="frameCount">--</div>
                <div>Frames</div>
            </div>
            <div class="stat-box">
                <div id="currentCamera">--</div>
                <div>Câmera Atual</div>
            </div>
        </div>
    </div>

    <script>
        function updateStream() {
            const img = document.getElementById('videoStream');
            img.src = '/stream?' + Date.now();
        }
        
        function loadCameras() {
            fetch('/cameras')
                .then(response => response.json())
                .then(cameras => {
                    const select = document.getElementById('cameraSelect');
                    select.innerHTML = '';
                    cameras.forEach(cam => {
                        const option = document.createElement('option');
                        option.value = cam.id;
                        option.textContent = `Câmera ${cam.id}`;
                        if (cam.active) option.selected = true;
                        select.appendChild(option);
                    });
                    
                    const active = cameras.find(cam => cam.active);
                    document.getElementById('status').textContent = `Ativa: ${active ? active.id : 'N/A'}`;
                })
                .catch(err => {
                    console.error('Erro:', err);
                    document.getElementById('status').textContent = 'Erro';
                });
        }
        
        function switchCamera() {
            const select = document.getElementById('cameraSelect');
            const cameraId = parseInt(select.value);
            
            document.getElementById('status').textContent = 'Trocando...';
            
            fetch('/switch_camera', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({camera_id: cameraId})
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    document.getElementById('status').textContent = `Ativa: ${cameraId}`;
                } else {
                    document.getElementById('status').textContent = 'Erro';
                }
            });
        }
        
        function updateData() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('frameCount').textContent = data.frame_count || '--';
                    document.getElementById('currentCamera').textContent = data.camera || '--';
                });
        }
        
        // Inicializar
        setInterval(updateStream, 200);
        setInterval(updateData, 1000);
        loadCameras();
        updateStream();
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_stream(self):
        if viewer.current_frame:
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            img_data = base64.b64decode(viewer.current_frame)
            self.wfile.write(img_data)
        else:
            self.send_error(503)
    
    def serve_data(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        data = viewer.current_data if viewer.current_data else {}
        self.wfile.write(json.dumps(data).encode())
    
    def serve_cameras(self):
        cameras_data = []
        for cam_id in viewer.available_cameras:
            cameras_data.append({
                'id': cam_id,
                'active': cam_id == viewer.current_camera
            })
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(cameras_data).encode())
    
    def handle_camera_switch(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            camera_id = data.get('camera_id')
            
            success = viewer.switch_camera(camera_id)
            response = {'success': success}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            response = {'success': False, 'error': str(e)}
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        pass

def main():
    try:
        viewer.initialize_components()
        viewer.start_capture()
        
        server = ThreadedHTTPServer(('localhost', 8081), RequestHandler)
        print(f"🚀 Servidor com seletor de câmera: http://localhost:8081")
        print(f"📹 Câmeras disponíveis: {viewer.available_cameras}")
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Parando...")
        viewer.stop_capture()
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()