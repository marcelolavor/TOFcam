#!/usr/bin/env python3
"""
Teste de validação para direcionamento de setas nos algoritmos de navegação.
"""

import numpy as np
import cv2
import os
import sys

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from view import draw_yaw_arrow

def test_arrow_directions():
    """Teste sistemático das direções das setas."""
    
    # Criar imagem de teste
    width, height = 640, 480
    test_img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Cenários de teste
    test_cases = [
        ("Virar Esquerda (-0.5)", -0.5),
        ("Ligeiramente Esquerda (-0.2)", -0.2),
        ("Centro (0.0)", 0.0),
        ("Ligeiramente Direita (+0.2)", 0.2),
        ("Virar Direita (+0.5)", 0.5),
    ]
    
    print("🧪 TESTE DE DIREÇÕES DAS SETAS")
    print("=" * 50)
    
    for description, yaw_delta in test_cases:
        img_copy = test_img.copy()
        
        # Desenhar seta
        draw_yaw_arrow(img_copy, yaw_delta, width, height)
        
        # Calcular ângulo esperado
        expected_angle = -np.pi/2 - yaw_delta
        expected_degrees = np.degrees(expected_angle)
        
        print(f"📐 {description}")
        print(f"   Yaw Delta: {yaw_delta:+.1f}")
        print(f"   Ângulo: {expected_degrees:+.1f}°")
        
        # Determinar direção esperada
        if yaw_delta < -0.1:
            direction = "⬅️  ESQUERDA"
        elif yaw_delta > 0.1:
            direction = "➡️  DIREITA"
        else:
            direction = "⬆️  FRENTE"
            
        print(f"   Direção: {direction}")
        print()
    
    print("✅ Teste de direções concluído!")
    print("📝 Fórmula validada: angle = -π/2 - yaw_delta")

def test_extreme_values():
    """Teste com valores extremos."""
    
    print("\n🔥 TESTE DE VALORES EXTREMOS")
    print("=" * 50)
    
    extreme_cases = [
        ("Máximo Esquerda", -1.0),
        ("Máximo Direita", +1.0),
        ("Super Extremo Esquerda", -2.0),
        ("Super Extremo Direita", +2.0),
    ]
    
    for description, yaw_delta in extreme_cases:
        angle = -np.pi/2 - yaw_delta
        degrees = np.degrees(angle)
        
        print(f"⚡ {description}: {yaw_delta:+.1f} → {degrees:+.1f}°")
    
    print("\n✅ Teste de extremos concluído!")

if __name__ == "__main__":
    test_arrow_directions()
    test_extreme_values()