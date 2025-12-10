#!/usr/bin/env python3
"""
Visualizador web para TOFcam - Alternativa para VS Code
Cria um servidor web local para visualizar imagens em tempo real
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
    from ..camera import CameraSource
    print("✅ Camera carregado")
except ImportError:
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from camera import CameraSource
        print("✅ Camera carregado")
    except ImportError as e:
        print(f"⚠️ Camera não disponível: {e}")
        CameraSource = None

try:
    from ..depth_estimator import MidasDepthEstimator
    print("✅ Depth estimator carregado")
except ImportError:
    try:
        from depth_estimator import MidasDepthEstimator
        print("✅ Depth estimator carregado")
    except ImportError as e:
        print(f"⚠️ Depth estimator não disponível: {e}")
        MidasDepthEstimator = None
        USE_DEPTH_ESTIMATION = False

try:
    from ..mapping import StrategicPlanner, ReactiveAvoider
    print("✅ Mappers carregados")
except ImportError:
    try:
        from mapping import StrategicPlanner, ReactiveAvoider
        print("✅ Mappers carregados")
    except ImportError as e:
        print(f"⚠️ Mapping não disponível: {e}")
        StrategicPlanner = ReactiveAvoider = None
        USE_MAPPING = False

try:
    from ..view import depth_to_color, draw_yaw_arrow
    print("✅ View carregado")
except ImportError:
    try:
        from view import depth_to_color, draw_yaw_arrow
        print("✅ View carregado")
    except ImportError as e:
        print(f"⚠️ View não disponível: {e}")
        def depth_to_color(depth):
            # Fallback: converter depth para colormap
            import cv2
            d = (depth * 255).astype(np.uint8)
            return cv2.applyColorMap(d, cv2.COLORMAP_JET)
        def draw_yaw_arrow(img, angle):
            return img

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Servidor HTTP com threading para múltiplas conexões."""
    allow_reuse_address = True

