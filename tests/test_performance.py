#!/usr/bin/env python3
"""
Teste de Performance/Benchmark dos algoritmos TOFcam
Mede velocidade e consumo de recursos
"""

import sys
import os
import numpy as np
import time
import psutil
import gc

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def measure_memory():
    """Medir uso de memória atual"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024  # MB

def benchmark_depth_estimation():
    """Benchmark do estimador de profundidade"""
    print("🧠 Benchmark: Estimativa de Profundidade")
    print("-" * 40)
    
    try:
        from depth_estimator import MidasDepthEstimator
        
        # Criar dados de teste
        test_frames = [
            np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
            np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8),
            np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
        ]
        
        frame_names = ["480p (640x480)", "240p (320x240)", "720p (1280x720)"]
        
        print("📋 Carregando modelo...")
        start_mem = measure_memory()
        estimator = MidasDepthEstimator()
        load_mem = measure_memory()
        print(f"  📊 Memória após carregamento: +{load_mem - start_mem:.1f} MB")
        
        for frame, name in zip(test_frames, frame_names):
            print(f"\n🎬 Testando {name}:")
            
            # Aquecer (primeira execução)
            estimator.estimate_depth(frame)
            
            # Medições reais
            times = []
            for i in range(5):
                start_time = time.time()
                depth = estimator.estimate_depth(frame)
                elapsed = time.time() - start_time
                times.append(elapsed)
                print(f"  ⏱️  Execução {i+1}: {elapsed:.3f}s")
            
            avg_time = np.mean(times)
            fps = 1.0 / avg_time
            print(f"  📊 Tempo médio: {avg_time:.3f}s")
            print(f"  🎯 FPS estimado: {fps:.1f}")
            print(f"  📏 Saída: {depth.shape}")
        
        final_mem = measure_memory()
        print(f"\n📊 Memória final: {final_mem:.1f} MB")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def benchmark_navigation():
    """Benchmark dos algoritmos de navegação"""
    print("\n🧭 Benchmark: Algoritmos de Navegação")
    print("-" * 40)
    
    try:
        from tofcam.nav import StrategicPlanner, ReactiveAvoider, ZoneMapper
        
        # Configurações de teste
        configs = [
            (6, 8, "Pequeno (6x8)"),
            (12, 16, "Médio (12x16)"),
            (24, 32, "Grande (24x32)")
        ]
        
        # Criar mapas de teste
        test_depths = [
            np.random.uniform(0.1, 5.0, (480, 640)).astype(np.float32),
            np.random.uniform(0.1, 5.0, (720, 1280)).astype(np.float32)
        ]
        
        for grid_h, grid_w, config_name in configs:
            print(f"\n🔧 Configuração {config_name}:")
            
            zone_mapper = ZoneMapper(grid_h=grid_h, grid_w=grid_w)
            strategic = StrategicPlanner()
            reactive = ReactiveAvoider()
            
            for i, depth_map in enumerate(test_depths):
                res_name = f"{depth_map.shape[1]}x{depth_map.shape[0]}"
                print(f"  📐 Resolução {res_name}:")
                
                # Benchmark mapeamento
                times_mapping = []
                times_strategic = []
                times_reactive = []
                
                for _ in range(10):
                    # Mapeamento
                    start = time.time()
                    zone_grid = zone_mapper.map_depth_to_zones(depth_map)
                    times_mapping.append(time.time() - start)
                    
                    # Strategic
                    start = time.time()
                    strategic_result = strategic.plan(zone_grid)
                    times_strategic.append(time.time() - start)
                    
                    # Reactive
                    start = time.time()
                    reactive_result = reactive.compute(zone_grid)
                    times_reactive.append(time.time() - start)
                
                print(f"    📊 Mapeamento: {np.mean(times_mapping)*1000:.2f}ms")
                print(f"    🎯 Strategic: {np.mean(times_strategic)*1000:.2f}ms")
                print(f"    ⚡ Reactive: {np.mean(times_reactive)*1000:.2f}ms")
                
                total_time = np.mean(times_mapping) + np.mean(times_strategic) + np.mean(times_reactive)
                fps = 1.0 / total_time
                print(f"    🚀 FPS Pipeline: {fps:.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def benchmark_visualization():
    """Benchmark dos componentes de visualização"""
    print("\n🎨 Benchmark: Visualização")
    print("-" * 40)
    
    try:
        from view import depth_to_color, draw_yaw_arrow
        import cv2
        
        # Dados de teste
        sizes = [
            (240, 320, "Small"),
            (480, 640, "Medium"),
            (720, 1280, "Large")
        ]
        
        for h, w, size_name in sizes:
            print(f"\n📏 Tamanho {size_name} ({w}x{h}):")
            
            depth_map = np.random.uniform(0.1, 5.0, (h, w)).astype(np.float32)
            canvas = np.zeros((h, w, 3), dtype=np.uint8)
            
            # Benchmark colorização
            times_color = []
            for _ in range(20):
                start = time.time()
                colored = depth_to_color(depth_map)
                times_color.append(time.time() - start)
            
            print(f"  🎨 Colorização: {np.mean(times_color)*1000:.2f}ms")
            
            # Benchmark desenho de seta
            times_arrow = []
            for _ in range(20):
                canvas_copy = canvas.copy()
                start = time.time()
                with_arrow = draw_yaw_arrow(canvas_copy, np.random.uniform(-1, 1))
                times_arrow.append(time.time() - start)
            
            print(f"  🧭 Desenho seta: {np.mean(times_arrow)*1000:.2f}ms")
            
            total_viz = np.mean(times_color) + np.mean(times_arrow)
            fps = 1.0 / total_viz
            print(f"  🎯 FPS Visualização: {fps:.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def benchmark_camera():
    """Benchmark da captura de câmera"""
    print("\n📹 Benchmark: Captura de Câmera")
    print("-" * 40)
    
    try:
        from camera import CameraSource
        
        camera = CameraSource(index=0)
        success = camera.open()
        
        if not success:
            print("❌ Não foi possível abrir câmera")
            return False
        
        print("📊 Medindo captura de frames...")
        
        # Descartar primeiros frames
        for _ in range(5):
            camera.read()
        
        # Medir captura
        times = []
        frame_sizes = []
        
        for i in range(50):
            start = time.time()
            frame = camera.read()
            elapsed = time.time() - start
            
            if frame is not None:
                times.append(elapsed)
                frame_sizes.append(frame.shape)
                if i % 10 == 0:
                    print(f"  Frame {i+1}: {elapsed*1000:.2f}ms")
        
        if times:
            avg_time = np.mean(times)
            fps = 1.0 / avg_time
            print(f"📊 Tempo médio captura: {avg_time*1000:.2f}ms")
            print(f"🎯 FPS captura: {fps:.1f}")
            print(f"📏 Resolução: {frame_sizes[0] if frame_sizes else 'N/A'}")
        
        return len(times) > 0
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def run_performance_tests():
    """Executar todos os testes de performance"""
    print("🏁 BENCHMARK TOFcam - PERFORMANCE")
    print("=" * 50)
    
    start_time = time.time()
    start_mem = measure_memory()
    
    tests = [
        ("Camera", benchmark_camera),
        ("Visualização", benchmark_visualization),
        ("Navegação", benchmark_navigation),
        ("Profundidade", benchmark_depth_estimation),
    ]
    
    results = {}
    passed = 0
    
    for test_name, test_func in tests:
        print()
        gc.collect()  # Limpeza de memória
        
        try:
            success = test_func()
            if success:
                results[test_name] = "✅ OK"
                passed += 1
            else:
                results[test_name] = "❌ FALHA"
        except Exception as e:
            results[test_name] = f"💥 ERRO: {str(e)}"
            print(f"💥 Exceção em {test_name}: {e}")
    
    # Resumo final
    elapsed = time.time() - start_time
    final_mem = measure_memory()
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DO BENCHMARK")
    print("=" * 50)
    
    for test_name, result in results.items():
        print(f"  {result} {test_name}")
    
    print(f"\n🏆 Testes passaram: {passed}/{len(tests)}")
    print(f"⏱️  Tempo total: {elapsed:.2f}s")
    print(f"📊 Memória inicial: {start_mem:.1f} MB")
    print(f"📊 Memória final: {final_mem:.1f} MB")
    print(f"📈 Delta memória: {final_mem - start_mem:+.1f} MB")
    
    if passed == len(tests):
        print("🎉 Todos os benchmarks foram concluídos!")
        return True
    else:
        print("⚠️  Alguns benchmarks falharam")
        return False

if __name__ == "__main__":
    success = run_performance_tests()
    sys.exit(0 if success else 1)