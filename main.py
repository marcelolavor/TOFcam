import cv2
from camera import CameraSource, PerceptionSystem
from depth_estimator import MidasDepthEstimator
from mapping import ZoneMapper, StrategicPlanner, ReactiveAvoider
from analysis import ObstacleAnalyzer
from view import depth_to_color, draw_zone_grid

def visualize(frame, depth_map, strategic_grid, reactive_grid,
              strategic_mapper, reactive_mapper):

    # 1) Depth em color map
    depth_color = depth_to_color(depth_map)

    # 2) Estratégico sobre depth
    strategic_img = draw_zone_grid(
        depth_color.copy(),
        strategic_grid,
        strategic_mapper.roi
    )

    # 3) Reativo sobre depth
    reactive_img = draw_zone_grid(
        depth_color.copy(),
        reactive_grid,
        reactive_mapper.roi
    )

    # 4) Mostrar ou salvar
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
    print("🚀 Iniciando TOFcam Debug Mode...")
    print("📹 Tentando inicializar câmera...")
    
    cam = CameraSource(0, use_test_image=False)
    cam.open()

    print("🧠 Carregando modelo MiDaS para estimação de profundidade...")
    depth_estimator = MidasDepthEstimator(model_type="MiDaS_small")
    print("✅ Modelo MiDaS carregado com sucesso")

    print("🗺️ Configurando mapeadores de zona...")

    strategic_mapper = ZoneMapper(
        grid_h=24, grid_w=32,
        warn_threshold=0.35, emergency_threshold=0.20,
        roi=(0.10, 1.00, 0.10, 0.90)
    )

    reactive_mapper = ZoneMapper(
        grid_h=12, grid_w=16,
        warn_threshold=0.25, emergency_threshold=0.12,
        roi=(0.50, 1.00, 0.25, 0.75)
    )

    print("🎯 Inicializando planejadores...")
    planner = StrategicPlanner()
    avoider = ReactiveAvoider()
    print("✅ Planejadores inicializados")

    print("🔧 Montando sistema de percepção...")
    system = PerceptionSystem(
        cam,
        depth_estimator,
        strategic_mapper,
        reactive_mapper,
        planner,
        avoider
    )
    print("✅ Sistema de percepção pronto!")
    print("")
    print("▶️ Iniciando loop principal - Pressione ESC para sair")
    
    frame_count = 0
    try:
        while True:
            frame_count += 1
            if frame_count % 30 == 0:  # A cada 30 frames
                print(f"📊 Processando frame {frame_count}...")
                
            out = system.process_once()
            if out is None:
                print("⚠️ Não foi possível capturar frame")
                break
                continue

            # visualizar
            visualize(
                frame=out.frame,
                depth_map=out.depth_map,
                strategic_grid=out.strategic_grid,
                reactive_grid=out.reactive_grid,
                strategic_mapper=strategic_mapper,
                reactive_mapper=reactive_mapper
            )

            # imprimir parâmetros de controle
            print(
                f"STRATEGIC yaw={out.strategic_plan.target_yaw_delta:.3f}, "
                f"conf={out.strategic_plan.confidence:.2f}"
            )
            print(
                f"REACTIVE yaw={out.reactive_cmd.yaw_delta:.3f}, "
                f"fwd={out.reactive_cmd.forward_scale:.2f}, "
                f"emergency={out.reactive_cmd.emergency_brake}"
            )

            # Testa se tem display para o waitKey
            try:
                if cv2.waitKey(1) & 0xFF == 27:
                    break
            except:
                # Sem display, roda apenas alguns frames para teste
                if frame_count >= 3:
                    print("🏁 Teste concluído (sem display)")
                    break

    finally:
        cam.release()
        try:
            cv2.destroyAllWindows()
        except:
            pass  # Sem display


if __name__ == "__main__":
    main()
