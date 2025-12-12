import torch
import cv2
import numpy as np
from typing import Optional
from tofcam_types import DepthEstimator

class MidasDepthEstimator(DepthEstimator):
    def __init__(self, model_type: str = "MiDaS_small", device: Optional[str] = None):
        # model_type: "DPT_Large", "DPT_Hybrid", "MiDaS_small" etc.
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        # Carrega modelo MiDaS
        self.model = torch.hub.load(
            "isl-org/MiDaS", model_type
        ).to(self.device)
        self.model.eval()

        # Carrega transforms
        transforms = torch.hub.load("isl-org/MiDaS", "transforms")
        if "DPT" in model_type:
            self.transform = transforms.dpt_transform
        else:
            self.transform = transforms.small_transform

    @torch.inference_mode()
    def estimate_depth(self, frame_bgr: np.ndarray) -> np.ndarray:
        # Converte BGR (OpenCV) -> RGB
        img_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        # Aplica transform
        input_batch = self.transform(img_rgb).to(self.device)

        # Forward
        prediction = self.model(input_batch)

        # Interpola para tamanho original
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img_rgb.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()

        depth = prediction.cpu().numpy().astype("float32")

        # depth é relativa (inverse depth). Você pode normalizar aqui.
        depth = depth - depth.min()
        depth = depth / (depth.max() + 1e-8)

        # Opcional: converter para "pseudo-distância" (maior valor = mais longe)
        depth_distance_like = 1.0 - depth

        return depth_distance_like
