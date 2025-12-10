"""
Biblioteca centralizada de análise TOFcam
Contém toda lógica de processamento de depth estimation e navegação
"""

import cv2
import numpy as np
import torch
import time
from typing import Optional, Dict, Any, Tuple, NamedTuple
import base64
from io import BytesIO
from PIL import Image

# Imports locais
from types import *
from mapping import ZoneMapper, StrategicPlanner, ReactiveAvoider

class AnalysisConfig:
    """Configuração para análise"""
    def __init__(
        self,
        strategic_grid_size: Tuple[int, int] = (24, 32),
        reactive_grid_size: Tuple[int, int] = (12, 16),
        use_sophisticated_analysis: bool = True,
        save_frames: bool = False,
        output_dir: str = "output_images",
        web_format: bool = False
    ):
        self.strategic_grid_size = strategic_grid_size
        self.reactive_grid_size = reactive_grid_size
        self.use_sophisticated_analysis = use_sophisticated_analysis
        self.save_frames = save_frames
        self.output_dir = output_dir
        self.web_format = web_format

class AnalysisResult(NamedTuple):
    """Resultado da análise"""
    rgb_frame: np.ndarray
    depth_color: np.ndarray
    combined_vis: Optional[np.ndarray]
    strategic_result: Dict[str, Any]
    reactive_result: Dict[str, Any]
    rgb_base64: Optional[str] = None
    depth_base64: Optional[str] = None
    timestamp: float = 0.0
    frame_id: int = 0

