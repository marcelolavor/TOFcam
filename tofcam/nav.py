import numpy as np
from typing import Tuple
try:
    from tofcam.tof_types import ZoneGrid, ZoneCell, ZoneStatus, StrategicPlan, ReactiveCommand, CellState
except ImportError:
    from tof_types import ZoneGrid, ZoneCell, ZoneStatus, StrategicPlan, ReactiveCommand, CellState

class ZoneMapper:
    def __init__(
        self,
        grid_h: int,
        grid_w: int,
        warn_threshold: float = 0.3,
        emergency_threshold: float = 0.15,
        roi: Tuple[float, float, float, float] = (0.0, 1.0, 0.0, 1.0),
    ):
        """
        roi: (y_min_rel, y_max_rel, x_min_rel, x_max_rel) em [0,1]
             para permitir ROIs diferentes (estratégico vs reativo).
        """
        self.grid_h = grid_h
        self.grid_w = grid_w
        self.warn_threshold = warn_threshold
        self.emergency_threshold = emergency_threshold
        self.roi = roi

    def map_depth_to_zones(self, depth_map: np.ndarray) -> ZoneGrid:
        h, w = depth_map.shape

        y0 = int(self.roi[0] * h)
        y1 = int(self.roi[1] * h)
        x0 = int(self.roi[2] * w)
        x1 = int(self.roi[3] * w)

        roi_depth = depth_map[y0:y1, x0:x1]
        roi_h, roi_w = roi_depth.shape

        cell_h = roi_h // self.grid_h
        cell_w = roi_w // self.grid_w

        cells = np.empty((self.grid_h, self.grid_w), dtype=object)

        global_min = float(roi_depth.min())
        global_max = float(roi_depth.max())

        for i in range(self.grid_h):
            for j in range(self.grid_w):
                yy0 = y0 + i * cell_h
                yy1 = y0 + ((i + 1) * cell_h if i < self.grid_h - 1 else roi_h)
                xx0 = x0 + j * cell_w
                xx1 = x0 + ((j + 1) * cell_w if j < self.grid_w - 1 else roi_w)

                region = depth_map[yy0:yy1, xx0:xx1]
                if region.size == 0:
                    min_depth = np.inf
                    mean_depth = np.inf
                    state = CellState.FREE
                else:
                    min_depth = float(np.percentile(region, 10))
                    mean_depth = float(region.mean())

                    if min_depth < self.emergency_threshold:
                        state = CellState.EMERGENCY
                    elif min_depth < self.warn_threshold:
                        state = CellState.WARNING
                    else:
                        state = CellState.FREE

                cells[i, j] = ZoneCell(
                    row=i,
                    col=j,
                    min_depth=min_depth,
                    mean_depth=mean_depth,
                    state=state,
                )

        return ZoneGrid(
            grid_h=self.grid_h,
            grid_w=self.grid_w,
            cells=cells,
            depth_min=global_min,
            depth_max=global_max,
        )

# Estratégico: quase toda imagem
strategic_mapper = ZoneMapper(
    grid_h=24, grid_w=32,
    warn_threshold=0.35, emergency_threshold=0.2,
    roi=(0.1, 1.0, 0.1, 0.9)
)

# Reativo: região inferior/central
reactive_mapper = ZoneMapper(
    grid_h=12, grid_w=16,
    warn_threshold=0.25, emergency_threshold=0.12,
    roi=(0.5, 1.0, 0.25, 0.75)
)


class StrategicPlanner:
    def __init__(self, fov_horizontal_deg: float = 80.0):
        self.fov_h = np.deg2rad(fov_horizontal_deg)

    def plan(self, zone_grid: ZoneGrid) -> StrategicPlan:
        cells = zone_grid.cells
        gh, gw = zone_grid.grid_h, zone_grid.grid_w

        # Agrega por coluna: score por quantidade de FREE + profundidade média
        col_scores = np.zeros(gw, dtype=float)
        col_min_depth = np.full(gw, np.inf, dtype=float)

        for j in range(gw):
            free_count = 0
            depth_sum = 0.0
            depth_count = 0
            for i in range(gh):
                cell = cells[i, j]
                if cell.state == CellState.FREE:
                    free_count += 1
                if np.isfinite(cell.min_depth):
                    depth_sum += cell.min_depth
                    depth_count += 1
                    if cell.min_depth < col_min_depth[j]:
                        col_min_depth[j] = cell.min_depth

            avg_depth = (depth_sum / depth_count) if depth_count > 0 else 0.0
            # Score simples: mais livres + mais longe
            col_scores[j] = free_count + 0.5 * avg_depth

        best_col = int(np.argmax(col_scores))
        best_score = float(col_scores[best_col])

        # Converte coluna em ângulo
        center = (gw - 1) / 2.0
        norm = (best_col - center) / center  # -1..+1
        target_yaw = -norm * (self.fov_h / 2.0)  # Inverter sinal para corrigir direção

        # Min distância à frente no corredor escolhido
        min_dist = float(col_min_depth[best_col]) if np.isfinite(col_min_depth[best_col]) else np.inf

        # Confiança simples
        confidence = best_score / (gh + 0.5) if gh > 0 else 0.0

        return StrategicPlan(
            target_yaw_delta=target_yaw,
            confidence=confidence,
            min_distance_ahead=min_dist,
        )


class ReactiveAvoider:
    def __init__(self, front_rows: int = 4):
        self.front_rows = front_rows

    def compute(self, zone_grid: ZoneGrid) -> ReactiveCommand:
        cells = zone_grid.cells
        gh, gw = zone_grid.grid_h, zone_grid.grid_w

        front_start = max(0, gh - self.front_rows)

        # centro
        center_col = gw // 2
        window = range(center_col - 1, center_col + 2)

        has_emergency = False
        has_warning = False

        # Verifica região frontal
        for i in range(front_start, gh):
            for j in window:
                if not (0 <= j < gw):
                    continue
                state = cells[i, j].state
                if state == CellState.EMERGENCY:
                    has_emergency = True
                elif state == CellState.WARNING:
                    has_warning = True

        # Score esquerda / direita baseado em FREE/ WARNING
        left_score = 0.0
        right_score = 0.0
        for i in range(front_start, gh):
            for j in range(gw):
                s = cells[i, j].state
                weight = 1.0 if s == CellState.FREE else (0.3 if s == CellState.WARNING else 0.0)
                if j < center_col:
                    left_score += weight
                else:
                    right_score += weight

        # yaw: para lado mais livre
        if left_score > right_score:
            yaw_delta = +0.6
        elif right_score > left_score:
            yaw_delta = -0.6
        else:
            yaw_delta = 0.0

        # forward_scale: reduz se warning/emergency
        if has_emergency:
            forward_scale = 0.0
        elif has_warning:
            forward_scale = 0.3
        else:
            forward_scale = 1.0

        return ReactiveCommand(
            yaw_delta=yaw_delta,
            forward_scale=forward_scale,
            emergency_brake=has_emergency,
        )
