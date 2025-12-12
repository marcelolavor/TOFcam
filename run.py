#!/usr/bin/env python3
"""
TOFcam - Main Application Entry Point (Refactored)
================================================

Professional Time-of-Flight camera analysis application
using tofcam.lib with web interface and navigation algorithms.
"""

from tofcam.lib import (
    create_camera_manager, create_depth_estimator, create_navigator,
    create_render_pipeline, WebIntegration, TOFConfig, NavigationMode,
    logger
)
import time
import threading

class TOFcamApplication:
    """Aplicação principal TOFcam usando tofcam.lib"""
    
    def __init__(self):
        self.config = TOFConfig()
        self.running = False
        
        # Componentes principais
        self.camera_manager = None
        self.depth_estimator = None
        self.navigator = None
        self.render_pipeline = None
        self.web_interface = None
        
    def initialize(self):
        """Inicializar todos os componentes"""
        logger.info("Inicializando componentes...")
        
        # Criar componentes
        self.camera_manager = create_camera_manager()
        self.depth_estimator = create_depth_estimator()
        self.navigator = create_navigator(self.config.navigation)
        self.render_pipeline = create_render_pipeline()
        
        # Configurar câmera
        if not self.camera_manager.add_camera(self.config.camera):
            logger.warning("Câmera não encontrada, usando modo de teste")
            self.config.camera.use_test_image = True
            self.camera_manager.add_camera(self.config.camera)
        
        # Iniciar interface web
        self.web_interface = WebIntegration()
        web_info = self.web_interface.start()
        
        logger.info("Todos os componentes inicializados")
        logger.info(f"Interface web disponível em: {web_info['url']}")
        
    def process_frame(self):
        """Processar um frame"""
        # Capturar frame
        frame = self.camera_manager.read_frame()
        if frame is None:
            return False
        
        # Estimar profundidade
        depth_map = self.depth_estimator.estimate_depth(frame)
        
        # Análise de navegação
        nav_result = self.navigator.navigate(depth_map, NavigationMode.HYBRID)
        
        # Criar visualização
        zone_grid = self.navigator.zone_mapper.create_strategic_grid(depth_map)
        visualization = self.render_pipeline.render_complete_view(
            depth_map, zone_grid, nav_result
        )
        
        # Atualizar interface web
        self.web_interface.update_frame(visualization)
        self.web_interface.update_navigation(nav_result)
        
        # Salvar frames se configurado
        if self.config.save_frames:
            import cv2
            import os
            os.makedirs(self.config.output_dir, exist_ok=True)
            timestamp = int(time.time() * 1000)
            cv2.imwrite(f"{self.config.output_dir}/frame_{timestamp}.jpg", frame)
            cv2.imwrite(f"{self.config.output_dir}/analysis_{timestamp}.jpg", visualization)
        
        return True
    
    def run_processing_loop(self):
        """Loop de processamento em thread separada"""
        frame_count = 0
        start_time = time.time()
        
        while self.running:
            try:
                if self.process_frame():
                    frame_count += 1
                    
                    # Log a cada 30 frames
                    if frame_count % 30 == 0:
                        elapsed = time.time() - start_time
                        fps = frame_count / elapsed
                        logger.info(f"Processado {frame_count} frames, FPS: {fps:.1f}")
                
                # Limitar FPS
                time.sleep(1/30)
                
            except Exception as e:
                logger.error(f"Erro no processamento: {e}")
                time.sleep(1)
    
    def run(self):
        """Executar aplicação"""
        try:
            self.initialize()
            
            # Iniciar processamento
            self.running = True
            processing_thread = threading.Thread(target=self.run_processing_loop, daemon=True)
            processing_thread.start()
            
            print("\n🌐 Servidor web iniciado!")
            print("📱 Acesse a interface web para visualizar")
            print("🛑 Pressione Ctrl+C para parar")
            
            # Manter aplicação viva
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Aplicação interrompida pelo usuário")
        except Exception as e:
            logger.error(f"Erro na aplicação: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Encerrar aplicação"""
        self.running = False
        
        if self.web_interface:
            self.web_interface.stop()
        
        if self.camera_manager:
            self.camera_manager.close_all()
        
        logger.info("Aplicação encerrada")

def main():
    """Main application entry point"""
    print("🚀 TOFcam - Professional Analysis System (Refactored)")
    print("=" * 60)
    
    app = TOFcamApplication()
    app.run()

if __name__ == "__main__":
    main()