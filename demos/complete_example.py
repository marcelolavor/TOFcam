#!/usr/bin/env python3
"""
TOFcam Library Example
=====================

Exemplo completo demonstrando como usar a nova biblioteca tofcam.lib
para análise de profundidade, navegação e interface web.
"""

import cv2
import numpy as np
import time
from typing import Optional

# Importar componentes da biblioteca centralizada
from tofcam.lib import (
    # Core types
    NavigationMode, TOFConfig, AnalysisFrame,
    
    # Camera
    create_camera_manager, discover_cameras,
    
    # Depth processing  
    create_depth_estimator, quick_depth_estimation,
    
    # Navigation
    create_navigator, quick_navigation,
    
    # Visualization
    create_render_pipeline, quick_display,
    
    # Web interface
    WebIntegration,
    
    # Utils
    Timer, logger, PerformanceMonitor
)

class TOFcamDemo:
    """Demonstração completa do sistema TOFcam usando a nova biblioteca"""
    
    def __init__(self):
        self.timer = Timer()
        self.performance_monitor = PerformanceMonitor()
        
        # Configuração do sistema
        self.config = TOFConfig()
        logger.info(f"TOFcam Demo iniciado com configuração: {self.config}")
        
        # Componentes principais
        self.camera_manager = None
        self.depth_estimator = None
        self.navigator = None
        self.render_pipeline = None
        self.web_interface = None
        
        # Estado
        self.current_frame = None
        self.current_depth = None
        self.current_navigation = None
        self.running = False
    
    def initialize(self) -> bool:
        """Inicializar todos os componentes"""
        try:
            logger.info("Inicializando componentes...")
            
            # 1. Camera manager
            logger.info("Configurando camera...")
            available_cameras = discover_cameras()
            logger.info(f"Cameras disponíveis: {available_cameras}")
            
            self.camera_manager = create_camera_manager()
            
            # Descobrir e configurar câmera
            config = TOFConfig().camera
            if not self.camera_manager.add_camera(config):
                logger.warning("Falha ao adicionar câmera configurada, usando modo de teste")
            
            # 2. Depth estimator  
            logger.info("Carregando modelo de profundidade...")
            self.depth_estimator = create_depth_estimator()
            
            # 3. Navigator
            logger.info("Configurando sistema de navegação...")
            self.navigator = create_navigator(self.config.navigation)
            
            # 4. Render pipeline
            logger.info("Preparando pipeline de visualização...")
            self.render_pipeline = create_render_pipeline()
            
            # 5. Web interface
            logger.info("Iniciando interface web...")
            self.web_interface = WebIntegration()
            web_info = self.web_interface.start()
            logger.info(f"Interface web disponível em: {web_info['url']}")
            
            logger.info("Todos os componentes inicializados com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização: {e}")
            return False
    
    def process_frame(self) -> Optional[AnalysisFrame]:
        """Processar um frame completo"""
        if not self.camera_manager:
            return None
        
        # Usar timer para medição total
        total_timer = Timer()
        capture_timer = Timer()
        depth_timer = Timer()
        nav_timer = Timer()
        render_timer = Timer()
        
        total_timer.start()
        
        # 1. Capturar frame
        capture_timer.start()
        frame = self.camera_manager.read_frame()
        if frame is None:
            return None
        self.current_frame = frame
        capture_time = capture_timer.stop()
        
        # 2. Estimar profundidade
        depth_timer.start()
        depth_map = self.depth_estimator.estimate_depth(frame)
        self.current_depth = depth_map
        depth_time = depth_timer.stop()
        
        # 3. Análise de navegação
        nav_timer.start()
        nav_result = quick_navigation(depth_map, NavigationMode.HYBRID)
        self.current_navigation = nav_result
        nav_time = nav_timer.stop()
        
        # 4. Renderização
        render_timer.start()
        zone_grid = self.navigator.zone_mapper.create_strategic_grid(depth_map)
        visualization = self.render_pipeline.render_complete_view(
            depth_map, zone_grid, nav_result
        )
        render_time = render_timer.stop()
        
        total_time = total_timer.stop()
        
        # Record performance
        self.performance_monitor.record_frame_time(total_time)
        
        # 5. Atualizar interface web
        self.web_interface.update_frame(visualization)
        self.web_interface.update_navigation(nav_result)
        
        # Criar frame de análise
        analysis_frame = AnalysisFrame(
            timestamp=time.time(),
            frame_id=1,
            rgb_image=frame,
            depth_map=depth_map,
            strategic_grid=zone_grid,
            reactive_grid=zone_grid,  # Usando o mesmo grid por simplicidade
            navigation_result=nav_result,
            depth_colored=visualization
        )
        
        return analysis_frame
    
    def run_realtime_demo(self, duration: float = 60.0):
        """Executar demo em tempo real"""
        logger.info(f"Iniciando demo em tempo real por {duration}s...")
        
        self.running = True
        start_time = time.time()
        frame_count = 0
        
        try:
            while self.running and (time.time() - start_time) < duration:
                self.timer.start()
                
                # Processar frame
                analysis_frame = self.process_frame()
                
                if analysis_frame:
                    frame_count += 1
                    
                    # Mostrar visualização local
                    key = quick_display(analysis_frame.visualization, 
                                      "TOFcam Demo", wait_key=1)
                    
                    # Sair com 'q'
                    if key & 0xFF == ord('q'):
                        break
                    
                    # Log periódico
                    if frame_count % 30 == 0:
                        fps = frame_count / (time.time() - start_time)
                        logger.info(f"Frame {frame_count}, FPS: {fps:.1f}")
                        
                        # Estatísticas de performance
                        avg_frame_time = self.performance_monitor.get_average_frame_time()
                        logger.info(f"Performance - Tempo médio por frame: {avg_frame_time:.3f}s")
                
                # Manter ~30 FPS
                elapsed = self.timer.stop()
                sleep_time = max(0, 1/30 - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("Demo interrompido pelo usuário")
        
        finally:
            self.running = False
            final_fps = frame_count / (time.time() - start_time)
            logger.info(f"Demo finalizado. Frames processados: {frame_count}, FPS médio: {final_fps:.1f}")
    
    def run_single_frame_demo(self):
        """Executar demo de frame único"""
        logger.info("Processando frame único...")
        
        analysis_frame = self.process_frame()
        
        if analysis_frame:
            # Mostrar resultados
            quick_display(analysis_frame.depth_colored, "TOFcam Single Frame")
            
            # Imprimir informações de navegação
            if analysis_frame.navigation_result:
                nav = analysis_frame.navigation_result
                logger.info(f"Navegação - Modo: {nav.mode.value}")
                
                if nav.strategic:
                    logger.info(f"Estratégico - Yaw: {np.rad2deg(nav.strategic.target_yaw_delta):.1f}°, "
                              f"Confiança: {nav.strategic.confidence:.2f}")
                
                if nav.reactive:
                    logger.info(f"Reativo - Urgência: {nav.reactive.urgency:.2f}, "
                              f"Freio emergência: {nav.reactive.emergency_brake}")
            
            # Aguardar tecla
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            logger.error("Falha ao processar frame")
    
    def shutdown(self):
        """Encerrar sistema"""
        logger.info("Encerrando sistema...")
        
        self.running = False
        
        if self.web_interface:
            self.web_interface.stop()
        
        if self.camera_manager:
            self.camera_manager.close_all()
        
        cv2.destroyAllWindows()
        logger.info("Sistema encerrado")

def main():
    """Função principal"""
    demo = TOFcamDemo()
    
    try:
        # Inicializar
        if not demo.initialize():
            logger.error("Falha na inicialização")
            return
        
        # Menu de opções
        print("\nTOFcam Demo - Biblioteca Centralizada")
        print("====================================")
        print("1. Demo em tempo real (60s)")
        print("2. Processar frame único")
        print("3. Apenas interface web")
        print("0. Sair")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "1":
            demo.run_realtime_demo()
        elif choice == "2":
            demo.run_single_frame_demo()
        elif choice == "3":
            logger.info("Interface web rodando. Pressione Ctrl+C para sair.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        elif choice == "0":
            logger.info("Saindo...")
        else:
            logger.warning("Opção inválida")
    
    except Exception as e:
        logger.error(f"Erro no demo: {e}")
    
    finally:
        demo.shutdown()

if __name__ == "__main__":
    main()