class TOFcamWebViewer:
    """Visualizador web para TOFcam."""
    
    def __init__(self):
        self.camera_source = None
        self.depth_estimator = None
        self.strategic = None
        self.reactive = None
        self.is_running = False
        self.current_frame = None
        self.current_data = {}
        self.current_camera = 0
        self.available_cameras = []
        
    def find_available_cameras(self):
        """Detectar câmeras disponíveis."""
        cameras = []
        print("🔍 Testando câmeras disponíveis...")
        
        # Testar câmeras de 0 a 4 com método simples que funcionava antes
        for i in range(5):  
            cap = cv2.VideoCapture(i)
            
            if cap.isOpened():
                # Configurar propriedades básicas apenas
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # Tentar ler um frame para validar
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    cameras.append(i)
                    print(f"✅ Câmera {i} disponível - resolução: {frame.shape}")
                else:
                    print(f"⚠️ Câmera {i} abriu mas sem frame válido")
                    
                cap.release()
                
        self.available_cameras = cameras
        print(f"📹 Total de câmeras funcionais: {len(cameras)} - {cameras}")
        return cameras
        print(f"📹 Total de câmeras funcionais: {len(cameras)} - {cameras}")
        return cameras
        
    def initialize_components(self):
        """Inicializar componentes do sistema."""
        print("🔍 Detectando câmeras disponíveis...")
        self.find_available_cameras()
        print(f"📹 Câmeras encontradas: {self.available_cameras}")
        
        if not self.available_cameras:
            raise Exception("Nenhuma câmera encontrada!")
            
        print(f"📹 Inicializando câmera {self.current_camera}...")
        
        if CameraSource:
            self.camera_source = CameraSource(self.current_camera)
            if not self.camera_source.open():
                raise Exception(f"Falha ao abrir câmera {self.current_camera}")
        else:
            # Fallback para OpenCV direto
            self.camera_source = cv2.VideoCapture(self.current_camera)
            if not self.camera_source.isOpened():
                raise Exception(f"Falha ao abrir câmera {self.current_camera}")
                
        # Inicializar depth estimator se disponível
        if USE_DEPTH_ESTIMATION and MidasDepthEstimator:
            print("🧠 Carregando MiDaS...")
            try:
                self.depth_estimator = MidasDepthEstimator()
                print("✅ MiDaS carregado!")
            except Exception as e:
                print(f"⚠️ Erro no MiDaS: {e}")
                self.depth_estimator = None
        else:
            print("⚠️ MiDaS desabilitado")
            
        # Inicializar algoritmos se disponível  
        if USE_MAPPING and StrategicPlanner and ReactiveAvoider:
            print("🗺️ Inicializando algoritmos...")
            self.strategic = StrategicPlanner()
            self.reactive = ReactiveAvoider()
            print("✅ Algoritmos carregados!")
        else:
            print("⚠️ Algoritmos desabilitados")
            
        # Inicializar ZoneMapper para análise sofisticada (igual ao main_analyzer)
        try:
            from mapping import ZoneMapper
            # Usar as mesmas configurações do main_analyzer.py
            self.strategic_mapper = ZoneMapper(
                grid_h=24, grid_w=32,
                warn_threshold=0.35, emergency_threshold=0.20,
                roi=(0.10, 1.00, 0.10, 0.90)
            )
            self.reactive_mapper = ZoneMapper(
                grid_h=12, grid_w=16,
                warn_threshold=0.25, emergency_threshold=0.12,
                roi=(0.50, 1.00, 0.25, 0.75)
            )
            print("✅ ZoneMappers carregados com configuração completa!")
        except Exception as e:
            print(f"⚠️ ZoneMappers não disponíveis: {e}")
            self.strategic_mapper = None
            self.reactive_mapper = None
        
        print("✅ Componentes prontos!")
        
    def switch_camera(self, camera_id):
        """Trocar para uma câmera diferente."""
        if camera_id not in self.available_cameras:
            return False
            
        print(f"📹 Trocando para câmera {camera_id}...")
        
        # Parar captura atual
        was_running = self.is_running
        if was_running:
            self.stop_capture()
            
        # Fechar câmera atual
        if self.camera_source:
            if CameraSource and hasattr(self.camera_source, 'cap'):
                self.camera_source.cap.release()
            elif hasattr(self.camera_source, 'release'):
                self.camera_source.release()
            
        # Abrir nova câmera
        if CameraSource:
            self.camera_source = CameraSource(camera_id)
            success = self.camera_source.open()
        else:
            self.camera_source = cv2.VideoCapture(camera_id)
            success = self.camera_source.isOpened()
            
            # Configurar propriedades específicas para câmeras USB
            if success and camera_id >= 2:
                print(f"   🔧 Configurando câmera USB {camera_id}...")
                self.camera_source.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera_source.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.camera_source.set(cv2.CAP_PROP_FPS, 15)  # FPS mais baixo para USB
                self.camera_source.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Buffer mínimo
                
                # Descartar alguns frames iniciais para estabilizar
                for i in range(3):
                    ret, _ = self.camera_source.read()
                    if ret:
                        break
                    import time
                    time.sleep(0.1)
            
        if success:
            self.current_camera = camera_id
            
            # Reiniciar captura se estava rodando
            if was_running:
                self.start_capture()
                
            print(f"✅ Câmera {camera_id} ativada!")
            return True
        else:
            print(f"❌ Falha ao abrir câmera {camera_id}")
            return False
        
    def _simple_analysis_fallback(self, depth_normalized):
        """Análise simples 3x3 como fallback."""
        h, w = depth_normalized.shape
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
        diff = right_avg - left_avg
        strategic_direction = diff * 1.5
        
        # Algoritmo Reactive simples 
        front_left = zone_grid[0][0]
        front_center = zone_grid[0][1] 
        front_right = zone_grid[0][2]
        
        if front_center < 0.4:
            if front_left > front_right:
                reactive_direction = -1.0
            else:
                reactive_direction = 1.0
        elif front_left < 0.5:
            reactive_direction = 0.8
        elif front_right < 0.5:
            reactive_direction = -0.8
        elif abs(front_left - front_right) > 0.1:
            if front_left > front_right:
                reactive_direction = -0.4
            else:
                reactive_direction = 0.4
        else:
            reactive_direction = 0.0
            
        return strategic_direction, reactive_direction

    def process_frame(self):
        """Processar um frame e gerar dados."""
        if not self.camera_source:
            return None
            
        # Ler frame com múltiplas tentativas para câmeras USB problemáticas
        frame = None
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                if CameraSource and hasattr(self.camera_source, 'read'):
                    frame = self.camera_source.read()
                else:
                    ret, frame = self.camera_source.read()
                    if not ret:
                        frame = None
                
                # Se conseguiu um frame válido, usar
                if frame is not None and frame.size > 0:
                    break
                elif attempt < max_attempts - 1:
                    # Para câmeras USB com timeout, aguardar um pouco
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
        
        # Análise de profundidade com MiDaS
        if self.depth_estimator:
            try:
                # Usar MiDaS para análise precisa (igual ao main_analyzer.py)
                depth_map = self.depth_estimator.estimate_depth(frame)
                # Normalizar para 0-1 como no main_analyzer
                depth_normalized = depth_map.astype(np.float32)
                # Converter para visualização usando a mesma função
                depth_color = depth_to_color(depth_map) if depth_to_color else cv2.applyColorMap((depth_map * 255).astype(np.uint8), cv2.COLORMAP_JET)
            except Exception as e:
                print(f"⚠️ Erro no MiDaS: {e}")
                # Fallback para análise simples
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                depth_map = (255 - blurred).astype(np.float32) / 255.0
                depth_normalized = depth_map
                depth_color = cv2.applyColorMap((depth_map * 255).astype(np.uint8), cv2.COLORMAP_JET)
        else:
            # Análise simples baseada em luminosidade
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            depth_map = (255 - blurred).astype(np.float32) / 255.0
            depth_normalized = depth_map
            depth_color = cv2.applyColorMap((depth_map * 255).astype(np.uint8), cv2.COLORMAP_JET)
        
        # Processar algoritmos de navegação com análise sofisticada (igual ao main_analyzer)
        h, w = depth_normalized.shape
        
        # Usar ZoneMappers completos se disponíveis
        if hasattr(self, 'strategic_mapper') and self.strategic_mapper and hasattr(self, 'reactive_mapper') and self.reactive_mapper:
            try:
                # Mapear profundidade para zonas usando os mappers reais
                strategic_grid = self.strategic_mapper.map_depth_to_zones(depth_normalized)
                reactive_grid = self.reactive_mapper.map_depth_to_zones(depth_normalized)
                
                # Processar algoritmos com os grids reais
                if self.strategic and USE_MAPPING:
                    strategic_result = self.strategic.plan(strategic_grid)
                    strategic_direction = strategic_result.target_yaw_delta if hasattr(strategic_result, 'target_yaw_delta') else 0.0
                else:
                    strategic_direction = 0.0
                    
                if self.reactive and USE_MAPPING:
                    reactive_result = self.reactive.compute(reactive_grid)
                    reactive_direction = reactive_result.yaw_delta if hasattr(reactive_result, 'yaw_delta') else 0.0
                else:
                    reactive_direction = 0.0
                    
            except Exception as e:
                print(f"⚠️ Erro nos algoritmos sofisticados: {e}")
                # Fallback para análise simples 3x3
                strategic_direction, reactive_direction = self._simple_analysis_fallback(depth_normalized)
        else:
            # Fallback para análise simples 3x3
            strategic_direction, reactive_direction = self._simple_analysis_fallback(depth_normalized)
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
            'zone_analysis': {
                'strategic_grid': f"{strategic_grid.grid_h}x{strategic_grid.grid_w}" if 'strategic_grid' in locals() else "N/A",
                'reactive_grid': f"{reactive_grid.grid_h}x{reactive_grid.grid_w}" if 'reactive_grid' in locals() else "N/A"
            }  # Para debug
        }
    
    def capture_loop(self):
        """Loop de captura contínua."""
        frame_count = 0
        while self.is_running:
            try:
                result = self.process_frame()
                if result:
                    # Converter para base64 com menor qualidade
                    _, buffer = cv2.imencode('.jpg', result['combined'], [cv2.IMWRITE_JPEG_QUALITY, 60])
                    img_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    self.current_frame = img_base64
                    self.current_data = {
                        'strategic': float(result['strategic']),
                        'reactive': float(result['reactive']),
                        'frame_count': frame_count,
                        'timestamp': result['timestamp'],
                        'camera': self.current_camera
                    }
                    
                    frame_count += 1
                    if frame_count % 30 == 0:  # Debug a cada 30 frames
                        strategic_val = result['strategic']
                        reactive_val = result['reactive']
                        print(f"📊 Frame {frame_count} - Strategic: {strategic_val:+.2f}, Reactive: {reactive_val:+.2f}")
                        print(f"    Imagem: {len(img_base64)} bytes, Câmera: {self.current_camera}")
                else:
                    print("⚠️  Nenhum frame capturado")
                    
                time.sleep(0.1)  # ~10 FPS
                
            except KeyboardInterrupt:
                print("\n⏹️  Interrompendo captura...")
                break
            except Exception as e:
                print(f"❌ Erro no loop de captura: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(1)
    
    def start_capture(self):
        """Iniciar captura em thread separada."""
        self.is_running = True
        self.capture_thread = threading.Thread(target=self.capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
    
    def stop_capture(self):
        """Parar captura e liberar recursos."""
        print("⏹️  Parando captura...")
        self.is_running = False
        
        # Aguardar thread terminar
        if hasattr(self, 'capture_thread') and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)
            
        # Fechar câmera se aberta
        if hasattr(self, 'camera_source') and self.camera_source:
            try:
                self.camera_source.release()
                self.camera_source = None
            except:
                pass
                
        print("✅ Captura parada")

# Instância global
tofcam_viewer = TOFcamWebViewer()

class TOFcamRequestHandler(BaseHTTPRequestHandler):
    """Handler para requisições HTTP."""
    
    def do_GET(self):
        if self.path == '/':
            self.serve_html()
        elif self.path.startswith('/stream'):  # Aceitar /stream com query string
            self.serve_stream()
        elif self.path == '/data':
            self.serve_data()
        elif self.path == '/cameras':
            self.serve_cameras()
        else:
            print(f"❌ Endpoint não encontrado: {self.path}")
            self.send_error(404)
            
    def do_POST(self):
        if self.path == '/switch_camera':
            self.handle_camera_switch()
        else:
            self.send_error(404)
    
    def serve_html(self):
        """Servir página HTML principal."""
        html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>TOFcam Web Viewer - Interface Completa</title>
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
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 TOFcam Web Viewer</h1>
        <p class="subtitle">Visualização completa com 4 visualizações simultâneas</p>
    </div>
    
    <div class="container">
        <div class="camera-controls">
            <label for="cameraSelect">📹 Câmera:</label>
            <select id="cameraSelect" onchange="switchCamera()">
                <!-- Opções serão preenchidas via JavaScript -->
            </select>
            <span id="cameraStatus" class="camera-status">Carregando...</span>
        </div>
        
        <div class="video-container">
            <img id="videoStream" src="" alt="TOFcam Stream Combinado (4 visualizações)" />
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value strategic" id="strategicValue">--</div>
                <div class="stat-label">Strategic Navigation</div>
                <div class="algorithm-detail" id="strategicDetail">Planejamento estratégico</div>
            </div>
            <div class="stat-box">
                <div class="stat-value reactive" id="reactiveValue">--</div>
                <div class="stat-label">Reactive Avoidance</div>
                <div class="algorithm-detail" id="reactiveDetail">Desvio reativo</div>
            </div>
            <div class="stat-box">
                <div class="stat-value frame-info" id="frameCount">--</div>
                <div class="stat-label">Frame Count</div>
                <div class="algorithm-detail">Frames processados</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" id="status">--</div>
                <div class="stat-label">System Status</div>
                <div class="algorithm-detail">Estado do sistema</div>
            </div>
        </div>
    </div>

    <script>
        function updateStream() {
            const img = document.getElementById('videoStream');
            const oldSrc = img.src;
            img.onerror = function() {
                console.log('❌ Erro ao carregar imagem');
                setTimeout(updateStream, 1000); // Tentar novamente em 1s
            };
            img.onload = function() {
                console.log('✅ Imagem carregada');
            };
            img.src = '/stream?' + new Date().getTime();
        }
        
        function loadCameras() {
            fetch('/cameras')
                .then(response => response.json())
                .then(cameras => {
                    const select = document.getElementById('cameraSelect');
                    const controls = document.querySelector('.camera-controls');
                    
                    select.innerHTML = '';
                    cameras.forEach(cam => {
                        const option = document.createElement('option');
                        option.value = cam.id;
                        option.textContent = `Câmera ${cam.id}`;
                        if (cam.active) option.selected = true;
                        select.appendChild(option);
                    });
                    
                    const activeCamera = cameras.find(cam => cam.active);
                    
                    // Se há apenas uma câmera, desabilitar seletor
                    if (cameras.length <= 1) {
                        select.disabled = true;
                        document.getElementById('cameraStatus').textContent = 
                            `📹 Câmera ${activeCamera ? activeCamera.id : 'N/A'} (única disponível)`;
                    } else {
                        select.disabled = false;
                        document.getElementById('cameraStatus').textContent = 
                            `Ativa: Câmera ${activeCamera ? activeCamera.id : 'N/A'} (${cameras.length} disponíveis)`;
                    }
                })
                .catch(err => {
                    console.error('Erro ao carregar câmeras:', err);
                    document.getElementById('cameraStatus').textContent = 'Erro';
                });
        }
        
        function switchCamera() {
            const select = document.getElementById('cameraSelect');
            const cameraId = parseInt(select.value);
            
            document.getElementById('cameraStatus').textContent = 'Trocando...';
            
            fetch('/switch_camera', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({camera_id: cameraId})
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    document.getElementById('cameraStatus').textContent = `Ativa: Câmera ${cameraId}`;
                    console.log(`✅ Câmera trocada para ${cameraId}`);
                } else {
                    document.getElementById('cameraStatus').textContent = 'Erro na troca';
                    console.error(`❌ Erro ao trocar câmera: ${result.error}`);
                }
            })
            .catch(err => {
                console.error('Erro ao trocar câmera:', err);
                document.getElementById('cameraStatus').textContent = 'Erro na troca';
            });
        }
        
        function updateData() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    // Strategic
                    const strategicEl = document.getElementById('strategicValue');
                    strategicEl.textContent = data.strategic.toFixed(3) + '°';
                    
                    // Reactive
                    const reactiveEl = document.getElementById('reactiveValue');
                    reactiveEl.textContent = data.reactive.toFixed(3) + '°';
                    
                    // Frame count
                    document.getElementById('frameCount').textContent = data.frame_count;
                    
                    // Status
                    const diff = Math.abs(data.strategic - data.reactive);
                    let status, statusClass;
                    if (diff < 0.1) {
                        status = 'ACORDO ✅';
                        statusClass = 'positive';
                    } else if (diff < 0.3) {
                        status = 'SIMILAR 🟡';
                        statusClass = 'neutral';
                    } else {
                        status = 'DIVERGEM 🔴';
                        statusClass = 'negative';
                    }
                    
                    const statusEl = document.getElementById('status');
                    statusEl.textContent = status;
                    statusEl.className = 'stat-value ' + statusClass;
                })
                .catch(err => console.error('Erro ao buscar dados:', err));
        }
        
        // Atualizar stream e dados
        console.log('🚀 Iniciando atualizações...');
        setInterval(updateStream, 500);  // 2 FPS (mais lento para debug)
        setInterval(updateData, 1000);    // 1 Hz
        
        // Primeira atualização
        console.log('📡 Primeira atualização...');
        loadCameras();  // Carregar lista de câmeras
        updateStream();
        updateData();
    </script>
