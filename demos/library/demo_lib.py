#!/usr/bin/env python3
"""
Demonstração da biblioteca TOFcam - Diferentes configurações
"""

import sys
import os

# Adicionar o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from analyzer_lib import TOFAnalyzer, AnalysisConfig
import cv2
import time

def demo_web_config():
    """Configuração para Web (sem salvar, com base64)"""
    print("🌐 Configuração Web:")
    config = AnalysisConfig(
        strategic_grid_size=(24, 32),
        reactive_grid_size=(12, 16), 
        use_sophisticated_analysis=True,
        save_frames=False,          # ❌ Não salvar
        web_format=True            # ✅ Gerar base64
    )
    return config

def demo_save_config():
    """Configuração para Persistência (salvar, sem base64)"""
    print("💾 Configuração Persistência:")
    config = AnalysisConfig(
        strategic_grid_size=(24, 32),
        reactive_grid_size=(12, 16),
        use_sophisticated_analysis=True,
        save_frames=True,           # ✅ Salvar
        output_dir="demo_output",
        web_format=False           # ❌ Sem base64
    )
    return config

def demo_simple_config():
    """Configuração Simples (análise 3x3)"""
    print("⚡ Configuração Simples:")
    config = AnalysisConfig(
        strategic_grid_size=(3, 3),  # Grid menor
        reactive_grid_size=(3, 3),
        use_sophisticated_analysis=False,  # ❌ Análise simples
        save_frames=True,
        output_dir="demo_simple",
        web_format=False
    )
    return config

def process_single_frame_demo():
    """Demonstrar processamento de frame único"""
    # Abrir câmera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Câmera não disponível")
        return
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("❌ Erro ao capturar frame")
        return
    
    print("📸 Frame capturado!")
    
    # Testar 3 configurações diferentes
    configs = [
        ("Web", demo_web_config()),
        ("Persistência", demo_save_config()),
        ("Simples", demo_simple_config())
    ]
    
    for name, config in configs:
        print(f"\n🔧 Testando configuração: {name}")
        start_time = time.time()
        
        # Criar analyzer
        analyzer = TOFAnalyzer(config)
        
        # Processar frame
        result = analyzer.process_frame(frame, camera_id=0)
        
        # Mostrar resultados
        elapsed = time.time() - start_time
        strategic = result.strategic_result.get('target_yaw_delta', 0.0)
        reactive = result.reactive_result.get('yaw_delta', 0.0)
        
        print(f"   ⏱️  Tempo: {elapsed:.2f}s")
        print(f"   🎯 Strategic: {strategic:+.3f}")
        print(f"   ⚡ Reactive: {reactive:+.3f}")
        print(f"   💾 Salvo: {'✅' if config.save_frames else '❌'}")
        print(f"   🌐 Base64: {'✅' if result.rgb_base64 else '❌'}")
        
        if config.save_frames:
            print(f"   📁 Diretório: {config.output_dir}/")

def main():
    print("🧪 Demonstração TOFcam Library")
    print("=" * 50)
    print("📖 A biblioteca centraliza toda lógica de análise")
    print("🔧 Diferentes parâmetros para diferentes casos de uso")
    print()
    
    process_single_frame_demo()
    
    print("\n" + "=" * 50)
    print("✅ Demonstração concluída!")
    print("💡 A mesma biblioteca serve para:")
    print("   🌐 Interface web (web_viewer_lib.py)")
    print("   💾 Persistência (main_analyzer_lib.py)")
    print("   📱 Apps móveis")
    print("   🔌 APIs")
    print("   📊 Análise offline")

if __name__ == "__main__":
    main()