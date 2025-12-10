#!/usr/bin/env python3
"""
Teste de comparação entre algoritmos Strategic e Reactive.
"""

import numpy as np
import sys
import os

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mapping import StrategicNavigationAlgorithm, ReactiveAvoidanceAlgorithm

def create_test_depth_map(scenario):
    """Criar mapas de profundidade para cenários específicos."""
    
    depth_map = np.ones((480, 640), dtype=np.float32) * 5.0  # Distância padrão: 5m
    
    if scenario == "obstacle_left":
        # Obstáculo à esquerda
        depth_map[:, :200] = 0.5  # Parede próxima à esquerda
        
    elif scenario == "obstacle_right":
        # Obstáculo à direita  
        depth_map[:, 440:] = 0.8  # Parede próxima à direita
        
    elif scenario == "obstacle_center":
        # Obstáculo no centro
        depth_map[200:280, 270:370] = 0.3  # Obstáculo central
        
    elif scenario == "corridor":
        # Corredor estreito
        depth_map[:, :100] = 0.5   # Parede esquerda
        depth_map[:, 540:] = 0.5   # Parede direita
        
    elif scenario == "clear_path":
        # Caminho livre
        pass  # Mantém distâncias padrão
        
    return depth_map

def test_algorithm_comparison():
    """Comparar comportamento dos algoritmos Strategic vs Reactive."""
    
    print("🔄 COMPARAÇÃO DE ALGORITMOS")
    print("=" * 60)
    
    # Inicializar algoritmos
    strategic = StrategicNavigationAlgorithm()
    reactive = ReactiveAvoidanceAlgorithm()
    
    # Cenários de teste
    scenarios = [
        ("clear_path", "🛤️  Caminho Livre"),
        ("obstacle_left", "🧱 Obstáculo à Esquerda"),
        ("obstacle_right", "🧱 Obstáculo à Direita"),
        ("obstacle_center", "🎯 Obstáculo Central"),
        ("corridor", "🚇 Corredor Estreito"),
    ]
    
    for scenario_key, description in scenarios:
        print(f"\n{description}")
        print("-" * 40)
        
        # Criar mapa de profundidade
        depth_map = create_test_depth_map(scenario_key)
        
        # Processar com ambos algoritmos
        strategic_result = strategic.process(depth_map)
        reactive_result = reactive.process(depth_map)
        
        # Resultados
        strategic_yaw = strategic_result['yaw_delta']
        reactive_yaw = reactive_result['yaw_delta']
        
        print(f"📊 Strategic: {strategic_yaw:+.3f}°")
        print(f"⚡ Reactive:  {reactive_yaw:+.3f}°")
        
        # Análise da diferença
        diff = abs(strategic_yaw - reactive_yaw)
        if diff < 0.1:
            agreement = "✅ CONCORDAM"
        elif diff < 0.5:
            agreement = "🟡 SIMILAR"
        else:
            agreement = "🔴 DIVERGEM"
            
        print(f"📈 Diferença: {diff:.3f}° - {agreement}")
        
        # Interpretação dos resultados
        if strategic_yaw > 0.2:
            strategic_dir = "➡️ Direita"
        elif strategic_yaw < -0.2:
            strategic_dir = "⬅️ Esquerda"
        else:
            strategic_dir = "⬆️ Frente"
            
        if reactive_yaw > 0.2:
            reactive_dir = "➡️ Direita"
        elif reactive_yaw < -0.2:
            reactive_dir = "⬅️ Esquerda"
        else:
            reactive_dir = "⬆️ Frente"
            
        print(f"🧭 Strategic sugere: {strategic_dir}")
        print(f"⚡ Reactive sugere: {reactive_dir}")

def test_edge_cases():
    """Testar casos extremos."""
    
    print("\n\n🔥 TESTE DE CASOS EXTREMOS")
    print("=" * 60)
    
    strategic = StrategicNavigationAlgorithm()
    reactive = ReactiveAvoidanceAlgorithm()
    
    # Casos extremos
    edge_cases = [
        ("all_close", "Tudo muito próximo (0.1m)"),
        ("all_far", "Tudo muito distante (50m)"),
        ("gradient_left", "Gradiente da esquerda para direita"),
        ("gradient_right", "Gradiente da direita para esquerda"),
    ]
    
    for case_key, description in edge_cases:
        print(f"\n{description}")
        print("-" * 30)
        
        # Criar mapas específicos
        if case_key == "all_close":
            depth_map = np.ones((480, 640), dtype=np.float32) * 0.1
        elif case_key == "all_far":
            depth_map = np.ones((480, 640), dtype=np.float32) * 50.0
        elif case_key == "gradient_left":
            depth_map = np.tile(np.linspace(0.5, 5.0, 640), (480, 1)).astype(np.float32)
        elif case_key == "gradient_right":
            depth_map = np.tile(np.linspace(5.0, 0.5, 640), (480, 1)).astype(np.float32)
        
        strategic_result = strategic.process(depth_map)
        reactive_result = reactive.process(depth_map)
        
        print(f"📊 Strategic: {strategic_result['yaw_delta']:+.3f}°")
        print(f"⚡ Reactive:  {reactive_result['yaw_delta']:+.3f}°")

if __name__ == "__main__":
    test_algorithm_comparison()
    test_edge_cases()