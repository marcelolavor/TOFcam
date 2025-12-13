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
    from tofcam.lib.camera import CameraSource
    from tofcam.lib.config import CameraConfig
    print("✅ Camera carregado")
except ImportError as e:
    print(f"⚠️ Camera não disponível: {e}")
    CameraSource = None
    CameraConfig = None

try:
    from tofcam.lib.depth import MidasDepthEstimator
    print("✅ Depth estimator carregado")
except ImportError:
    try:
        from tofcam.lib.depth import MidasDepthEstimator
        print("✅ Depth estimator carregado")
    except ImportError as e:
        print(f"⚠️ Depth estimator não disponível: {e}")
        MidasDepthEstimator = None
        USE_DEPTH_ESTIMATION = False

try:
    from tofcam.lib.navigation import StrategicPlanner, ReactiveAvoider
    print("✅ Mappers carregados")
except ImportError:
    try:
        from tofcam.lib.navigation import StrategicPlanner, ReactiveAvoider
        print("✅ Mappers carregados")
    except ImportError as e:
        print(f"⚠️ Mapping não disponível: {e}")
        StrategicPlanner = ReactiveAvoider = None
        USE_MAPPING = False

try:
    from tofcam.lib.visualization import ColorUtils
    print("✅ View carregado")
except ImportError:
    try:
        from tofcam.lib.visualization import ColorUtils
        print("✅ View carregado")
    except ImportError as e:
        print(f"⚠️ View não disponível: {e}")
        def depth_to_color(depth):
            # Usar esquema intuitivo: Vermelho=Próximo, Verde=Longe
            try:
                return ColorUtils.depth_to_color(depth)
            except:
                # Fallback personalizado com esquema vermelho->verde
                import cv2
                # Criar colormap customizado
                d = (depth * 255).astype(np.uint8)
                # Inverter JET para que vermelho seja próximo
                colored = cv2.applyColorMap(255 - d, cv2.COLORMAP_JET)
                # Ajustar para nosso padrão: trocar azul por vermelho para proximidade
                colored[:,:,[0,2]] = colored[:,:,[2,0]]  # Trocar B e R
                return colored
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
        self.current_camera = 0  # Será definido para a maior câmera disponível
        self.available_cameras = []
        
        # Controles para técnica híbrida de profundidade
        self.depth_mode = "hybrid"  # "midas", "gradient", "hybrid"
        self.midas_weight = 0.87  # Peso do MiDaS (0.0 a 1.0) - 87% padrão
        self.gradient_weight = 0.58  # Peso do gradiente (0.0 a 1.0) - 58% padrão
        
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
        # Definir câmera padrão como a maior disponível  
        if cameras:
            self.current_camera = max(cameras)
            print(f"📹 Câmera padrão definida: {self.current_camera} (maior disponível)")
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
        
        if CameraSource and CameraConfig:
            try:
                print(f"🔧 Criando CameraConfig para câmera {self.current_camera}...")
                config = CameraConfig(index=self.current_camera)
                print(f"🔧 Criando CameraSource com config...")
                self.camera_source = CameraSource(config)
                print(f"🔧 CameraSource criado, tentando abrir...")
                if not self.camera_source.open():
                    raise Exception(f"Falha ao abrir câmera {self.current_camera}")
            except Exception as e:
                print(f"❌ Erro na criação/abertura do CameraSource: {e}")
                raise
        else:
            # Fallback para OpenCV direto
            print(f"🔧 Usando fallback cv2.VideoCapture({self.current_camera})...")
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
            
        # Inicializar variáveis que serão usadas ao longo da função
        depth_color = None
        frame = None
            
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
        
        # Análise de profundidade com técnica híbrida configurável
        try:
            # Sempre gerar múltiplos depth maps para permitir mistura visual
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 1. Depth map por gradiente Sobel (bordas)
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient = np.sqrt(grad_x**2 + grad_y**2)
            gradient = gradient / (gradient.max() + 1e-8)
            depth_gradient = 1.0 - gradient  # Bordas = próximo
            
            # 2. Depth map por luminosidade (simulação MiDaS quando não disponível)
            # Áreas mais escuras = mais próximas (como MiDaS)
            blurred = cv2.GaussianBlur(gray, (9, 9), 0)
            depth_luminosity = (255 - blurred).astype(np.float32) / 255.0
            
            # 3. Usar MiDaS real se disponível
            depth_midas = None
            if self.depth_estimator:
                try:
                    depth_midas = self.depth_estimator.estimate_depth(frame)
                    depth_midas = depth_midas.astype(np.float32)
                    if depth_midas.max() > 1.0:
                        depth_midas = depth_midas / depth_midas.max()
                except Exception as e:
                    print(f"⚠️ Erro no MiDaS: {e}")
                    depth_midas = None
            
            # Combinar depth maps conforme modo e pesos
            if self.depth_mode == "gradient":
                depth_map = depth_gradient
            elif self.depth_mode == "midas":
                depth_map = depth_midas if depth_midas is not None else depth_luminosity
            elif self.depth_mode == "hybrid":
                # Usar MiDaS real se disponível, senão usar luminosidade como substituto
                primary_depth = depth_midas if depth_midas is not None else depth_luminosity
                
                # Normalizar pesos
                total_weight = self.midas_weight + self.gradient_weight
                if total_weight > 0:
                    weight_primary = self.midas_weight / total_weight
                    weight_gradient = self.gradient_weight / total_weight
                else:
                    weight_primary = 0.5
                    weight_gradient = 0.5
                
                # Combinar com pesos visíveis
                depth_map = (primary_depth * weight_primary + 
                           depth_gradient * weight_gradient)
            else:
                depth_map = depth_gradient  # Fallback
                
                depth_normalized = depth_map
                
                # Aplicar mapeamento de cores personalizado com maior contraste
                def enhanced_depth_colormap(depth_array):
                    """Mapear profundidade para cores com maior variação de contraste."""
                    # Normalizar corretamente para garantir uso completo da escala
                    depth_min = np.min(depth_array)
                    depth_max = np.max(depth_array)
                    
                    # Evitar divisão por zero
                    if depth_max > depth_min:
                        # Normalizar para 0-1 usando min/max reais da imagem
                        depth_norm = (depth_array - depth_min) / (depth_max - depth_min)
                    else:
                        depth_norm = depth_array
                    
                    # Inverter para que maior distância = valor mais alto = cor mais distante (preto)
                    # MiDaS: valores altos = longe, valores baixos = perto
                    # Nossa escala: 0 = perto (vermelho), 1 = longe (preto)
                    depth_norm = 1.0 - depth_norm
                    
                    # Expandir contraste com mapeamento não-linear para melhor distribuição
                    contrast_factor = 1.8  # Fator ajustado para melhor distribuição
                    depth_enhanced = np.power(depth_norm, 1.0 / contrast_factor)
                    
                    # Mapear para esquema de cores INTUITIVO: Vermelho->Amarelo->Verde->Preto
                    # 0.0 -> Vermelho intenso (255, 0, 0) - PERIGO/MUITO PRÓXIMO
                    # 0.25 -> Vermelho-laranja (255, 128, 0) - ATENÇÃO/PRÓXIMO  
                    # 0.5 -> Amarelo (255, 255, 0) - CUIDADO/MÉDIO
                    # 0.75 -> Verde (0, 255, 0) - SEGURO/LONGE
                    # 1.0 -> Preto (0, 0, 0) - MUITO LONGE/IRRELEVANTE
                    
                    height, width = depth_enhanced.shape
                    colored = np.zeros((height, width, 3), dtype=np.uint8)
                    
                    for i in range(height):
                        for j in range(width):
                            val = depth_enhanced[i, j]
                            
                            if val <= 0.25:  # Vermelho intenso -> Vermelho-laranja (PERIGO)
                                ratio = val / 0.25
                                colored[i, j] = [
                                    255,                     # R: mantém vermelho máximo
                                    int(128 * ratio),        # G: 0->128 (adiciona laranja)
                                    0                        # B: mantém 0
                                ]
                            elif val <= 0.5:  # Vermelho-laranja -> Amarelo (ATENÇÃO)
                                ratio = (val - 0.25) / 0.25
                                colored[i, j] = [
                                    255,                     # R: mantém 255
                                    int(128 + 127 * ratio),  # G: 128->255 (completa amarelo)
                                    0                        # B: mantém 0
                                ]
                            elif val <= 0.75:  # Amarelo -> Verde (CUIDADO -> SEGURO)
                                ratio = (val - 0.5) / 0.25
                                colored[i, j] = [
                                    int(255 - 255 * ratio),  # R: 255->0 (remove vermelho)
                                    255,                     # G: mantém verde máximo
                                    0                        # B: mantém 0
                                ]
                            else:  # Verde -> Preto (LONGE -> IRRELEVANTE)
                                ratio = (val - 0.75) / 0.25
                                colored[i, j] = [
                                    0,                       # R: mantém 0
                                    int(255 - 255 * ratio),  # G: 255->0 (escurece)
                                    0                        # B: mantém 0
                                ]
                    
                    return colored
                
                # Usar mapeamento personalizado ou fallback intuitivo
                try:
                    depth_color = enhanced_depth_colormap(depth_map)
                except Exception as e:
                    print(f"⚠️ Erro no mapeamento personalizado: {e}, usando fallback intuitivo")
                    # Fallback com esquema vermelho->verde
                    depth_normalized = (depth_map - np.min(depth_map)) / (np.max(depth_map) - np.min(depth_map) + 1e-8)
                    depth_inverted = 1.0 - depth_normalized  # Inverter: 0=longe, 1=perto
                    depth_color = cv2.applyColorMap((depth_inverted * 255).astype(np.uint8), cv2.COLORMAP_HOT)
                    
        except Exception as e:
            print(f"⚠️ Erro no processamento de profundidade: {e}")
            # Fallback para análise simples
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            depth_map = (255 - blurred).astype(np.float32) / 255.0
            depth_normalized = depth_map
            # Usar esquema intuitivo também no fallback
            depth_inverted = 1.0 - depth_normalized  # Inverter para vermelho=próximo
            depth_color = cv2.applyColorMap((depth_inverted * 255).astype(np.uint8), cv2.COLORMAP_HOT)
        
        # Garantir que depth_color esteja sempre definido
        if depth_color is None:
            depth_inverted = 1.0 - depth_map  # Inverter para vermelho=próximo
            depth_color = cv2.applyColorMap((depth_inverted * 255).astype(np.uint8), cv2.COLORMAP_HOT)
        
        # Processar algoritmos de navegação com análise sofisticada (igual ao main_analyzer)
        depth_normalized = depth_map
        
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
        
        # Adicionar labels com contraste automático
        def add_text_with_contrast(img, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, scale=0.5, thickness=1):
            """Adicionar texto com contraste automático baseado no fundo."""
            x, y = position
            
            # Verificar se a posição está dentro da imagem
            if x >= 0 and y >= 0 and x < img.shape[1] and y < img.shape[0]:
                # Calcular cor média da região do texto (área aproximada)
                text_width = len(text) * 10 * scale  # Estimativa da largura do texto
                text_height = 20 * scale  # Estimativa da altura do texto
                
                # Definir região para análise (com limites seguros)
                x1 = max(0, int(x - 5))
                y1 = max(0, int(y - text_height))
                x2 = min(img.shape[1], int(x + text_width + 5))
                y2 = min(img.shape[0], int(y + 5))
                
                if x2 > x1 and y2 > y1:
                    # Calcular luminosidade média da região
                    region = img[y1:y2, x1:x2]
                    if len(region.shape) == 3:
                        # Converter para escala de cinza se colorido
                        gray_region = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
                    else:
                        gray_region = region
                    
                    avg_brightness = np.mean(gray_region)
                    
                    # Escolher cor do texto baseada na luminosidade
                    if avg_brightness < 128:  # Fundo escuro
                        text_color = (255, 255, 255)  # Texto branco
                        shadow_color = (0, 0, 0)      # Sombra preta
                    else:  # Fundo claro
                        text_color = (0, 0, 0)        # Texto preto
                        shadow_color = (255, 255, 255) # Sombra branca
                    
                    # Adicionar sombra para maior contraste
                    cv2.putText(img, text, (x + 1, y + 1), font, scale, shadow_color, thickness + 1)
                    # Adicionar texto principal
                    cv2.putText(img, text, (x, y), font, scale, text_color, thickness)
                else:
                    # Fallback para texto branco se não conseguir analisar
                    cv2.putText(img, text, (x, y), font, scale, (255, 255, 255), thickness)
            else:
                # Fallback para texto branco se posição inválida
                cv2.putText(img, text, (10, 20), font, scale, (255, 255, 255), thickness)
        
        # Adicionar labels com contraste inteligente
        add_text_with_contrast(combined, "ORIGINAL", (10, 20))
        add_text_with_contrast(combined, "DEPTH MAP", (330, 20))
        add_text_with_contrast(combined, f"STRATEGIC: {strategic_direction:+.2f}", (10, 260))
        add_text_with_contrast(combined, f"REACTIVE: {reactive_direction:+.2f}", (330, 260))
        
        # Adicionar informação da câmera e timestamp com contraste automático
        add_text_with_contrast(combined, f"Camera {self.current_camera}", (10, 290), scale=0.4)
        add_text_with_contrast(combined, time.strftime("%H:%M:%S"), (10, 310), scale=0.4)
        
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
        elif self.path == '/depth_mode':
            self.handle_depth_mode()
        elif self.path == '/depth_weights':
            self.handle_depth_weights()
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
            flex-direction: row;
            align-items: flex-start; 
            max-width: 1400px;
            margin: 0 auto;
            gap: 30px;
        }
        .left-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 2;
        }
        .controls-container {
            width: 100%;
            max-width: 800px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-bottom: 30px;
        }
        .right-section {
            display: flex;
            flex-direction: column;
            gap: 20px;
            flex: 1;
            min-width: 300px;
        }
        .camera-controls {
            padding: 20px;
            background: rgba(42,42,62,0.8);
            border-radius: 12px;
            display: flex;
            align-items: center;
            gap: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            width: 100%;
            box-sizing: border-box;
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
        .depth-controls {
            padding: 20px;
            background: rgba(42,42,62,0.8);
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            width: 100%;
            box-sizing: border-box;
        }
        .depth-controls label {
            font-weight: bold;
            color: #ff00ff;
            display: block;
            margin-bottom: 10px;
        }
        .depth-controls select {
            width: 100%;
            padding: 12px 15px;
            background: rgba(26,26,46,0.9);
            color: white;
            border: 2px solid #444;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            transition: border-color 0.3s ease;
            margin-bottom: 20px;
        }
        .depth-controls select:hover {
            border-color: #ff00ff;
        }
        .weight-controls {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .weight-group {
            flex: 1;
            min-width: 200px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .weight-group label {
            color: #aaa;
            font-size: 14px;
            margin-bottom: 0;
            min-width: 80px;
        }
        .weight-group input[type="range"] {
            flex: 1;
            height: 6px;
            background: rgba(68,68,68,0.5);
            border-radius: 3px;
            appearance: none;
        }
        .weight-group input[type="range"]::-webkit-slider-thumb {
            appearance: none;
            width: 20px;
            height: 20px;
            background: #ff00ff;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(255,0,255,0.5);
        }
        .weight-group span {
            color: #ff00ff;
            font-weight: bold;
            min-width: 40px;
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
            display: flex;
            flex-direction: column;
            gap: 15px;
            width: 100%;
        }
        .stat-box { 
            background: rgba(42,42,62,0.8); 
            padding: 20px; 
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
        <div class="left-section">
            <div class="controls-container">
                <div class="camera-controls">
                    <label for="cameraSelect">📹 Câmera:</label>
                    <select id="cameraSelect" onchange="switchCamera()">
                        <!-- Opções serão preenchidas via JavaScript -->
                    </select>
                    <span id="cameraStatus" class="camera-status">Carregando...</span>
                </div>
                
                <div class="depth-controls">
                    <label for="depthModeSelect">🧠 Modo Profundidade:</label>
                    <select id="depthModeSelect" onchange="changeDepthMode()">
                        <option value="midas">MiDaS Puro</option>
                        <option value="gradient">Gradiente Puro</option>
                        <option value="hybrid" selected>Híbrido (MiDaS + Gradiente)</option>
                    </select>
                    
                    <div class="weight-controls">
                        <div class="weight-group">
                            <label for="midasWeight">MiDaS:</label>
                            <input type="range" id="midasWeight" min="0" max="100" value="87" oninput="updateWeights()">
                            <span id="midasValue">87%</span>
                        </div>
                        <div class="weight-group">
                            <label for="gradientWeight">Gradiente:</label>
                            <input type="range" id="gradientWeight" min="0" max="100" value="58" oninput="updateWeights()">
                            <span id="gradientValue">58%</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="video-container">
                <img id="videoStream" src="" alt="TOFcam Stream Combinado (4 visualizações)" />
            </div>
        </div>
        
        <div class="right-section">
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
        
        function changeDepthMode() {
            const select = document.getElementById('depthModeSelect');
            const mode = select.value;
            
            fetch('/depth_mode', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({mode: mode})
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    console.log(`✅ Modo de profundidade alterado para: ${result.mode}`);
                } else {
                    console.error(`❌ Erro ao alterar modo: ${result.error}`);
                }
            })
            .catch(err => {
                console.error('Erro ao alterar modo de profundidade:', err);
            });
        }
        
        function updateWeights() {
            const midasWeight = document.getElementById('midasWeight').value;
            const gradientWeight = document.getElementById('gradientWeight').value;
            
            // Atualizar displays
            document.getElementById('midasValue').textContent = midasWeight + '%';
            document.getElementById('gradientValue').textContent = gradientWeight + '%';
            
            // Enviar para servidor
            fetch('/depth_weights', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    midas_weight: midasWeight / 100.0,
                    gradient_weight: gradientWeight / 100.0
                })
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    console.log(`✅ Pesos atualizados - MiDaS: ${result.midas_weight}, Gradiente: ${result.gradient_weight}`);
                } else {
                    console.error(`❌ Erro ao atualizar pesos: ${result.error}`);
                }
            })
            .catch(err => {
                console.error('Erro ao atualizar pesos:', err);
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
    
    def handle_depth_mode(self):
        """Lidar com mudança de modo de profundidade."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            mode = data.get('mode', 'hybrid')
            
            if mode in ['midas', 'gradient', 'hybrid']:
                tofcam_viewer.depth_mode = mode
                success = True
                print(f"🎯 Modo de profundidade alterado para: {mode}")
            else:
                success = False
            
            response = {'success': success, 'mode': tofcam_viewer.depth_mode}
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
    
    def handle_depth_weights(self):
        """Lidar com mudança de pesos de profundidade."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            midas_weight = float(data.get('midas_weight', 0.87))
            gradient_weight = float(data.get('gradient_weight', 0.29))
            
            # Validar pesos (0.0 a 1.0)
            midas_weight = max(0.0, min(1.0, midas_weight))
            gradient_weight = max(0.0, min(1.0, gradient_weight))
            
            tofcam_viewer.midas_weight = midas_weight
            tofcam_viewer.gradient_weight = gradient_weight
            
            print(f"⚖️ Pesos alterados - MiDaS: {midas_weight:.2f}, Gradiente: {gradient_weight:.2f}")
            
            response = {
                'success': True, 
                'midas_weight': midas_weight,
                'gradient_weight': gradient_weight
            }
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
        port = 8082
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