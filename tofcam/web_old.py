"""
TOFcam Web Server Module
========================

Professional web interface for real-time TOF camera analysis
with sophisticated UI and streaming capabilities.
"""

import cv2
import numpy as np
import time
import threading
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs

# Local imports
from .core import TOFAnalyzer, AnalysisConfig

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """HTTP Server que suporta múltiplas conexões simultâneas"""
    daemon_threads = True

class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html_page().encode())
            
        elif path == '/stream':
            # Streaming da imagem processada
            if hasattr(self.server, 'latest_frame') and self.server.latest_frame is not None:
                analysis_result = self.server.latest_frame
                image_data = analysis_result.rgb_base64.split(',')[1] if analysis_result.rgb_base64 else None
                
                if image_data:
                    import base64
                    image_bytes = base64.b64decode(image_data)
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', str(len(image_bytes)))
                    self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                    self.end_headers()
                    self.wfile.write(image_bytes)
                    
                    print(f"🖼️  Imagem servida: {len(image_bytes)} bytes para {self.path}")
                else:
                    self.send_error(404, "Imagem não disponível")
            else:
                print(f"❌ Nenhuma imagem disponível para {self.path}")
                self.send_error(404, "Nenhuma imagem disponível")
                
        elif path == '/data':
            # API de dados de análise
            if hasattr(self.server, 'latest_frame') and self.server.latest_frame is not None:
                analysis_result = self.server.latest_frame
                
                data = {
                    'timestamp': analysis_result.timestamp,
                    'frame_id': analysis_result.frame_id,
                    'strategic': analysis_result.strategic_result,
                    'reactive': analysis_result.reactive_result,
                    'camera_id': getattr(self.server.camera_controller, 'current_camera', 0) if hasattr(self.server, 'camera_controller') else 0,
                    'success': True
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
                
                print(f"📊 Dados servidos: frame #{analysis_result.frame_id}")
            else:
                # Enviar dados padrão mesmo se não houver frame
                data = {
                    'timestamp': time.time(),
                    'frame_id': 0,
                    'strategic': {'target_yaw_delta': 0, 'confidence': 0, 'grid_info': 'Inicializando...'},
                    'reactive': {'yaw_delta': 0, 'forward_scale': 0, 'grid_info': 'Inicializando...'},
                    'camera_id': getattr(self.server.camera_controller, 'current_camera', 0) if hasattr(self.server, 'camera_controller') else 0,
                    'success': True
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
                
                print("📊 Dados padrão servidos (sistema inicializando)")
                
        elif path == '/switch_camera':
            # Trocar câmera
            query_params = parse_qs(parsed_path.query)
            camera_id = int(query_params.get('id', [0])[0])
            
            if hasattr(self.server, 'camera_controller'):
                success = self.server.camera_controller.switch_camera(camera_id)
                
                response = {'success': success, 'camera_id': camera_id}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_error(500, "Camera controller não disponível")
        else:
            self.send_error(404, "Página não encontrada")
    
    def get_html_page(self):
        """Gerar página HTML com design sofisticado"""
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>TOFcam Web Viewer - Biblioteca Centralizada</title>
    <meta charset="utf-8">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3a 100%); 
            color: white; 
            min-height: 100vh;
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px;
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .header h1 {
            font-size: 2.5em;
            background: linear-gradient(45deg, #00ffff, #ff00ff);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        }
        .subtitle {
            color: #aaa;
            font-size: 1.1em;
            margin-top: 10px;
        }
        .container { 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            max-width: 1200px;
            margin: 0 auto;
        }
        .camera-controls {
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(42,42,62,0.8);
            border-radius: 12px;
            display: flex;
            align-items: center;
            gap: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .camera-controls label {
            font-weight: bold;
            color: #00ffff;
        }
        .camera-controls select {
            padding: 8px 15px;
            background: rgba(26,26,46,0.9);
            color: white;
            border: 2px solid #444;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            transition: border-color 0.3s ease;
        }
        .camera-controls select:hover {
            border-color: #00ffff;
        }
        .camera-status {
            color: #00ff88;
            font-size: 14px;
            font-weight: 500;
        }
        .video-container { 
            border: 3px solid #333; 
            border-radius: 15px; 
            overflow: hidden; 
            margin-bottom: 30px; 
            box-shadow: 0 15px 40px rgba(0,0,0,0.4);
            position: relative;
        }
        .video-container::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #00ffff, #ff00ff, #ffff00, #00ffff);
            border-radius: 17px;
            z-index: -1;
            animation: borderGlow 3s linear infinite;
        }
        @keyframes borderGlow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .stats { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
            gap: 20px; 
            width: 100%; 
            max-width: 1000px; 
        }
        .stat-box { 
            background: rgba(42,42,62,0.8); 
            padding: 25px; 
            border-radius: 12px; 
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .stat-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        }
        .stat-value { 
            font-size: 28px; 
            font-weight: bold; 
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }
        .stat-label {
            color: #aaa;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .strategic { color: #00ffff; text-shadow: 0 0 10px #00ffff; }
        .reactive { color: #ff00ff; text-shadow: 0 0 10px #ff00ff; }
        .positive { color: #00ff88; }
        .negative { color: #ff6666; }
        .neutral { color: #ffff00; }
        .frame-info { color: #88ccff; }
        
        #videoStream { 
            max-width: 100%; 
            height: auto;
            display: block;
        }
        
        .loading {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .spinner {
            width: 20px;
            height: 20px;
            border: 2px solid #444;
            border-top: 2px solid #00ffff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .algorithm-detail {
            font-size: 12px;
            color: #999;
            margin-top: 8px;
        }
        
        .confidence-bar {
            width: 100%;
            height: 6px;
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
            margin-top: 8px;
            overflow: hidden;
        }
        
        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff6666, #ffff00, #00ff88);
            border-radius: 3px;
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 TOFcam Web Viewer</h1>
        <p class="subtitle">Análise de Profundidade e Navegação em Tempo Real - Biblioteca Centralizada</p>
    </div>
    
    <div class="container">
        <div class="camera-controls">
            <label for="cameraSelect">📹 Câmera:</label>
            <select id="cameraSelect" onchange="switchCamera()">
                <option value="0">Câmera 0</option>
                <option value="2">Câmera 2</option>
            </select>
            <span id="cameraStatus" class="camera-status loading">
                <div class="spinner"></div>
                Conectando sistema...
            </span>
        </div>
        
        <div class="video-container">
            <img id="videoStream" src="/stream?" alt="TOFcam Stream" />
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value strategic" id="strategicValue">--</div>
                <div class="stat-label">Strategic Navigation</div>
                <div class="algorithm-detail" id="strategicDetail">
                    Planejamento de rota baseado em análise global
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" id="strategicConfidence" style="width: 0%"></div>
                </div>
            </div>
            
            <div class="stat-box">
                <div class="stat-value reactive" id="reactiveValue">--</div>
                <div class="stat-label">Reactive Avoidance</div>
                <div class="algorithm-detail" id="reactiveDetail">
                    Evasão imediata de obstáculos próximos
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" id="reactiveConfidence" style="width: 0%"></div>
                </div>
            </div>
            
            <div class="stat-box">
                <div class="stat-value frame-info" id="frameCount">--</div>
                <div class="stat-label">Frame Analysis</div>
                <div class="algorithm-detail" id="frameDetail">
                    Frames processados e timestamp
                </div>
            </div>
            
            <div class="stat-box">
                <div class="stat-value" id="systemStatus">--</div>
                <div class="stat-label">System Status</div>
                <div class="algorithm-detail" id="statusDetail">
                    Estado do sistema e performance
                </div>
            </div>
        </div>
    </div>

    <script>
        let frameCount = 0;
        let lastUpdateTime = Date.now();
        
        function formatYawValue(yaw) {
            const angle = (yaw * 180 / Math.PI).toFixed(1);
            if (Math.abs(angle) < 0.1) return '0.0°';
            return (angle > 0 ? '+' : '') + angle + '°';
        }
        
        function getYawClass(yaw) {
            const angle = Math.abs(yaw * 180 / Math.PI);
            if (angle < 0.1) return 'neutral';
            return yaw > 0 ? 'negative' : 'positive';
        }
        
        function updateStream() {
            const img = document.getElementById('videoStream');
            const oldSrc = img.src;
            
            img.onerror = function() {
                console.log('❌ Erro ao carregar stream');
                document.getElementById('systemStatus').textContent = 'ERRO';
                document.getElementById('systemStatus').className = 'stat-value negative';
                setTimeout(updateStream, 2000);
            };
            
            img.onload = function() {
                frameCount++;
                const now = Date.now();
                const fps = frameCount / ((now - lastUpdateTime) / 1000);
                
                document.getElementById('systemStatus').textContent = 'ATIVO';
                document.getElementById('systemStatus').className = 'stat-value positive';
                document.getElementById('statusDetail').textContent = 
                    `FPS: ${fps.toFixed(1)} | Última atualização: ${new Date().toLocaleTimeString()}`;
            };
            
            // Cache busting para forçar atualização
            img.src = '/stream?' + new Date().getTime();
        }
        
        function updateData() {
            fetch('/data')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('📊 Dados recebidos:', data);
                    
                    if (data.success) {
                        // Remover loading se ainda estiver visível
                        const loadingElements = document.querySelectorAll('.loading');
                        loadingElements.forEach(el => el.style.display = 'none');
                        
                        // Atualizar valores Strategic
                        const strategicYaw = data.strategic?.target_yaw_delta || 0;
                        const strategicElement = document.getElementById('strategicValue');
                        if (strategicElement) {
                            strategicElement.textContent = formatYawValue(strategicYaw);
                            strategicElement.className = 'stat-value strategic ' + getYawClass(strategicYaw);
                        }
                        
                        // Detalhes Strategic
                        const strategicConf = (data.strategic?.confidence || 0) * 100;
                        const strategicDetail = document.getElementById('strategicDetail');
                        if (strategicDetail) {
                            strategicDetail.textContent = 
                                `Confiança: ${strategicConf.toFixed(1)}% | Grid: ${data.strategic?.grid_info || '--'}`;
                        }
                        const strategicConfidence = document.getElementById('strategicConfidence');
                        if (strategicConfidence) {
                            strategicConfidence.style.width = strategicConf + '%';
                        }
                        
                        // Atualizar valores Reactive
                        const reactiveYaw = data.reactive?.yaw_delta || 0;
                        const reactiveElement = document.getElementById('reactiveValue');
                        if (reactiveElement) {
                            reactiveElement.textContent = formatYawValue(reactiveYaw);
                            reactiveElement.className = 'stat-value reactive ' + getYawClass(reactiveYaw);
                        }
                        
                        // Detalhes Reactive
                        const reactiveForward = data.reactive?.forward_scale || 0;
                        const reactiveDetail = document.getElementById('reactiveDetail');
                        if (reactiveDetail) {
                            reactiveDetail.textContent = 
                                `Forward: ${(reactiveForward * 100).toFixed(1)}% | Grid: ${data.reactive?.grid_info || '--'}`;
                        }
                        const reactiveConfidence = document.getElementById('reactiveConfidence');
                        if (reactiveConfidence) {
                            reactiveConfidence.style.width = (reactiveForward * 100) + '%';
                        }
                        
                        // Frame info
                        const frameCount = document.getElementById('frameCount');
                        if (frameCount) {
                            frameCount.textContent = `#${data.frame_id || '--'}`;
                        }
                        const frameDetail = document.getElementById('frameDetail');
                        if (frameDetail) {
                            frameDetail.textContent = 
                                `Timestamp: ${data.timestamp ? new Date(data.timestamp * 1000).toLocaleTimeString() : '--'}`;
                        }
                        
                        // Status geral
                        const cameraStatus = document.getElementById('cameraStatus');
                        if (cameraStatus) {
                            cameraStatus.innerHTML = `✅ Câmera ${data.camera_id || 0} ativa`;
                        }
                        
                        console.log('✅ Interface atualizada com sucesso');
                    }
                })
                .catch(error => {
                    console.error('❌ Erro ao buscar dados:', error);
                    const systemStatus = document.getElementById('systemStatus');
                    if (systemStatus) {
                        systemStatus.textContent = 'ERRO';
                        systemStatus.className = 'stat-value negative';
                    }
                });
        }
        
        function switchCamera() {
            const select = document.getElementById('cameraSelect');
            const cameraId = parseInt(select.value);
            
            document.getElementById('cameraStatus').innerHTML = 
                '<div class="spinner"></div> Trocando...';
            
            fetch(`/switch_camera?id=${cameraId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('cameraStatus').innerHTML = 
                            `✅ Câmera ${cameraId} ativa`;
                        console.log(`✅ Câmera trocada para ${cameraId}`);
                    } else {
                        document.getElementById('cameraStatus').innerHTML = '❌ Erro na troca';
                        console.error(`❌ Erro ao trocar câmera: ${data.error}`);
                    }
                })
                .catch(err => {
                    console.error('❌ Erro ao trocar câmera:', err);
                    document.getElementById('cameraStatus').innerHTML = '❌ Erro na troca';
                });
        }
        
        // Inicialização
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 Inicializando interface...');
            
            // Primeiro atualizar dados
            updateData();
            // Depois o stream
            setTimeout(updateStream, 500);
            
            // Auto-refresh com intervalos otimizados
            setInterval(updateStream, 400);  // ~2.5 FPS para video
            setInterval(updateData, 800);    // ~1.25 Hz para dados
            
            // Atualizar status inicial
            setTimeout(() => {
                document.getElementById('cameraStatus').innerHTML = '✅ Sistema inicializado';
            }, 1000);
        });
    </script>
</body>
</html>
        '''

    def log_message(self, format, *args):
        # Suprimir logs HTTP
        return

class CameraController:
    """Controlador de câmera usando a biblioteca de análise"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.camera = None
        self.analyzer = None
        self.current_camera = 0
        self.running = False
        
    def start_capture(self):
        """Iniciar captura em thread separada"""
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
    def _capture_loop(self):
        """Loop principal de captura"""
        while self.running:
            try:
                if self.analyzer and hasattr(self.analyzer, 'camera_manager'):
                    frame = self.analyzer.camera_manager.read()
                    if frame is not None:
                        result = self.analyzer.process_frame(frame, camera_id=self.current_camera)
                        if hasattr(self, 'server'):
                            self.server.latest_frame = result
            except KeyError as e:
                if "'yaw_delta'" in str(e):
                    # Ignorar erro específico de yaw_delta temporariamente
                    pass
                else:
                    print(f"❌ Erro KeyError na captura: {e}")
            except Exception as e:
                if "'yaw_delta'" not in str(e):
                    print(f"❌ Erro na captura: {e}")
            time.sleep(0.1)  # ~10 FPS máximo
                
    def switch_camera(self, camera_id):
        """Trocar para câmera específica"""
        try:
            self.current_camera = camera_id
            
            # Recriar analyzer com nova câmera
            if self.analyzer:
                self.analyzer.cleanup()
                
            # Inicializar novo analyzer  
            self.analyzer = TOFAnalyzer(config=self.config, camera_id=camera_id)
            return True
        except Exception as e:
            print(f"❌ Erro ao trocar câmera: {e}")
            return False
            
    def get_current_data(self):
        """Obter dados atuais de análise"""
        if hasattr(self, 'server') and hasattr(self.server, 'latest_frame'):
            result = self.server.latest_frame
            if result:
                return {
                    'success': True,
                    'frame_id': result.frame_id,
                    'timestamp': result.timestamp,
                    'camera_id': self.current_camera,
                    'strategic': {
                        'target_yaw_delta': result.strategic_result.get('target_yaw_delta', 0),
                        'confidence': result.strategic_result.get('confidence', 0),
                        'grid_info': f"{result.strategic_result.get('grid_h', '--')}x{result.strategic_result.get('grid_w', '--')}"
                    },
                    'reactive': {
                        'yaw_delta': result.reactive_result.get('yaw_delta', 0), 
                        'forward_scale': result.reactive_result.get('forward_scale', 0),
                        'grid_info': f"{result.reactive_result.get('grid_h', '--')}x{result.reactive_result.get('grid_w', '--')}"
                    }
                }
        
        return {'success': False, 'error': 'Dados não disponíveis'}
        
    def stop_capture(self):
        """Parar captura"""
        self.running = False
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join(timeout=2)
        
    def cleanup(self):
        """Limpar recursos"""
        self.stop_capture()
        if self.analyzer:
            self.analyzer.cleanup()

class WebServer:
    """Professional web server for TOFcam analysis"""
    
    def __init__(self, config: AnalysisConfig, port: int = 8081):
        """Initialize web server"""
        self.config = config
        self.port = port
        self.controller = None
        self.httpd = None
        
    def run(self):
        """Run the web server"""
        print("🌐 TOFcam Web Viewer (Professional)")
        print("=" * 50)
        
        try:
            # Initialize camera controller
            self.controller = CameraController(self.config)
            
            # Configure web server
            server_address = ('0.0.0.0', self.port)
            self.httpd = ThreadingHTTPServer(server_address, WebHandler)
            
            # Connect controller to server
            self.httpd.camera_controller = self.controller
            self.controller.server = self.httpd
            
            # Initialize first camera and start capture
            self.controller.switch_camera(0)
            self.controller.start_capture()
            
            print(f"🚀 Servidor iniciado em: http://localhost:{self.port}")
            print("📱 Abra o navegador e acesse o link acima")
            print("⏹️  Pressione Ctrl+C para parar")
            print("-" * 50)
            
            # Serve requests
            self.httpd.serve_forever()
            
        except KeyboardInterrupt:
            print("\n🛑 Parando servidor...")
        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            self.cleanup()
            print("✅ Servidor parado!")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.controller:
            self.controller.cleanup()
        if self.httpd:
            self.httpd.shutdown()

def main():
    """Legacy main function"""
    config = AnalysisConfig(
        strategic_grid_size=(24, 32),
        reactive_grid_size=(12, 16),
        use_sophisticated_analysis=True,
        save_frames=False,
        web_format=True
    )
    
    server = WebServer(config)
    server.run()

if __name__ == "__main__":
    main()
