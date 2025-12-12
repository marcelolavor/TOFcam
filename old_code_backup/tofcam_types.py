import abc
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import IntEnum

import cv2
import numpy as np
import torch

class CellState(IntEnum):
    FREE = 0
    WARNING = 1
    EMERGENCY = 2

class Direction(IntEnum):
    FORWARD = 0
    LEFT = 1
    RIGHT = 2
    BACKWARD = 3

# Alias para compatibilidade
ZoneStatus = CellState

class Direction(IntEnum):
    LEFT = -1
    STRAIGHT = 0
    RIGHT = 1

@dataclass
class ZoneCell:
    row: int
    col: int
    min_depth: float
    mean_depth: float
    state: CellState


@dataclass
class ZoneGrid:
    grid_h: int
    grid_w: int
    cells: np.ndarray  # matriz (grid_h x grid_w) de ZoneCell
    depth_min: float
    depth_max: float


@dataclass
class ObstacleInfo:
    zone_grid: ZoneGrid
    min_distance: float
    has_collision_ahead: bool
    suggested_yaw_delta: float  # radianos, ex.: + esquerda, - direita


@dataclass
class StrategicPlan:
    target_yaw_delta: float  # rad
    confidence: float
    min_distance_ahead: float


@dataclass
class ReactiveCommand:
    yaw_delta: float
    forward_scale: float  # 0..1 (redução de velocidade)
    emergency_brake: bool


class DepthEstimator(abc.ABC):
    @abc.abstractmethod
    def estimate_depth(self, frame_bgr: np.ndarray) -> np.ndarray:
        """Retorna mapa de profundidade (float32, H x W)."""
        pass
