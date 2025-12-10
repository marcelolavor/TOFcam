import cv2
import numpy as np
from enum import IntEnum

# Cores para células: (B, G, R)
COLOR_FREE      = (0, 255, 0)
COLOR_WARNING   = (0, 255, 255)
COLOR_EMERGENCY = (0, 0, 255)

def depth_to_color(depth: np.ndarray) -> np.ndarray:
    """
    Converte profundidade normalizada [0..1] para mapa colorido intuitivo.
    
    Convenção intuitiva com JET invertido:
    - 🔴 Vermelho: Perto/Perigoso (valores baixos de profundidade) 
    - 🟡 Amarelo: Médio/Atenção (valores intermediários)
    - 🟢 Verde: Intermediário
    - 🔵 Azul: Longe/Seguro (valores altos de profundidade)
    
    JET invertido oferece maior contraste e gradiente mais técnico.
    """
    # Inverter a profundidade para mapeamento intuitivo
    # depth=0 (perto) -> vermelho, depth=1 (longe) -> azul
    inverted_depth = 1.0 - depth
    
    # JET invertido fornece vermelho->amarelo->verde->azul
    d = (inverted_depth * 255).astype(np.uint8)
    colored = cv2.applyColorMap(d, cv2.COLORMAP_JET)
    
    return colored


def draw_zone_grid(image: np.ndarray, zone_grid, roi, thickness=1):
    """
    Desenha o grid de zonas e colore conforme estado.
    'image' deve ter o mesmo tamanho da imagem original.
    'roi' = (y0_rel, y1_rel, x0_rel, x1_rel) relativos.
    """
    h, w = image.shape[:2]
    y0 = int(roi[0] * h)
    y1 = int(roi[1] * h)
    x0 = int(roi[2] * w)
    x1 = int(roi[3] * w)

    gh, gw = zone_grid.grid_h, zone_grid.grid_w
    cell_h = (y1 - y0) // gh
    cell_w = (x1 - x0) // gw

    overlay = image.copy()

    for i in range(gh):
        for j in range(gw):
            cell = zone_grid.cells[i, j]

            yy0 = y0 + i * cell_h
            yy1 = y0 + (i + 1) * cell_h
            xx0 = x0 + j * cell_w
            xx1 = x0 + (j + 1) * cell_w

            if cell.state == 0:       # FREE
                color = COLOR_FREE
            elif cell.state == 1:     # WARNING
                color = COLOR_WARNING
            else:                     # EMERGENCY
                color = COLOR_EMERGENCY

            cv2.rectangle(overlay, (xx0, yy0), (xx1, yy1), color, -1)

    # mistura: 60% imagem, 40% overlay
    blended = cv2.addWeighted(image, 0.6, overlay, 0.4, 0)
    
    # desenha linhas do grid
    for i in range(gh + 1):
        yy = y0 + i * cell_h
        cv2.line(blended, (x0, yy), (x1, yy), (255, 255, 255), thickness)
    for j in range(gw + 1):
        xx = x0 + j * cell_w
        cv2.line(blended, (xx, y0), (xx, y1), (255, 255, 255), thickness)

    return blended

def draw_yaw_arrow(image, yaw_delta, length=150, color=(0, 255, 255), label=""):
    """
    Desenha uma seta representando a direção de yaw recomendada.
    
    Args:
        image: Imagem onde desenhar a seta
        yaw_delta: Ângulo em radianos (+ esquerda, - direita)
        length: Comprimento da seta em pixels
        color: Cor da seta (B, G, R)
        label: Texto opcional para identificar a seta
    
    Returns:
        Imagem com a seta desenhada
    """
    h, w = image.shape[:2]
    
    # Ponto de origem da seta no centro inferior
    x0 = w // 2
    y0 = int(h * 0.9)
    
    # Converter yaw_delta (rad) em ângulo 2D
    # Se yaw = 0, seta aponta para cima (-90 graus)
    # Correção: inverter sinal para direção correta
    angle = -np.pi/2 - yaw_delta  # Negativo para corrigir direção
    
    x1 = int(x0 + length * np.cos(angle))
    y1 = int(y0 + length * np.sin(angle))
    
    # Desenhar a seta
    cv2.arrowedLine(image, (x0, y0), (x1, y1), color, 4, tipLength=0.3)
    
    # Desenhar círculo na base para destacar
    cv2.circle(image, (x0, y0), 8, color, -1)
    
    # Adicionar texto se fornecido
    if label:
        # Posição do texto ao lado da base da seta
        text_x = x0 + 15
        text_y = y0 - 10
        cv2.putText(image, label, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Adicionar valor do ângulo
    angle_text = f"{np.degrees(yaw_delta):.1f}°"
    cv2.putText(image, angle_text, (x0 - 30, y0 + 25), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    return image
