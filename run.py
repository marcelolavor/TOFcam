#!/usr/bin/env python3
"""
TOFcam - Main Application Entry Point
====================================

Professional Time-of-Flight camera analysis application
with web interface and advanced navigation algorithms.
"""

from tofcam import WebServer, AnalysisConfig

def main():
    """Main application entry point"""
    print("🚀 TOFcam - Professional Analysis System")
    print("=" * 50)
    
    # Configuration
    config = AnalysisConfig(
        use_sophisticated_analysis=True,
        save_frames=True  # Ativar para gerar output_images
    )
    
    # Start web server
    web_server = WebServer(config=config)
    web_server.run()

if __name__ == "__main__":
    main()