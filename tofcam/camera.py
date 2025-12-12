import cv2
import numpy as np
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass
try:
    from tofcam.tof_types import DepthEstimator, ZoneGrid, StrategicPlan, ReactiveCommand
except ImportError:
    from tof_types import DepthEstimator, ZoneGrid, StrategicPlan, ReactiveCommand

if TYPE_CHECKING:
    from mapping import ZoneMapper, StrategicPlanner, ReactiveAvoider

class CameraSource:
    def __init__(self, index: int = 0, use_test_image: bool = False):
        self.index = index
        self.cap = None
        self.use_test_image = use_test_image
        self.test_frame_count = 0

    def open(self):
        if self.use_test_image:
            print("📸 Usando imagem de teste sintética")
            return True
        
        self.cap = cv2.VideoCapture(self.index)
        if not self.cap.isOpened():
            print(f"❌ Não foi possível abrir a câmera {self.index}")
            print("💡 Ativando modo de teste com imagem sintética")
            self.use_test_image = True
            return True
        print(f"✅ Câmera {self.index} aberta com sucesso")
        return True

    def read(self) -> Optional[np.ndarray]:
        if self.use_test_image:
            # Gera uma imagem de teste colorida com gradiente
            height, width = 480, 640
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Gradiente colorido + ruído para simular uma cena
            for y in range(height):
                for x in range(width):
                    frame[y, x] = [
                        int(255 * x / width),  # Componente R
                        int(255 * y / height), # Componente G
                        int(127 + 127 * np.sin(self.test_frame_count * 0.1 + x * 0.01)) # Componente B animado
                    ]
            
            # Adiciona alguns objetos simulados
            cv2.rectangle(frame, (200, 150), (300, 250), (255, 255, 255), -1)
            cv2.circle(frame, (450, 350), 50, (0, 255, 255), -1)
            
            self.test_frame_count += 1
            return frame
        
        if self.cap is None:
            return None
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if self.use_test_image:
            print("📸 Modo de teste finalizado")


@dataclass
class PerceptionOutput:
    frame: np.ndarray  # Frame original da câmera
    depth_map: np.ndarray
    strategic_grid: ZoneGrid
    reactive_grid: ZoneGrid
    strategic_plan: StrategicPlan
    reactive_cmd: ReactiveCommand
    
class PerceptionSystem:
    def __init__(
        self,
        camera: CameraSource,
        depth_estimator: DepthEstimator,
        strategic_mapper: "ZoneMapper",
        reactive_mapper: "ZoneMapper", 
        strategic_planner: "StrategicPlanner",
        reactive_avoider: "ReactiveAvoider",
    ):
        self.camera = camera
        self.depth_estimator = depth_estimator
        self.strategic_mapper = strategic_mapper
        self.reactive_mapper = reactive_mapper
        self.strategic_planner = strategic_planner
        self.reactive_avoider = reactive_avoider

    def process_once(self) -> Optional[PerceptionOutput]:
        frame = self.camera.read()
        if frame is None:
            return None

        depth = self.depth_estimator.estimate_depth(frame)
        depth = cv2.medianBlur(depth, 5)

        strategic_grid = self.strategic_mapper.map_depth_to_zones(depth)
        reactive_grid = self.reactive_mapper.map_depth_to_zones(depth)

        strategic_plan = self.strategic_planner.plan(strategic_grid)
        reactive_cmd = self.reactive_avoider.compute(reactive_grid)

        return PerceptionOutput(
            frame=frame,
            depth_map=depth,
            strategic_grid=strategic_grid,
            reactive_grid=reactive_grid,
            strategic_plan=strategic_plan,
            reactive_cmd=reactive_cmd
        )