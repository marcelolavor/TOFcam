#!/usr/bin/env python3
"""
TOFcam - Unified Application Entry Point
=======================================

Professional Time-of-Flight camera analysis application with three operation modes:
- Desktop: 4-window visualization interface  
- Web: Browser-based streaming interface
- Analysis: Background processing with file output

Usage:
    python main.py                    # Interactive mode selection
    python main.py --desktop         # Desktop interface
    python main.py --web             # Web interface
    python main.py --analysis        # Analysis mode
    python main.py --help            # Show this help
"""

import argparse
import sys
import os
import cv2
import numpy as np
import time
import threading
import signal
from typing import Optional, NamedTuple
from datetime import datetime
from pathlib import Path

from tofcam.lib import (
    create_camera_manager, create_depth_estimator, create_navigator,
    create_render_pipeline, create_zone_renderer, create_depth_renderer,
    WebIntegration, TOFConfig, NavigationMode, CameraConfig, 
    NavigationConfig, logger, AnalysisFrame, discover_cameras
)

# =============================================================================
# Shared Components
# =============================================================================

class PerceptionOutput(NamedTuple):
    """Unified perception output for all modes"""
    frame: np.ndarray
    depth_map: np.ndarray
    strategic_grid: object
    reactive_grid: object
    strategic_plan: object
    reactive_cmd: object

class PerceptionSystem:
    """Unified perception system using tofcam.lib"""
    
    def __init__(self, camera_manager, depth_estimator, navigator):
        self.camera_manager = camera_manager
        self.depth_estimator = depth_estimator
        self.navigator = navigator
    
    def process_once(self) -> Optional[PerceptionOutput]:
        """Process one frame - unified API"""
        frame = self.camera_manager.read_frame()
        if frame is None:
            return None
        
        depth_map = self.depth_estimator.estimate_depth(frame)
        nav_result = self.navigator.navigate(depth_map)
        
        return PerceptionOutput(
            frame, depth_map, 
            nav_result.strategic_grid, nav_result.reactive_grid,
            nav_result.strategic, nav_result.reactive
        )

def check_display():
    """Check if X11 display is available"""
    try:
        import subprocess
        display = os.environ.get('DISPLAY', '')
        if not display:
            return False
        result = subprocess.run(['xset', 'q'], capture_output=True, timeout=2)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

# =============================================================================
# Desktop Mode
# =============================================================================