class TOFAnalyzer:
    """Analisador centralizado para TOFcam"""
    
    def __init__(self, config: AnalysisConfig, camera_id: int = 0):
        self.config = config
        self.frame_counter = 0
        self.camera_id = camera_id
        
        # Inicializar camera
        self._init_camera()
        
        # Inicializar MiDaS
        self._init_midas()
        
        # Inicializar mappers e algoritmos
        self._init_algorithms()
        
    def _init_camera(self):
        """Inicializar câmera"""
        from camera import CameraSource
        self.camera_manager = CameraSource(index=self.camera_id)
        self.camera_manager.open()
        
    def _init_midas(self):
        """Inicializar MiDaS depth estimation"""
        print("🧠 Carregando MiDaS...")
        self.midas = torch.hub.load("intel-isl/MiDaS", "MiDaS")
        self.midas.eval()
        
        # Transformações MiDaS
        self.midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
        self.transform = self.midas_transforms.default_transform
        
        # Device
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.midas.to(self.device)
        print("✅ MiDaS carregado!")
        
    def _init_algorithms(self):
        """Inicializar algoritmos de navegação"""
        if self.config.use_sophisticated_analysis:
            # Mappers sofisticados
            self.strategic_mapper = ZoneMapper(
                grid_h=self.config.strategic_grid_size[0],
                grid_w=self.config.strategic_grid_size[1],
                warn_threshold=0.3,
                emergency_threshold=0.15
            )
            
            self.reactive_mapper = ZoneMapper(
                grid_h=self.config.reactive_grid_size[0],
                grid_w=self.config.reactive_grid_size[1],
                warn_threshold=0.2,
                emergency_threshold=0.1
            )
            
            # Algoritmos
            self.strategic_planner = StrategicPlanner(fov_horizontal_deg=80.0)
            self.reactive_avoider = ReactiveAvoider(front_rows=4)
            
            print("✅ Algoritmos sofisticados carregados!")
        else:
            print("ℹ️ Usando análise simplificada")
    
    def process_frame(self, frame: np.ndarray, camera_id: int = 0) -> AnalysisResult:
        """
        Processa um frame completo
        
        Args:
            frame: Frame RGB de entrada
            camera_id: ID da câmera
            
        Returns:
            AnalysisResult com todos os dados processados
        """
        self.frame_counter += 1
        timestamp = time.time()
        
        # 1. Depth estimation com MiDaS
        depth_map = self._estimate_depth(frame)
        
        # 2. Converter depth para visualização colorida
        depth_color = self._depth_to_color(depth_map)
        
        # 3. Análise sofisticada ou simples
        if self.config.use_sophisticated_analysis and hasattr(self, 'strategic_mapper'):
            strategic_result, reactive_result = self._sophisticated_analysis(depth_map)
        else:
            strategic_result, reactive_result = self._simple_analysis(depth_map)
        
        # 4. Criar visualização combinada
        combined_vis = self._create_combined_visualization(
            frame, depth_color, strategic_result, reactive_result, camera_id
        )
        
        # 5. Converter para base64 se necessário (web)
        rgb_base64 = None
        depth_base64 = None
        
        if self.config.web_format:
            rgb_base64 = self._frame_to_base64(combined_vis)
            depth_base64 = self._frame_to_base64(depth_color)
        
        # 6. Salvar frames se configurado
        if self.config.save_frames:
            self._save_frame_analysis(
                frame, depth_color, combined_vis, 
                strategic_result, reactive_result, 
                camera_id, timestamp
            )
        
        return AnalysisResult(
            rgb_frame=frame,
            depth_color=depth_color,
            combined_vis=combined_vis,
            strategic_result=strategic_result,
            reactive_result=reactive_result,
            rgb_base64=rgb_base64,
            depth_base64=depth_base64,
            timestamp=timestamp,
            frame_id=self.frame_counter
        )
    
    def _estimate_depth(self, frame: np.ndarray) -> np.ndarray:
        """Estimar profundidade usando MiDaS"""
        # Preprocessar para MiDaS
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_tensor = self.transform(rgb)  # Remove o .unsqueeze(0)
        
        # Adicionar batch dimension se necessário
        if input_tensor.dim() == 3:
            input_tensor = input_tensor.unsqueeze(0)
        
        input_tensor = input_tensor.to(self.device)
        
        # Inferência
        with torch.no_grad():
            depth_tensor = self.midas(input_tensor)
            depth_map = depth_tensor.squeeze().cpu().numpy()
        
        return depth_map
    
    def _depth_to_color(self, depth_map: np.ndarray) -> np.ndarray:
        """Converter mapa de profundidade para visualização colorida"""
        # Normalizar depth map
        depth_normalized = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        # Aplicar colormap
        depth_color = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_PLASMA)
        
        return depth_color
    
    def _sophisticated_analysis(self, depth_map: np.ndarray) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Análise sofisticada com ZoneMappers"""
        try:
            # Criar grids de zona
            strategic_grid = self.strategic_mapper.map_depth_to_zones(depth_map)
            reactive_grid = self.reactive_mapper.map_depth_to_zones(depth_map)
            
            # Processar algoritmos
            strategic_plan = self.strategic_planner.plan(strategic_grid)
            reactive_cmd = self.reactive_avoider.compute(reactive_grid)
            
            strategic_result = {
                'target_yaw_delta': strategic_plan.target_yaw_delta,
                'confidence': strategic_plan.confidence,
                'min_distance_ahead': strategic_plan.min_distance_ahead,
                'grid_info': f"{strategic_grid.grid_h}x{strategic_grid.grid_w}"
            }
            
            reactive_result = {
                'yaw_delta': reactive_cmd.yaw_delta,
                'forward_scale': reactive_cmd.forward_scale,
                'emergency_brake': reactive_cmd.emergency_brake,
                'grid_info': f"{reactive_grid.grid_h}x{reactive_grid.grid_w}"
            }
            
            return strategic_result, reactive_result
            
        except Exception as e:
            print(f"⚠️ Erro na análise sofisticada: {e}")
            return self._simple_analysis(depth_map)
    
    def _simple_analysis(self, depth_map: np.ndarray) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Análise simples como fallback"""
        h, w = depth_map.shape
        
        # Dividir em 3x3 para análise simples
        cell_h, cell_w = h // 3, w // 3
        
        # Analisar região central vs laterais
        center = depth_map[cell_h:2*cell_h, cell_w:2*cell_w]
        left = depth_map[cell_h:2*cell_h, 0:cell_w]
        right = depth_map[cell_h:2*cell_h, 2*cell_w:3*cell_w]
        
        center_mean = np.nanmean(center)
        left_mean = np.nanmean(left)
        right_mean = np.nanmean(right)
        
        # Decisão simples baseada em profundidade média
        if left_mean > right_mean:
            strategic_yaw = -0.3  # Vire à esquerda
        else:
            strategic_yaw = 0.3   # Vire à direita
            
        reactive_yaw = strategic_yaw * 1.5  # Mais agressivo
        
        strategic_result = {
            'target_yaw_delta': strategic_yaw,
            'confidence': 0.5,
            'min_distance_ahead': center_mean if np.isfinite(center_mean) else float('inf'),
            'grid_info': "3x3_simple"
        }
        
        reactive_result = {
            'yaw_delta': reactive_yaw,
            'forward_scale': 1.0 if center_mean > 1.0 else 0.3,
            'emergency_brake': center_mean < 0.5 if np.isfinite(center_mean) else False,
            'grid_info': "3x3_simple"
        }
        
        return strategic_result, reactive_result
    
    def _create_combined_visualization(
        self, 
        frame: np.ndarray, 
        depth_color: np.ndarray,
        strategic_result: Dict[str, Any],
        reactive_result: Dict[str, Any],
        camera_id: int
    ) -> np.ndarray:
        """Criar visualização combinada"""
        # Redimensionar para visualização
        small_frame = cv2.resize(frame, (320, 240))
        small_depth = cv2.resize(depth_color, (320, 240))
        
        # Combinar lado a lado
        combined = np.hstack([small_frame, small_depth])
        
        # Adicionar setas de direção
        self._draw_navigation_arrows(combined, strategic_result, reactive_result)
        
        # Adicionar labels e informações
        cv2.putText(combined, "ORIGINAL", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(combined, "DEPTH MAP", (330, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        strategic_yaw = strategic_result.get('target_yaw_delta', 0.0)
        reactive_yaw = reactive_result.get('yaw_delta', 0.0)
        
        cv2.putText(combined, f"STRATEGIC: {strategic_yaw:+.2f}", (10, 260), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        cv2.putText(combined, f"REACTIVE: {reactive_yaw:+.2f}", (330, 260), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
        
        # Info da câmera e timestamp
        cv2.putText(combined, f"Camera {camera_id}", (10, 290), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        cv2.putText(combined, time.strftime("%H:%M:%S"), (10, 310), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return combined
    
    def _draw_navigation_arrows(
        self, 
        combined: np.ndarray, 
        strategic_result: Dict[str, Any], 
        reactive_result: Dict[str, Any]
    ):
        """Desenhar setas de navegação"""
        center_x, center_y = 160, 120
        arrow_length = 60
        
        # Seta Strategic (amarelo)
        strategic_yaw = strategic_result.get('target_yaw_delta', 0.0)
        strategic_angle = strategic_yaw * 45
        end_x = int(center_x + arrow_length * np.sin(np.radians(strategic_angle)))
        end_y = int(center_y - arrow_length * np.cos(np.radians(strategic_angle)))
        cv2.arrowedLine(combined, (center_x, center_y), (end_x, end_y), 
                       (0, 255, 255), 3, tipLength=0.3)
        
        # Seta Reactive (magenta) na parte do depth
        reactive_yaw = reactive_result.get('yaw_delta', 0.0)
        reactive_angle = reactive_yaw * 45
        reactive_center_x = center_x + 320
        end_x = int(reactive_center_x + arrow_length * np.sin(np.radians(reactive_angle)))
        end_y = int(center_y - arrow_length * np.cos(np.radians(reactive_angle)))
        cv2.arrowedLine(combined, (reactive_center_x, center_y), (end_x, end_y), 
                       (255, 0, 255), 3, tipLength=0.3)
    
    def _frame_to_base64(self, frame: np.ndarray) -> str:
        """Converter frame para base64"""
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        encoded_image = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded_image}"
    
    def _save_frame_analysis(
        self,
        frame: np.ndarray,
        depth_color: np.ndarray,
        combined_vis: np.ndarray,
        strategic_result: Dict[str, Any],
        reactive_result: Dict[str, Any],
        camera_id: int,
        timestamp: float
    ):
        """Salvar análise do frame"""
        import os
        
        # Criar diretório com timestamp
        timestamp_str = time.strftime("%Y%m%d_%H%M%S", time.localtime(timestamp))
        output_subdir = os.path.join(self.config.output_dir, f"cam{camera_id}_{timestamp_str}")
        os.makedirs(output_subdir, exist_ok=True)
        
        # Salvar imagens
        cv2.imwrite(os.path.join(output_subdir, "original.jpg"), frame)
        cv2.imwrite(os.path.join(output_subdir, "depth.jpg"), depth_color)
        cv2.imwrite(os.path.join(output_subdir, "combined.jpg"), combined_vis)
        
        # Salvar dados de análise
        analysis_data = {
            'frame_id': self.frame_counter,
            'timestamp': timestamp,
            'camera_id': camera_id,
            'strategic': {
                'yaw_delta': float(strategic_result['yaw_delta']),
                'direction': strategic_result.get('direction', 'forward'),
                'confidence': float(strategic_result.get('confidence', 0.0))
            },
            'reactive': {
                'yaw_delta': float(reactive_result['yaw_delta']),
                'direction': reactive_result.get('direction', 'forward'),
                'confidence': float(reactive_result.get('confidence', 0.0))
            }
        }
        
        import json
        with open(os.path.join(output_subdir, "analysis.json"), "w") as f:
            json.dump(analysis_data, f, indent=2)
    
    def cleanup(self):
        """Limpar recursos"""
        try:
            if hasattr(self, 'camera_manager'):
                self.camera_manager.release()
        except:
            pass
        
        print(f"🛑 Cleanup finalizado")