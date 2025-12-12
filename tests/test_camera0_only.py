#!/usr/bin/env python3
"""
Teste simples apenas com câmera 0 para verificar o sistema funcionando
"""

import cv2
import numpy as np
import base64
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import sys
import os

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Tentar importar módulos com fallback
USE_DEPTH_ESTIMATION = True
USE_MAPPING = True

try:
    from camera import CameraSource
    print("✅ Camera carregado")
except ImportError as e:
    print(f"⚠️ Camera não disponível: {e}")
    CameraSource = None

try:
    from depth_estimator import MidasDepthEstimator
    print("✅ Depth estimator carregado")
except ImportError as e:
    print(f"⚠️ Depth estimator não disponível: {e}")
    MidasDepthEstimator = None
    USE_DEPTH_ESTIMATION = False

try:
    from tofcam.nav import StrategicPlanner, ReactiveAvoider
    print("✅ Mappers carregados")
except ImportError as e:
    print(f"⚠️ Mapping não disponível: {e}")
    StrategicPlanner = ReactiveAvoider = None
    USE_MAPPING = False

try:
    from view import depth_to_color, draw_yaw_arrow
    print("✅ View carregado")
except ImportError as e:
    print(f"⚠️ View não disponível: {e}")
    depth_to_color = draw_yaw_arrow = None

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Servidor HTTP que permite múltiplas conexões."""
    allow_reuse_address = True

class TOFcamWebViewer:
    def __init__(self, port=8080):
        self.port = port
        self.current_camera = 0
        self.available_cameras = [0]  # Força apenas câmera 0
        self.camera_source = None
        self.is_running = False
        self.capture_thread = None
        self.current_image = None
        self.current_data = None
        self.server = None
        
        # Componentes de análise
        self.depth_estimator = None
        self.strategic = None
        self.reactive = None
        
        self.initialize_components()
        
    def initialize_components(self):
        """Inicializar componentes do sistema."""
        print("🔍 Utilizando apenas câmera 0...")
        print(f"📹 Câmeras disponíveis: {self.available_cameras}")
        
        print(f"📹 Inicializando câmera {self.current_camera}...")
        self.switch_camera(self.current_camera)
        
        # Inicializar componentes de análise
        if USE_DEPTH_ESTIMATION and MidasDepthEstimator:
            try:
                print("📡 Inicializando estimador de profundidade...")
                self.depth_estimator = MidasDepthEstimator()
                print("✅ Estimador de profundidade carregado")
            except Exception as e:
                print(f"⚠️ Erro ao carregar estimador: {e}")
                self.depth_estimator = None
        
        if USE_MAPPING and StrategicPlanner and ReactiveAvoider:
            try:
                print("🧭 Inicializando algoritmos de navegação...")
                self.strategic = StrategicPlanner()
                self.reactive = ReactiveAvoider()
                print("✅ Algoritmos de navegação carregados")
            except Exception as e:
                print(f"⚠️ Erro ao carregar algoritmos: {e}")
                self.strategic = self.reactive = None
    
    def switch_camera(self, camera_id):
        """Trocar para uma câmera específica."""
        if camera_id not in self.available_cameras:
            print(f"⚠️ Câmera {camera_id} não disponível")
            return False
            
        # Parar captura atual se estiver rodando
        if self.camera_source:
            try:
                if hasattr(self.camera_source, 'release'):
                    self.camera_source.release()
                else:
                    self.camera_source.close()
            except:
                pass
                
        # Tentar inicializar nova câmera
        try:
            # Usar OpenCV diretamente
            self.camera_source = cv2.VideoCapture(camera_id)
            if not self.camera_source.isOpened():
                print(f"❌ Erro ao abrir câmera {camera_id}")
                return False
                
            self.camera_source.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera_source.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera_source.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
            self.current_camera = camera_id
            print(f"✅ Câmera {camera_id} ativada")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao trocar para câmera {camera_id}: {e}")
            return False
        
    def process_frame(self):
        """Processar um frame e gerar dados."""
        if not self.camera_source:
            return None
            
        # Ler frame com múltiplas tentativas
        frame = None
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                # Usar OpenCV diretamente
                ret, frame = self.camera_source.read()
                if not ret:
                    frame = None
                
                # Se conseguiu um frame válido, usar
                if frame is not None and frame.size > 0:
                    break
                elif attempt < max_attempts - 1:
                    time.sleep(0.1)
            except Exception as e:
                print(f"⚠️ Erro na captura tentativa {attempt+1}: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(0.1)
                    
        if frame is None or frame.size == 0:
            print("⚠️ Nenhum frame capturado")
            return None
            
        # Redimensionar para tamanho padrão
        frame = cv2.resize(frame, (640, 480))
        
        # Implementar análise de profundidade simples sem MiDaS
        # Converter para escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Aplicar blur para reduzir ruído
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Criar mapa de profundidade baseado em luminosidade e gradientes
        # Pixels mais escuros = mais distantes, pixels mais claros = mais próximos
        depth_map = 255 - blurred
        
        # Adicionar informação de gradiente para detectar bordas/obstáculos
        grad_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Combinar luminosidade com gradiente
        depth_map = (depth_map * 0.7 + gradient_magnitude * 0.3).astype(np.uint8)
        
        # Normalizar
        depth_normalized = depth_map.astype(np.float32) / 255.0
        
        # Criar visualização colorida da profundidade
        depth_color = cv2.applyColorMap(depth_map, cv2.COLORMAP_JET)
        
        # Processar algoritmos de navegação
        h, w = depth_normalized.shape
        
        # Criar grid 3x3 para análise de zonas
        zone_grid = []
        for i in range(3):
            row = []
            for j in range(3):
                y1, y2 = i * h//3, (i+1) * h//3
                x1, x2 = j * w//3, (j+1) * w//3
                zone_depth = np.mean(depth_normalized[y1:y2, x1:x2])
                row.append(float(zone_depth))
            zone_grid.append(row)
        
        # Algoritmo Strategic simples
        left_avg = np.mean([zone_grid[i][0] for i in range(3)])
        right_avg = np.mean([zone_grid[i][2] for i in range(3)])
        center_avg = np.mean([zone_grid[i][1] for i in range(3)])
        
        # Calcular tendência direcional
        diff = right_avg - left_avg
        strategic_direction = diff * 1.5  # Amplificar diferenças
        
        # Algoritmo Reactive simples 
        front_left = zone_grid[0][0]
        front_center = zone_grid[0][1] 
        front_right = zone_grid[0][2]
        
        # Detectar padrões de obstáculos ou diferenças
        if front_center < 0.4:  # Obstáculo frontal
            if front_left > front_right:
                reactive_direction = -1.0  # Vire à esquerda
            else:
                reactive_direction = 1.0   # Vire à direita
        elif front_left < 0.5:  # Obstáculo à esquerda
            reactive_direction = 0.8
        elif front_right < 0.5:  # Obstáculo à direita
            reactive_direction = -0.8
        elif abs(front_left - front_right) > 0.1:  # Assimetria detectada
            if front_left > front_right:
                reactive_direction = -0.4  # Leve tendência à esquerda
            else:
                reactive_direction = 0.4   # Leve tendência à direita
        else:
            reactive_direction = 0.0
        
        # Criar visualização combinada com análises
        # Redimensionar imagens para 320x240 para melhor performance
        small_frame = cv2.resize(frame, (320, 240))
        small_depth = cv2.resize(depth_color, (320, 240))
        
        # Criar versões com setas de direção
        strategic_vis = small_depth.copy()
        reactive_vis = small_depth.copy()
        
        # Desenhar setas indicando direção
        center_x, center_y = 160, 120
        arrow_length = 60
        
        # Seta Strategic (azul ciano)
        strategic_angle = strategic_direction * 45  # Converter para graus
        end_x = int(center_x + arrow_length * np.sin(np.radians(strategic_angle)))
        end_y = int(center_y - arrow_length * np.cos(np.radians(strategic_angle)))
        cv2.arrowedLine(strategic_vis, (center_x, center_y), (end_x, end_y), (255, 255, 0), 3, tipLength=0.3)
        
        # Seta Reactive (magenta)
        reactive_angle = reactive_direction * 45
        end_x = int(center_x + arrow_length * np.sin(np.radians(reactive_angle)))
        end_y = int(center_y - arrow_length * np.cos(np.radians(reactive_angle)))
        cv2.arrowedLine(reactive_vis, (center_x, center_y), (end_x, end_y), (255, 0, 255), 3, tipLength=0.3)
        
        # Combinar em grade 2x2
        top_row = np.hstack([small_frame, small_depth])
        bottom_row = np.hstack([strategic_vis, reactive_vis])
        combined = np.vstack([top_row, bottom_row])
        
        # Adicionar labels
        cv2.putText(combined, "ORIGINAL", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(combined, "DEPTH MAP", (330, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(combined, f"STRATEGIC: {strategic_direction:+.2f}", (10, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        cv2.putText(combined, f"REACTIVE: {reactive_direction:+.2f}", (330, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
        
        # Adicionar informação da câmera e timestamp
        cv2.putText(combined, f"Camera {self.current_camera}", (10, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        cv2.putText(combined, time.strftime("%H:%M:%S"), (10, 310), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return {
            'combined': combined,
            'strategic': float(strategic_direction),
            'reactive': float(reactive_direction),
            'timestamp': time.time(),
            'zone_analysis': zone_grid
        }
    
    def capture_loop(self):
        """Loop de captura contínua."""
        frame_count = 0
        while self.is_running:
            try:
                result = self.process_frame()
                if result:
                    # Converter para base64 com menor qualidade
                    _, buffer = cv2.imencode('.jpg', result['combined'], [cv2.IMWRITE_JPEG_QUALITY, 70])
                    base64_image = base64.b64encode(buffer).decode('utf-8')
                    
                    self.current_image = base64_image
                    self.current_data = {
                        'image': base64_image,
                        'strategic': result['strategic'],
                        'reactive': result['reactive'],
                        'timestamp': result['timestamp'],
                        'camera': self.current_camera,
                        'frame_count': frame_count
                    }
                    frame_count += 1
                else:
                    print("❌ Nenhuma imagem disponível")
                    
            except Exception as e:
                print(f"❌ Erro no processamento: {e}")
                import traceback
                traceback.print_exc()
                
            time.sleep(0.1)  # 10 FPS aproximadamente
    
    def start_capture(self):
        """Iniciar captura de vídeo."""
        if self.is_running:
            return
            
        self.is_running = True
        self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.capture_thread.start()
        print("✅ Captura iniciada")
    
    def stop_capture(self):
        """Parar captura de vídeo."""
        self.is_running = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)
        print("✅ Captura parada")
    
    def get_status(self):
        """Obter status do sistema."""
        return {
            'available_cameras': self.available_cameras,
            'current_camera': self.current_camera,
            'is_running': self.is_running,
            'has_depth_estimator': self.depth_estimator is not None,
            'has_mapping': (self.strategic is not None and self.reactive is not None)
        }

class WebRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suprimir logs
    
    def do_GET(self):
        if self.path == '/':
            self.serve_html()
        elif self.path == '/stream':
            self.serve_stream()
        elif self.path == '/status':
            self.serve_status()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/switch_camera':
            self.handle_camera_switch()
        else:
            self.send_error(404)
    
    def serve_html(self):
        html_content = """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>TOFcam Web Viewer (Camera 0 Only)</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #1a1a1a;
                    color: #ffffff;
                }
                .header {
                    text-align: center;
                    margin-bottom: 20px;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                #video-container {
                    position: relative;
                    margin-bottom: 20px;
                }
                #camera-image {
                    max-width: 640px;
                    width: 100%;
                    height: auto;
                    border: 2px solid #444;
                    border-radius: 8px;
                }
                .controls {
                    margin: 20px 0;
                    text-align: center;
                }
                .status-panel {
                    background: #333;
                    padding: 15px;
                    border-radius: 8px;
                    margin-top: 20px;
                    max-width: 600px;
                    width: 100%;
                }
                .data-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 10px;
                    margin-top: 10px;
                }
                .data-item {
                    background: #444;
                    padding: 10px;
                    border-radius: 4px;
                    text-align: center;
                }
                .strategic { border-left: 4px solid #00ffff; }
                .reactive { border-left: 4px solid #ff00ff; }
                .camera { border-left: 4px solid #00ff00; }
                .error {
                    color: #ff6b6b;
                    text-align: center;
                    margin: 20px 0;
                }
                .loading {
                    color: #ffd93d;
                    text-align: center;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌐 TOFcam Web Viewer - Camera 0 Only</h1>
                <p>Visualização em tempo real com análise de navegação</p>
            </div>
            
            <div class="container">
                <div id="video-container">
                    <img id="camera-image" src="" alt="Camera feed will appear here">
                </div>
                
                <div class="controls">
                    <p>Sistema funcionando apenas com câmera 0</p>
                </div>
                
                <div class="status-panel">
                    <h3>📊 Status do Sistema</h3>
                    <div class="data-grid">
                        <div class="data-item camera">
                            <strong>Câmera</strong><br>
                            <span id="current-camera">-</span>
                        </div>
                        <div class="data-item strategic">
                            <strong>Strategic</strong><br>
                            <span id="strategic-value">-</span>
                        </div>
                        <div class="data-item reactive">
                            <strong>Reactive</strong><br>
                            <span id="reactive-value">-</span>
                        </div>
                        <div class="data-item">
                            <strong>FPS</strong><br>
                            <span id="fps-value">-</span>
                        </div>
                        <div class="data-item">
                            <strong>Timestamp</strong><br>
                            <span id="timestamp-value">-</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                let lastFrameTime = 0;
                let frameCount = 0;
                let lastFpsUpdate = Date.now();
                
                function updateStream() {
                    fetch('/stream')
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('Network response was not ok');
                            }
                            return response.json();
                        })
                        .then(data => {
                            if (data.image) {
                                document.getElementById('camera-image').src = 'data:image/jpeg;base64,' + data.image;
                                
                                // Atualizar dados
                                document.getElementById('current-camera').textContent = data.camera || '-';
                                document.getElementById('strategic-value').textContent = data.strategic ? data.strategic.toFixed(2) : '-';
                                document.getElementById('reactive-value').textContent = data.reactive ? data.reactive.toFixed(2) : '-';
                                document.getElementById('timestamp-value').textContent = new Date(data.timestamp * 1000).toLocaleTimeString();
                                
                                // Calcular FPS
                                frameCount++;
                                const now = Date.now();
                                if (now - lastFpsUpdate >= 1000) {
                                    const fps = frameCount / ((now - lastFpsUpdate) / 1000);
                                    document.getElementById('fps-value').textContent = fps.toFixed(1);
                                    frameCount = 0;
                                    lastFpsUpdate = now;
                                }
                                
                                // Limpar mensagens de erro
                                const errorDiv = document.querySelector('.error');
                                if (errorDiv) errorDiv.remove();
                                const loadingDiv = document.querySelector('.loading');
                                if (loadingDiv) loadingDiv.remove();
                            }
                        })
                        .catch(error => {
                            console.error('Erro:', error);
                            // Mostrar apenas na primeira vez ou a cada 30 segundos
                            if (!document.querySelector('.error')) {
                                const errorDiv = document.createElement('div');
                                errorDiv.className = 'error';
                                errorDiv.textContent = '❌ Erro ao carregar stream: ' + error.message;
                                document.querySelector('.container').appendChild(errorDiv);
                            }
                        });
                }
                
                // Iniciar atualizações
                setTimeout(updateStream, 1000); // Primeira atualização em 1s
                setInterval(updateStream, 100); // Atualizações a cada 100ms (10 FPS)
                
                // Mostrar loading inicial
                const loadingDiv = document.createElement('div');
                loadingDiv.className = 'loading';
                loadingDiv.textContent = '⏳ Carregando câmera...';
                document.querySelector('.container').appendChild(loadingDiv);
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def serve_stream(self):
        viewer = self.server.viewer
        
        try:
            if viewer.current_data:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.end_headers()
                
                self.wfile.write(json.dumps(viewer.current_data).encode('utf-8'))
            else:
                self.send_response(204)  # No content
                self.end_headers()
                
        except Exception as e:
            print(f"❌ Erro ao servir stream: {e}")
            self.send_response(500)
            self.end_headers()
    
    def serve_status(self):
        viewer = self.server.viewer
        
        try:
            status = viewer.get_status()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            self.wfile.write(json.dumps(status).encode('utf-8'))
            
        except Exception as e:
            print(f"❌ Erro ao servir status: {e}")
            self.send_response(500)
            self.end_headers()

def main():
    print("✅ Camera carregado")
    print("✅ Depth estimator carregado") 
    print("✅ Mappers carregados")
    print("✅ View carregado")
    print("🌐 TOFcam Web Viewer - Camera 0 Only")
    print("========================================")
    
    try:
        # Criar e configurar servidor
        viewer = TOFcamWebViewer(port=8080)
        
        server = ThreadingHTTPServer(('localhost', 8080), WebRequestHandler)
        server.viewer = viewer
        
        # Iniciar captura
        viewer.start_capture()
        
        print(f"🚀 Servidor iniciado em http://localhost:8080")
        print("📋 Pressione Ctrl+C para parar")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Parando servidor...")
            
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        try:
            viewer.stop_capture()
            server.socket.close()
            print("✅ Servidor parado!")
        except:
            pass

if __name__ == "__main__":
    main()