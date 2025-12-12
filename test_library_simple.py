#!/usr/bin/env python3
"""
Teste Simples da Biblioteca TOFcam
=================================

Teste básico da nova biblioteca sem interface gráfica.
"""

import cv2
import numpy as np
import time

# Importar componentes da biblioteca centralizada
from tofcam.lib import (
    NavigationMode,
    create_camera_manager, discover_cameras,
    create_depth_estimator,
    create_navigator,
    create_render_pipeline,
    logger
)

def main():
    """Teste simples sem GUI"""
    try:
        logger.info("🚀 Iniciando teste da biblioteca TOFcam...")
        
        # 1. Teste de descoberta de câmeras
        logger.info("📹 Testando descoberta de câmeras...")
        cameras = discover_cameras()
        logger.info(f"✅ Câmeras encontradas: {cameras}")
        
        # 2. Teste do camera manager
        logger.info("📹 Testando camera manager...")
        camera_manager = create_camera_manager()
        logger.info("✅ Camera manager criado")
        
        # 3. Teste do depth estimator
        logger.info("🧠 Testando depth estimator...")
        depth_estimator = create_depth_estimator()
        logger.info("✅ Depth estimator criado")
        
        # 4. Teste do navigator
        logger.info("🧭 Testando navigator...")
        navigator = create_navigator()
        logger.info("✅ Navigator criado")
        
        # 5. Teste do render pipeline
        logger.info("🎨 Testando render pipeline...")
        render_pipeline = create_render_pipeline()
        logger.info("✅ Render pipeline criado")
        
        # 6. Teste com imagem sintética
        logger.info("🖼️  Testando com imagem sintética...")
        
        # Criar uma imagem de teste
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        logger.info(f"📐 Imagem de teste: {test_image.shape}")
        
        # Estimar profundidade
        start_time = time.time()
        depth_map = depth_estimator.estimate_depth(test_image)
        depth_time = time.time() - start_time
        logger.info(f"✅ Profundidade estimada: {depth_map.shape}, tempo: {depth_time:.3f}s")
        
        # Navegação
        start_time = time.time()
        nav_result = navigator.navigate(depth_map, NavigationMode.HYBRID)
        nav_time = time.time() - start_time
        logger.info(f"✅ Navegação calculada, tempo: {nav_time:.3f}s")
        
        # Imprimir resultados de navegação
        if nav_result.strategic:
            logger.info(f"📊 Estratégico - Yaw: {np.rad2deg(nav_result.strategic.target_yaw_delta):.1f}°, "
                       f"Confiança: {nav_result.strategic.confidence:.3f}")
        
        if nav_result.reactive:
            logger.info(f"⚡ Reativo - Urgência: {nav_result.reactive.urgency:.3f}, "
                       f"Emergência: {nav_result.reactive.emergency_brake}")
        
        # Renderização (sem mostrar)
        start_time = time.time()
        zone_grid = navigator.zone_mapper.create_strategic_grid(depth_map)
        visualization = render_pipeline.render_complete_view(depth_map, zone_grid, nav_result)
        render_time = time.time() - start_time
        logger.info(f"✅ Visualização renderizada: {visualization.shape}, tempo: {render_time:.3f}s")
        
        # Salvar resultado (opcional)
        output_path = "/tmp/tofcam_test_result.jpg"
        cv2.imwrite(output_path, visualization)
        logger.info(f"💾 Resultado salvo em: {output_path}")
        
        logger.info("🎉 Todos os testes passaram com sucesso!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("📋 A biblioteca tofcam.lib está funcionando corretamente")
    else:
        print("\n❌ TESTE FALHOU!")
        print("📋 Verifique os logs para mais detalhes")