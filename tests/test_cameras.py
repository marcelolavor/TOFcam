#!/usr/bin/env python3
"""
Script para testar acesso às câmeras disponíveis
"""
import cv2
import sys

def test_camera_access():
    print("🔍 Testando acesso às câmeras...")
    print("=" * 50)
    
    available_cameras = []
    
    # Testar índices de 0 a 5
    for camera_index in range(6):
        print(f"\n📹 Testando /dev/video{camera_index}...")
        
        try:
            # Tentar abrir a câmera
            cap = cv2.VideoCapture(camera_index)
            
            if cap.isOpened():
                # Tentar ler um frame
                ret, frame = cap.read()
                
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    print(f"✅ Câmera {camera_index} FUNCIONANDO!")
                    print(f"   📐 Resolução: {width}x{height}")
                    print(f"   📊 Tipo: {frame.dtype}")
                    available_cameras.append({
                        'index': camera_index,
                        'width': width,
                        'height': height,
                        'status': 'working'
                    })
                else:
                    print(f"⚠️ Câmera {camera_index} abre mas não retorna frames")
                    available_cameras.append({
                        'index': camera_index,
                        'status': 'no_frames'
                    })
            else:
                print(f"❌ Não foi possível abrir câmera {camera_index}")
                
            cap.release()
            
        except Exception as e:
            print(f"❌ Erro ao testar câmera {camera_index}: {e}")
    
    print(f"\n" + "=" * 50)
    print("📊 RESUMO:")
    
    if available_cameras:
        working_cameras = [cam for cam in available_cameras if cam.get('status') == 'working']
        
        if working_cameras:
            print(f"✅ {len(working_cameras)} câmera(s) funcionando:")
            for cam in working_cameras:
                print(f"   📹 Câmera {cam['index']}: {cam['width']}x{cam['height']}")
            return working_cameras
        else:
            print("⚠️ Câmeras encontradas mas sem frames válidos")
            return []
    else:
        print("❌ Nenhuma câmera acessível encontrada")
        return []

def test_specific_camera(camera_index):
    """Teste detalhado de uma câmera específica"""
    print(f"\n🎯 Teste detalhado da câmera {camera_index}")
    print("-" * 30)
    
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print("❌ Falha ao abrir câmera")
        return False
    
    # Obter propriedades da câmera
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"📐 Resolução: {width}x{height}")
    print(f"🎬 FPS: {fps}")
    
    # Testar captura de alguns frames
    frames_captured = 0
    for i in range(5):
        ret, frame = cap.read()
        if ret and frame is not None:
            frames_captured += 1
            if i == 0:  # Salvar primeiro frame
                cv2.imwrite(f"/tmp/camera_{camera_index}_test.jpg", frame)
                print(f"💾 Frame de teste salvo: /tmp/camera_{camera_index}_test.jpg")
    
    cap.release()
    print(f"📊 Frames capturados: {frames_captured}/5")
    
    return frames_captured > 0

if __name__ == "__main__":
    available = test_camera_access()
    
    # Testar a primeira câmera funcionando em detalhes
    if available:
        best_camera = available[0]
        print(f"\n🚀 Testando câmera {best_camera['index']} em detalhes...")
        test_specific_camera(best_camera['index'])
    else:
        print("\n💡 Sugestões:")
        print("1. Verificar se o usuário está no grupo 'video':")
        print("   sudo usermod -a -G video $USER")
        print("2. Fazer logout/login para aplicar mudanças de grupo")
        print("3. Verificar se há uma webcam conectada")
        print("4. Tentar executar com sudo temporariamente para teste")