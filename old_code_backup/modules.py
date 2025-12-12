import numpy as np
from tofcam_types import ZoneGrid, ObstacleInfo, Direction, ZoneStatus

class ObstacleAnalyzer:
    def __init__(self, front_rows: int = 3):
        """
        front_rows: quantas linhas inferiores (mais perto do chão/campo de visão à frente)
                    considerar como "frente" do drone.
        """
        self.front_rows = front_rows

    def analyze(self, zone_grid: ZoneGrid) -> ObstacleInfo:
        cells = zone_grid.cells
        gh, gw = zone_grid.grid_h, zone_grid.grid_w

        # Considera "frente" as linhas mais baixas da imagem (i maiores)
        front_start = max(0, gh - self.front_rows)
        front_region = cells[front_start:, :]

        min_distance = np.inf
        occupancy_map = np.zeros((gh, gw), dtype=bool)

        for i in range(gh):
            for j in range(gw):
                occupancy_map[i, j] = cells[i, j].occupied
                if cells[i, j].min_depth < min_distance:
                    min_distance = cells[i, j].min_depth

        # Checa se há colisão direta à frente (centro da imagem)
        center_col = gw // 2
        # define uma janela central
        center_window = range(center_col - 1, center_col + 2)
        has_collision_ahead = False
        for i in range(front_start, gh):
            for j in center_window:
                if 0 <= j < gw and occupancy_map[i, j]:
                    has_collision_ahead = True
                    break
            if has_collision_ahead:
                break

        # Sugere yaw: se lado esquerdo estiver mais livre, gira à esquerda, etc.
        left_free_score = float(
            (~occupancy_map[front_start:, :center_col]).sum()
        )
        right_free_score = float(
            (~occupancy_map[front_start:, center_col:]).sum()
        )

        if left_free_score > right_free_score:
            suggested_yaw_delta = +0.5  # radianos, por exemplo
        elif right_free_score > left_free_score:
            suggested_yaw_delta = -0.5
        else:
            suggested_yaw_delta = 0.0

        return ObstacleInfo(
            zone_grid=zone_grid,
            min_distance=min_distance,
            has_collision_ahead=has_collision_ahead,
            suggested_yaw_delta=suggested_yaw_delta,
        )
