#!/usr/bin/env python3
"""
Demo Manager - Sistema Interativo de Demonstrações

Gerenciador central para todos os demos e exemplos do projeto TOFcam.
"""

import os
import sys
import subprocess

class DemoManager:
    """Gerenciador interativo de demonstrações."""
    
    def __init__(self):
        self.demos_dir = os.path.dirname(os.path.abspath(__file__))
        self.demos = {
            "Biblioteca Centralizada": [
                ("library/demo_lib.py", "Demo configurações biblioteca", "Demonstra diferentes configurações da analyzer_lib.py"),
            ],
            "Algoritmos & Comparação": [
                ("basic_usage.py", "Uso básico - Biblioteca", "Análise em tempo real usando biblioteca centralizada"),
                ("algorithm_comparison.py", "Comparação algoritmos", "Comparação visual Strategic vs Reactive vs Biblioteca"),
            ],
            "Interface & Cameras": [
                ("camera_selection/camera_selector.py", "Seleção de câmeras", "Interface web para testar diferentes câmeras"),
            ],
        }
    
    def display_menu(self):
        """Exibir menu principal."""
        print("\n" + "=" * 60)
        print("🎬 TOFCAM - GERENCIADOR DE DEMONSTRAÇÕES")
        print("=" * 60)
        
        demo_count = 1
        for category, items in self.demos.items():
            print(f"\n📁 {category}:")
            for file_path, name, description in items:
                print(f"  {demo_count}. {name}")
                print(f"     📝 {description}")
                demo_count += 1
        
        print(f"\n  0. ❌ Sair")
        print("=" * 60)
    
    def run_demo(self, demo_number):
        """Executar demo específico."""
        current_num = 1
        for category, items in self.demos.items():
            for file_path, name, description in items:
                if current_num == demo_number:
                    full_path = os.path.join(self.demos_dir, file_path)
                    if os.path.exists(full_path):
                        print(f"\n🚀 Executando: {name}")
                        print(f"📁 Arquivo: {file_path}")
                        print(f"📝 Descrição: {description}")
                        print("-" * 50)
                        
                        try:
                            # Executar demo
                            result = subprocess.run([sys.executable, full_path], 
                                                  cwd=os.path.dirname(full_path),
                                                  check=False)
                            print(f"\n✅ Demo finalizado com código: {result.returncode}")
                        except KeyboardInterrupt:
                            print(f"\n🛑 Demo interrompido pelo usuário")
                        except Exception as e:
                            print(f"\n❌ Erro ao executar demo: {e}")
                    else:
                        print(f"\n❌ Arquivo não encontrado: {full_path}")
                    return True
                current_num += 1
        return False
    
    def run(self):
        """Executar gerenciador interativo."""
        while True:
            self.display_menu()
            
            try:
                choice = input("\n👉 Escolha um demo (0-{} ou Enter para sair): ".format(
                    sum(len(items) for items in self.demos.values())
                )).strip()
                
                if not choice:
                    print("👋 Saindo do gerenciador de demos...")
                    break
                
                if choice == '0':
                    print("👋 Saindo do gerenciador de demos...")
                    break
                
                demo_num = int(choice)
                if demo_num < 1 or demo_num > sum(len(items) for items in self.demos.values()):
                    print("❌ Número inválido!")
                    continue
                
                if not self.run_demo(demo_num):
                    print("❌ Demo não encontrado!")
                
                # Aguardar antes de mostrar menu novamente
                input("\n📤 Pressione Enter para voltar ao menu...")
                
            except ValueError:
                print("❌ Por favor, digite um número válido!")
            except KeyboardInterrupt:
                print("\n👋 Saindo...")
                break

if __name__ == "__main__":
    manager = DemoManager()
    manager.run()