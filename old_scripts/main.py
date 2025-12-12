#!/usr/bin/env python3
"""
TOFcam - Main Application (Refactored with Full Functionality)
============================================================

Versão refatorada mantendo 100% das funcionalidades originais:
- 4 janelas de visualização separadas
- MiDaS depth estimation
- Zone mapping strategic e reactive  
- Sistema de percepção completo
- Métricas de navegação detalhadas
"""

import cv2
import numpy as np
import time
from typing import NamedTuple, Optional

from tofcam.lib import (
    create_camera_manager, create_depth_estimator, create_navigator,
    create_render_pipeline, create_zone_renderer, create_depth_renderer,
    NavigationMode, CameraConfig, NavigationConfig, logger
)

class PerceptionOutput(NamedTuple):
    """Saída do sistema de percepção - compatível com código original"""
    frame: np.ndarray
    depth_map: np.ndarray
    strategic_grid: object  # ZoneGrid
    reactive_grid: object   # ZoneGrid 
    strategic_plan: object  # StrategicPlan
    reactive_cmd: object    # ReactiveCommand

class PerceptionSystem:
    """Sistema de percepção usando tofcam.lib - mantém API original"""
    
    def __init__(self, camera_manager, depth_estimator, navigator):
        self.camera_manager = camera_manager
        self.depth_estimator = depth_estimator
        self.navigator = navigator
    
    def process_once(self) -> Optional[PerceptionOutput]:
        """Processa um frame - API compatível com código original"""
        # Capturar frame
        frame = self.camera_manager.read_frame()
        if frame is None:
            return None
        
        # Estimar profundidade
        depth_map = self.depth_estimator.estimate_depth(frame)
        
        # Análise de navegação
        nav_result = self.navigator.navigate(depth_map, NavigationMode.HYBRID)
        
        # Criar grids para compatibilidade
        strategic_grid = self.navigator.zone_mapper.create_strategic_grid(depth_map)
        reactive_grid = self.navigator.zone_mapper.create_reactive_grid(depth_map)
        
        return PerceptionOutput(
            frame=frame,
            depth_map=depth_map,
            strategic_grid=strategic_grid,
            reactive_grid=reactive_grid,
            strategic_plan=nav_result.strategic,
            reactive_cmd=nav_result.reactive
        )

def visualize(frame, depth_map, strategic_grid, reactive_grid, strategic_mapper, reactive_mapper):
    """Visualização com 4 janelas separadas - preserva funcionalidade original"""
    
    # Criar renderers
    depth_renderer = create_depth_renderer()
    zone_renderer = create_zone_renderer()
    
    # 1) Depth em color map
    depth_color = depth_renderer.render_depth_colormap(depth_map)
    
    # 2) Strategic grid sobre depth
    strategic_img = zone_renderer.render_zone_overlay(
        depth_color.copy(), strategic_grid, alpha=0.5
    )
    
    # 3) Reactive grid sobre depth  
    reactive_img = zone_renderer.render_zone_overlay(
        depth_color.copy(), reactive_grid, alpha=0.5
    )
    
    # 4) Mostrar ou salvar - preserva comportamento original
    try:
        cv2.imshow("CAMERA", frame)
        cv2.imshow("DEPTH", depth_color) 
        cv2.imshow("STRATEGIC GRID", strategic_img)
        cv2.imshow("REACTIVE GRID", reactive_img)
        print("📺 Imagens exibidas")
    except:
        print("💾 Salvando imagens...")
        cv2.imwrite("/tmp/camera.jpg", frame)
        cv2.imwrite("/tmp/depth.jpg", depth_color)
        cv2.imwrite("/tmp/strategic.jpg", strategic_img)
        cv2.imwrite("/tmp/reactive.jpg", reactive_img)
        print("✅ Salvo em /tmp/")

def main():
    print("🚀 Iniciando TOFcam usando tofcam.lib...")
    print("📹 Inicializando componentes...")
    
    try:
        # Criar componentes usando a biblioteca
        camera_manager = create_camera_manager()
        depth_estimator = create_depth_estimator()
        
        # Configurar navegação com parâmetros originais
        nav_config = NavigationConfig(
            strategic_grid_size=(24, 32),  # grid_h=24, grid_w=32
            reactive_grid_size=(12, 16),   # grid_h=12, grid_w=16
            warn_threshold=0.35,           # strategic: 0.35, reactive: 0.25
            emergency_threshold=0.20,      # strategic: 0.20, reactive: 0.12
            strategic_roi=(0.10, 1.00, 0.10, 0.90),  # ROI original strategic
            reactive_roi=(0.50, 1.00, 0.25, 0.75)    # ROI original reactive
        )
        navigator = create_navigator(nav_config)
        
        print("✅ Componentes criados com sucesso")
        
        # Configurar câmera
        camera_config = CameraConfig(index=0, use_test_image=False)
        
        if not camera_manager.add_camera(camera_config):
            print("⚠️ Câmera não encontrada, usando modo de teste")
            camera_config.use_test_image = True
            camera_manager.add_camera(camera_config)
        
        # Criar sistema de percepção - preserva API original
        system = PerceptionSystem(camera_manager, depth_estimator, navigator)
        
        print("▶️ Iniciando loop principal - Pressione ESC para sair")
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            frame_count += 1
            if frame_count % 30 == 0:  # A cada 30 frames
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"📊 Processando frame {frame_count}... FPS: {fps:.1f}")
                
            # Processar frame - API original
            out = system.process_once()
            if out is None:
                print("⚠️ Não foi possível capturar frame")
                continue

            # Visualizar - função original preservada
            visualize(
                frame=out.frame,
                depth_map=out.depth_map,
                strategic_grid=out.strategic_grid,
                reactive_grid=out.reactive_grid,
                strategic_mapper=None,  # Não usado nos renderers
                reactive_mapper=None    # Não usado nos renderers
            )

            # Imprimir parâmetros de controle - output original preservado
            if out.strategic_plan and out.reactive_cmd:
                print(
                    f"STRATEGIC yaw={out.strategic_plan.target_yaw_delta:.3f}, "
                    f"conf={out.strategic_plan.confidence:.2f}"
                )
                print(
                    f"REACTIVE yaw={out.reactive_cmd.yaw_delta:.3f}, "
                    f"fwd={out.reactive_cmd.forward_scale:.2f}, "
                    f"emergency={out.reactive_cmd.emergency_brake}"
                )

            # Testa se tem display para o waitKey - preserva comportamento
            try:
                if cv2.waitKey(1) & 0xFF == 27:
                    break
            except:
                # Sem display, roda apenas alguns frames para teste
                if frame_count >= 3:
                    print("🏁 Teste concluído (sem display)")
                    break

    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Limpeza - preserva comportamento original
        try:
            camera_manager.close_all()
        except:
            pass
        try:
            cv2.destroyAllWindows()
        except:
            pass  # Sem display
        print("✅ Finalizado")

if __name__ == "__main__":
    main()