</body>
</html>
        '''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def serve_stream(self):
        """Servir stream de imagem."""
        try:
            if tofcam_viewer.current_frame:
                self.send_response(200)
                self.send_header('Content-type', 'image/jpeg')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                img_data = base64.b64decode(tofcam_viewer.current_frame)
                self.wfile.write(img_data)
                print(f"🖼️  Imagem servida: {len(img_data)} bytes para {self.path}")
            else:
                print(f"❌ Nenhuma imagem disponível para {self.path}")
                self.send_error(503, "Nenhuma imagem disponível")
        except Exception as e:
            print(f"❌ Erro ao servir imagem: {e}")
            self.send_error(500, f"Erro interno: {e}")
    
    def serve_data(self):
        """Servir dados em JSON."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        data = tofcam_viewer.current_data if tofcam_viewer.current_data else {}
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def serve_cameras(self):
        """Servir lista de câmeras disponíveis."""
        cameras_data = []
        for cam_id in tofcam_viewer.available_cameras:
            cameras_data.append({
                'id': cam_id,
                'active': cam_id == tofcam_viewer.current_camera
            })
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(cameras_data).encode('utf-8'))
    
    def handle_camera_switch(self):
        """Lidar com troca de câmera."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            camera_id = data.get('camera_id')
            
            success = tofcam_viewer.switch_camera(camera_id)
            
            response = {'success': success}
            if not success:
                response['error'] = f'Falha ao trocar para câmera {camera_id}'
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            error_response = {'success': False, 'error': str(e)}
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suprimir logs HTTP."""
        pass

def main():
    """Função principal."""
    print("🌐 TOFcam Web Viewer")
    print("=" * 40)
    
    try:
        # Inicializar componentes
        tofcam_viewer.initialize_components()
        
        # Iniciar captura
        tofcam_viewer.start_capture()
        
        # Iniciar servidor web
        port = 8080
        server = ThreadedHTTPServer(('localhost', port), TOFcamRequestHandler)
        
        print(f"🚀 Servidor iniciado em: http://localhost:{port}")
        print("📱 Abra o navegador e acesse o link acima")
        print("⏹️  Pressione Ctrl+C para parar")
        print("-" * 40)
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Parando servidor...")
            server.shutdown()
            server.server_close()
        
    except KeyboardInterrupt:
        print("\n🛑 Parando servidor...")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        
    finally:
        # Garantir que tudo seja limpo
        tofcam_viewer.stop_capture()
        if 'server' in locals():
            try:
                server.shutdown()
                server.server_close()
            except:
                pass
        print("✅ Servidor parado!")

if __name__ == "__main__":
    main()