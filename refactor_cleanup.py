#!/usr/bin/env python3
"""
Script de Refatoração - Eliminar Código Duplicado
================================================

Remove arquivos obsoletos e refatora os restantes para usar tofcam.lib.
"""

import os
import shutil

def main():
    print("🔄 Refatorando projeto para usar 100% tofcam.lib...")
    
    # Criar pasta de backup
    backup_dir = "old_code_backup"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"📁 Criada pasta de backup: {backup_dir}")
    
    # Lista de arquivos duplicados para mover para backup
    duplicated_files = [
        "camera.py",           # Duplicado de tofcam.lib.camera
        "depth_estimator.py",  # Duplicado de tofcam.lib.depth  
        "mapping.py",          # Duplicado de tofcam.lib.navigation
        "view.py",             # Duplicado de tofcam.lib.visualization
        "tofcam_types.py",     # Duplicado de tofcam.lib.config
        "modules.py",          # Código antigo obsoleto
        "analyzer_lib.py",     # Usar main_analyzer_lib.py refatorado
        "web_viewer.py",       # Duplicado de tofcam.lib.web
        "web_viewer_lib.py"    # Usar tofcam.lib.web
    ]
    
    print("\n📦 Movendo arquivos duplicados para backup...")
    for file in duplicated_files:
        if os.path.exists(file):
            try:
                shutil.move(file, os.path.join(backup_dir, file))
                print(f"  ✅ {file} -> {backup_dir}/")
            except Exception as e:
                print(f"  ❌ Erro movendo {file}: {e}")
        else:
            print(f"  ℹ️  {file} não encontrado")
    
    # Verificar arquivos que precisam ser refatorados (não duplicados)
    files_to_refactor = [
        "main_analyzer.py",
        "main_analyzer_lib.py", 
        "setup_display.py"
    ]
    
    print(f"\n🔧 Arquivos que precisam refatoração:")
    for file in files_to_refactor:
        if os.path.exists(file):
            print(f"  📝 {file}")
        else:
            print(f"  ❌ {file} não encontrado")
    
    # Listar arquivos restantes na raiz
    remaining_files = []
    for file in os.listdir("."):
        if file.endswith(".py") and os.path.isfile(file):
            remaining_files.append(file)
    
    print(f"\n📋 Arquivos Python restantes na raiz:")
    for file in sorted(remaining_files):
        print(f"  📄 {file}")
    
    print("\n✅ Refatoração de estrutura concluída!")
    print("📋 Próximos passos:")
    print("  1. ✅ main.py - já refatorado")
    print("  2. ✅ run.py - já refatorado") 
    print("  3. 📝 Refatorar main_analyzer.py e main_analyzer_lib.py")
    print("  4. 📝 Refatorar setup_display.py")
    print("  5. 🧪 Testar todos os arquivos refatorados")

if __name__ == "__main__":
    main()