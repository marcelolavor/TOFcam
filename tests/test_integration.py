#!/usr/bin/env python3
"""
Teste de integração completo do sistema TOFcam
Verifica se todos os componentes trabalham bem juntos
"""

import sys
import os
import numpy as np
import time

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_module_imports():
    """Testar importação de todos os módulos principais"""
    print("🔍 Testando importações de módulos...")
    
    modules_to_test = [
        ("camera", "CameraSource"),
        ("depth_estimator", "MidasDepthEstimator"), 
        ("mapping", "ZoneMapper"),
        ("view", "depth_to_color"),
        ("tofcam.nav", "StrategicPlanner"),
        ("tofcam.nav", "ReactiveAvoider"),
        ("tofcam.core", "TOFAnalyzer"),
        ("analyzer_lib", "AnalysisConfig"),
    ]
    
    failed = 0
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  ✅ {module_name}.{class_name}")
        except Exception as e:
            print(f"  ❌ {module_name}.{class_name}: {e}")
            failed += 1
    
    success = failed == 0
    print(f"  📊 {len(modules_to_test) - failed}/{len(modules_to_test)} módulos importados")
    return success

def test_camera_detection():
    """Testar detecção de câmeras"""
    print("\n📹 Testando detecção de câmeras...")
    
    try:
        from camera import CameraSource
        
        # Testar câmera 0
        camera = CameraSource(index=0)
        success = camera.open()
        
        if success:
            frame = camera.read()
            if frame is not None:
                print(f"  ✅ Câmera funcional: {frame.shape}")
                return True, [0]
            else:
                print("  ❌ Não foi possível capturar frame")
                return False, []
        else:
            print("  ❌ Não foi possível abrir câmera")
            return False, []
            
    except Exception as e:
        print(f"  ❌ Erro na detecção: {e}")
        return False, []

def test_depth_estimation():
    """Testar estimativa de profundidade com dados sintéticos"""
    print("\n🧠 Testando estimativa de profundidade...")
    
    try:
        from depth_estimator import MidasDepthEstimator
        
        # Criar imagem sintética
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Tentar criar estimador (sem carregar o modelo)
        print("  🔧 Testando apenas a estrutura do estimador...")
        estimator = MidasDepthEstimator()
        print("  ✅ Estrutura do estimador funcionando")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def test_navigation_algorithms():
    """Testar algoritmos de navegação"""
    print("\n🧭 Testando algoritmos de navegação...")
    
    try:
        from tofcam.nav import StrategicPlanner, ReactiveAvoider, ZoneMapper
        
        # Criar mapa de profundidade sintético
        depth_map = np.random.uniform(0.1, 5.0, (480, 640)).astype(np.float32)
        
        # Criar componentes
        zone_mapper = ZoneMapper(grid_h=6, grid_w=8)
        strategic = StrategicPlanner()
        reactive = ReactiveAvoider()
        
        # Processar
        zone_grid = zone_mapper.map_depth_to_zones(depth_map)
        strategic_result = strategic.plan(zone_grid)
        reactive_result = reactive.compute(zone_grid)
        
        print(f"  ✅ Strategic: {np.rad2deg(strategic_result.target_yaw_delta):.1f}°")
        print(f"  ✅ Reactive: {np.rad2deg(reactive_result.yaw_delta):.1f}°")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def test_visualization():
    """Testar componentes de visualização"""
    print("\n🎨 Testando visualização...")
    
    try:
        from view import depth_to_color, draw_yaw_arrow
        import cv2
        
        # Dados sintéticos
        depth_map = np.random.uniform(0.1, 5.0, (240, 320)).astype(np.float32)
        
        # Testar colorização
        colored = depth_to_color(depth_map)
        print(f"  ✅ Mapa colorizado: {colored.shape}")
        
        # Testar seta
        canvas = np.zeros((240, 320, 3), dtype=np.uint8)
        with_arrow = draw_yaw_arrow(canvas, 0.5)  # 0.5 radianos
        print(f"  ✅ Seta desenhada: {with_arrow.shape}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def test_tofcam_package():
    """Testar pacote tofcam"""
    print("\n📦 Testando pacote tofcam...")
    
    try:
        import tofcam
        from tofcam.core import TOFAnalyzer, AnalysisConfig
        
        # Testar configuração
        config = AnalysisConfig()
        print(f"  ✅ Configuração criada: {config}")
        
        print("  ✅ Pacote tofcam funcional")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def run_integration_tests():
    """Executar todos os testes de integração"""
    print("🔬 TESTE DE INTEGRAÇÃO TOFcam")
    print("=" * 50)
    
    start_time = time.time()
    
    # Executar testes
    tests = [
        ("Importações de Módulos", test_module_imports),
        ("Detecção de Câmeras", test_camera_detection),
        ("Estimativa de Profundidade", test_depth_estimation),
        ("Algoritmos de Navegação", test_navigation_algorithms),
        ("Visualização", test_visualization),
        ("Pacote TOFcam", test_tofcam_package),
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            if result == True or (isinstance(result, tuple) and result[0] == True):
                results[test_name] = "✅ PASSOU"
                passed += 1
            else:
                results[test_name] = "❌ FALHOU"
        except Exception as e:
            print(f"  💥 Exceção: {e}")
            results[test_name] = f"💥 ERRO: {e}"
    
    # Resumo final
    elapsed = time.time() - start_time
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES DE INTEGRAÇÃO")
    print("=" * 50)
    
    for test_name, result in results.items():
        print(f"  {result} {test_name}")
    
    print(f"\n🏆 Resultado: {passed}/{total} testes passaram")
    print(f"⏱️  Tempo total: {elapsed:.2f}s")
    
    if passed == total:
        print("🎉 Sistema totalmente integrado!")
        return True
    else:
        print("⚠️  Algumas integrações falharam")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)