class DesktopMode:
    """4-window desktop visualization mode"""
    
    def __init__(self):
        self.config = TOFConfig()
        self.perception = None
        self.render_pipeline = None
        self.zone_renderer = None
        self.depth_renderer = None
        
    def initialize(self):
        """Initialize desktop components"""
        logger.info("🖥️ Inicializando modo Desktop...")
        
        camera_manager = create_camera_manager()
        depth_estimator = create_depth_estimator()
        navigator = create_navigator(self.config.navigation)
        
        # Try to discover and use available cameras
        available_cameras = discover_cameras()
        if available_cameras:
            # Use first available camera
            camera_config = CameraConfig(index=available_cameras[0])
            camera_manager.add_camera(camera_config)
        else:
            # Fallback to test mode
            logger.warning("No cameras found, using test mode")
            test_config = CameraConfig(index=0, use_test_image=True)
            camera_manager.add_camera(test_config)
        
        self.perception = PerceptionSystem(camera_manager, depth_estimator, navigator)
        self.render_pipeline = create_render_pipeline()
        self.zone_renderer = create_zone_renderer()
        self.depth_renderer = create_depth_renderer()
        
        # Setup windows
        window_names = ['Camera', 'Depth', 'Strategic', 'Reactive']
        for i, name in enumerate(window_names):
            cv2.namedWindow(name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(name, 480, 360)
            x, y = (i % 2) * 500, (i // 2) * 400
            cv2.moveWindow(name, x, y)
        
        logger.info("✅ Desktop mode initialized")
        
    def run(self):
        """Run desktop interface"""
        if not check_display():
            logger.error("❌ Sem display X11 disponível para modo desktop")
            logger.info("💡 Use: python main.py --web")
            return
            
        self.initialize()
        
        logger.info("🖥️ Desktop interface ativa - Pressione 'q' para sair")
        
        try:
            while True:
                output = self.perception.process_once()
                if output is None:
                    time.sleep(0.1)
                    continue
                
                # Render visualizations
                depth_vis = self.depth_renderer.render(output.depth_map)
                strategic_vis = self.zone_renderer.render_strategic(output.strategic_grid)
                reactive_vis = self.zone_renderer.render_reactive(output.reactive_grid)
                
                # Display windows
                cv2.imshow('Camera', output.frame)
                cv2.imshow('Depth', depth_vis)
                cv2.imshow('Strategic', strategic_vis)
                cv2.imshow('Reactive', reactive_vis)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            cv2.destroyAllWindows()
            logger.info("🛑 Desktop mode stopped")

# =============================================================================
# Web Mode
# =============================================================================

class WebMode:
    """Browser-based streaming interface mode"""
    
    def __init__(self):
        self.config = TOFConfig()
        self.running = False
        self.web_interface = None
        self.perception = None
        # Don't setup signal handler here - wait until after initialization
        
    def setup_signal_handler(self):
        """Setup signal handler for graceful shutdown"""
        def signal_handler(sig, frame):
            logger.info("🛑 Sinal de interrupção recebido - parando imediatamente")
            self.running = False
            # Force exit immediately without cleanup to avoid hanging
            import threading
            timer = threading.Timer(1.0, lambda: os._exit(0))
            timer.start()
            raise KeyboardInterrupt()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def initialize(self):
        """Initialize web components"""
        logger.info("🌐 Inicializando modo Web...")
        
        # Limpar porta 8081 antes de iniciar
        logger.info("🧹 Limpando porta 8081...")
        import subprocess
        try:
            # Try multiple methods to clear port
            subprocess.run(["pkill", "-f", ":8081"], check=False, capture_output=True)
            subprocess.run(["pkill", "-f", "8081"], check=False, capture_output=True)
            time.sleep(0.5)  # Give time for cleanup
            logger.info("✅ Porta 8081 limpa")
        except Exception as e:
            logger.debug(f"Erro na limpeza da porta (normal se não houver processos): {e}")
        
        camera_manager = create_camera_manager()
        depth_estimator = create_depth_estimator()
        navigator = create_navigator(self.config.navigation)
        render_pipeline = create_render_pipeline()
        
        # Try to discover and use available cameras
        available_cameras = discover_cameras()
        if available_cameras:
            # Use first available camera
            camera_config = CameraConfig(index=available_cameras[0])
            camera_manager.add_camera(camera_config)
        else:
            # Fallback to test mode
            logger.warning("No cameras found, using test mode")
            test_config = CameraConfig(index=0, use_test_image=True)
            camera_manager.add_camera(test_config)
        
        self.web_interface = WebIntegration(port=8081)
        web_info = self.web_interface.start()
        logger.info(f"Interface web disponível em: {web_info['url']}")
        
        self.perception = PerceptionSystem(camera_manager, depth_estimator, navigator)
        self.render_pipeline = render_pipeline
        
        logger.info("✅ Web mode initialized")
    
    def run(self):
        """Run web interface"""
        self.initialize()
        
        # Setup signal handler only after initialization is complete
        self.setup_signal_handler()
        
        logger.info("🌐 Servidor web iniciado!")
        logger.info("📱 Acesse a interface web para visualizar")
        logger.info("🛑 Pressione Ctrl+C para parar")
        
        self.running = True
        frame_count = 0
        last_fps_time = time.time()
        
        try:
            while self.running:
                # Quick check for interrupt
                if not self.running:
                    break
                    
                if not hasattr(self, 'perception') or self.perception is None:
                    logger.error("Perception system not initialized")
                    break
                    
                output = self.perception.process_once()
                if output is None:
                    time.sleep(0.01)  # Shorter sleep for faster response
                    continue
                
                frame_count += 1
                current_time = time.time()
                
                if current_time - last_fps_time >= 5:
                    fps = frame_count / (current_time - last_fps_time)
                    logger.info(f"Processado {frame_count} frames, FPS: {fps:.1f}")
                    frame_count = 0
                    last_fps_time = current_time
                    
        except KeyboardInterrupt:
            logger.info("🚨 Interrupção detectada - parando...")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Erro na execução: {e}")
        finally:
            try:
                self.shutdown()
            except:
                pass
            logger.info("✅ Programa finalizado")
    
    def shutdown(self):
        """Shutdown web interface"""
        self.running = False
        try:
            if hasattr(self, 'web_interface') and self.web_interface:
                self.web_interface.stop()
        except Exception as e:
            logger.debug(f"Erro parando web interface: {e}")
        
        try:
            if hasattr(self, 'perception') and self.perception:
                # Cleanup perception resources if needed
                pass
        except Exception as e:
            logger.debug(f"Erro limpando perception: {e}")
        
        logger.info("🛑 Web mode stopped")

# =============================================================================
# Analysis Mode
# =============================================================================

class AnalysisMode:
    """Background analysis with file output mode"""
    
    def __init__(self):
        self.config = TOFConfig()
        self.output_dir = Path(f"analysis_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.frame_count = 0
        
    def initialize(self):
        """Initialize analysis components"""
        logger.info("📊 Inicializando modo Analysis...")
        
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"💾 Salvando resultados em: {self.output_dir}")
        
        camera_manager = create_camera_manager()
        depth_estimator = create_depth_estimator()
        navigator = create_navigator(self.config.navigation)
        
        # Try to discover and use available cameras
        available_cameras = discover_cameras()
        if available_cameras:
            # Use first available camera
            camera_config = CameraConfig(index=available_cameras[0])
            camera_manager.add_camera(camera_config)
        else:
            # Fallback to test mode
            logger.warning("No cameras found, using test mode")
            test_config = CameraConfig(index=0, use_test_image=True)
            camera_manager.add_camera(test_config)
        
        self.perception = PerceptionSystem(camera_manager, depth_estimator, navigator)
        self.render_pipeline = create_render_pipeline()
        self.zone_renderer = create_zone_renderer()
        self.depth_renderer = create_depth_renderer()
        
        logger.info("✅ Analysis mode initialized")
    
    def run(self):
        """Run background analysis"""
        self.initialize()
        
        logger.info("📊 Análise em background iniciada")
        logger.info("💾 Salvando frames processados")
        logger.info("🛑 Pressione Ctrl+C para parar")
        
        try:
            while True:
                output = self.perception.process_once()
                if output is None:
                    time.sleep(0.1)
                    continue
                
                self._save_analysis_frame(output)
                self.frame_count += 1
                
                if self.frame_count % 30 == 0:
                    logger.info(f"📊 Processados {self.frame_count} frames")
                    
        except KeyboardInterrupt:
            logger.info("Análise interrompida pelo usuário")
        finally:
            logger.info(f"📊 Total de frames processados: {self.frame_count}")
            logger.info(f"💾 Resultados salvos em: {self.output_dir}")
    
    def _save_analysis_frame(self, output: PerceptionOutput):
        """Save analysis results to files"""
        frame_dir = self.output_dir / f"frame_{self.frame_count:06d}"
        frame_dir.mkdir(exist_ok=True)
        
        # Save images
        cv2.imwrite(str(frame_dir / "camera.jpg"), output.frame)
        
        depth_vis = self.depth_renderer.render(output.depth_map)
        cv2.imwrite(str(frame_dir / "depth.jpg"), depth_vis)
        
        strategic_vis = self.zone_renderer.render_strategic(output.strategic_grid)
        cv2.imwrite(str(frame_dir / "strategic.jpg"), strategic_vis)
        
        reactive_vis = self.zone_renderer.render_reactive(output.reactive_grid)
        cv2.imwrite(str(frame_dir / "reactive.jpg"), reactive_vis)
        
        # Save metadata (simplified)
        metadata = {
            "frame": self.frame_count,
            "timestamp": datetime.now().isoformat(),
            "strategic_angle": getattr(output.strategic_plan, 'optimal_yaw', 0),
            "reactive_urgency": getattr(output.reactive_cmd, 'urgency', 0)
        }
        
        import json
        with open(frame_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

# =============================================================================
# Interactive Mode
# =============================================================================

def interactive_mode():
    """Interactive mode selection"""
    print("\n🚀 TOFcam - Professional Analysis System")
    print("=" * 50)
    print("Escolha o modo de operação:")
    print()
    print("1. 🖥️  Desktop - Interface com 4 janelas")
    print("2. 🌐 Web - Interface no navegador") 
    print("3. 📊 Analysis - Processamento em background")
    print("4. ❌ Sair")
    print()
    
    while True:
        try:
            choice = input("👉 Sua escolha (1-4): ").strip()
            
            if choice == '1':
                return DesktopMode()
            elif choice == '2':
                return WebMode()
            elif choice == '3':
                return AnalysisMode()
            elif choice == '4':
                print("👋 Saindo...")
                return None
            else:
                print("❌ Opção inválida. Escolha 1-4.")
                
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            return None

# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Main entry point with argument parsing"""
    # Setup global signal handler as a fallback
    def global_signal_handler(sig, frame):
        logger.info("🚨 Forçando parada do programa...")
        os._exit(1)
    
    signal.signal(signal.SIGINT, global_signal_handler)
    signal.signal(signal.SIGTERM, global_signal_handler)
    
    parser = argparse.ArgumentParser(
        description='TOFcam - Professional Time-of-Flight Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--desktop', action='store_true',
                       help='Run desktop interface (4 windows)')
    parser.add_argument('--web', action='store_true', 
                       help='Run web interface')
    parser.add_argument('--analysis', action='store_true',
                       help='Run background analysis')
    
    args = parser.parse_args()
    
    # Determine mode
    mode = None
    if args.desktop:
        mode = DesktopMode()
    elif args.web:
        mode = WebMode()
    elif args.analysis:
        mode = AnalysisMode()
    else:
        mode = interactive_mode()
    
    # Run selected mode
    if mode:
        try:
            mode.run()
        except Exception as e:
            logger.error(f"❌ Erro na execução: {e}")
            return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())