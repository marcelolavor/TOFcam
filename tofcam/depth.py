"""
TOFcam Depth Estimation Module
============================

Advanced depth estimation using MiDaS and custom algorithms
for real-time Time-of-Flight camera analysis.
"""

import cv2
import numpy as np
import torch

class DepthEstimator:
    """Professional depth estimation using MiDaS"""
    
    def __init__(self):
        """Initialize depth estimator"""
        self._init_midas()
        
    def _init_midas(self):
        """Initialize MiDaS depth estimation"""
        print("🧠 Carregando MiDaS...")
        self.midas = torch.hub.load("intel-isl/MiDaS", "MiDaS")
        self.midas.eval()
        
        # MiDaS transforms
        self.midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
        self.transform = self.midas_transforms.default_transform
        
        # Device configuration
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.midas.to(self.device)
        print("✅ MiDaS carregado!")
        
    def estimate(self, frame: np.ndarray) -> np.ndarray:
        """Estimate depth using MiDaS"""
        # Preprocess for MiDaS
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_tensor = self.transform(rgb)
        
        # Add batch dimension if needed
        if input_tensor.dim() == 3:
            input_tensor = input_tensor.unsqueeze(0)
        
        input_tensor = input_tensor.to(self.device)
        
        # Inference
        with torch.no_grad():
            depth_tensor = self.midas(input_tensor)
            depth_map = depth_tensor.squeeze().cpu().numpy()
        
        return depth_map
    
    def to_color(self, depth_map: np.ndarray) -> np.ndarray:
        """Convert depth map to color visualization"""
        # Normalize depth map
        depth_normalized = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        # Apply colormap
        depth_color = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_PLASMA)
        
        return depth_color