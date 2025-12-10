#!/usr/bin/env python3
"""
Gerenciador Interativo de Testes TOFcam
Sistema de testes organizado por categorias com execução interativa
"""

import sys
import os
import subprocess
import time
from typing import Dict, List, Tuple

class TestManager:
    """Gerenciador de testes TOFcam"""
    
    def __init__(self):
        self.tests_dir = os.path.dirname(__file__)
        self.tests = self._discover_tests()
        
    def _discover_tests(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """Descobrir todos os testes disponíveis organizados por categoria"""
        tests = {
            "📹 Hardware": [
                ("test_cameras.py", "Testa acesso às câmeras", "Verificar câmeras disponíveis"),
                ("test_camera0_only.py", "Teste específico câmera 0", "Validar funcionamento câmera 0"),
                ("test_camera2.py", "Teste específico câmera 2", "Validar funcionamento câmera 2"),
                ("test_usb_camera.py", "Teste câmeras USB", "Detectar e testar câmeras USB"),
            ],
            "🧠 Algoritmos": [
                ("test_algorithms.py", "Teste algoritmos navegação", "Validar Strategic e Reactive"),
                ("test_arrows.py", "Teste setas direção", "Verificar cálculo de direções"),
            ],
            "🌐 Interface": [
                ("test_image_server.py", "Teste servidor imagens", "Validar streaming web"),
            ],
            "🧪 Biblioteca": [
                ("../demo_lib.py", "Demo biblioteca centralizada", "Testar diferentes configurações"),
                ("../main_analyzer_lib.py", "Analyzer biblioteca", "Teste análise com persistência"),
                ("../web_viewer_lib.py", "Web viewer biblioteca", "Teste interface web refatorada"),
            ],
        }
        
        # Filtrar apenas testes que existem
        filtered_tests = {}
        for category, test_list in tests.items():
            existing_tests = []
            for test_file, desc, purpose in test_list:
                test_path = os.path.join(self.tests_dir, test_file)
                if os.path.exists(test_path):
                    existing_tests.append((test_file, desc, purpose))
            if existing_tests:
                filtered_tests[category] = existing_tests
                
        return filtered_tests
    
    def show_menu(self) -> None:
        """Exibir menu principal"""
        print("🧪 Gerenciador de Testes TOFcam")
        print("=" * 60)
        
        test_index = 1
        for category, test_list in self.tests.items():
            print(f"\n{category}:")
            for test_file, desc, purpose in test_list:
                print(f"  {test_index:2d}. {desc}")
                print(f"      📝 {purpose}")
                print(f"      📄 {test_file}")
                test_index += 1
        
        print(f"\n🎯 Opções especiais:")
        print(f"  {test_index:2d}. Executar todos os testes")
        print(f"  {test_index + 1:2d}. Executar por categoria")
        print(f"   0. Sair")
        
    def get_all_tests(self) -> List[Tuple[str, str, str]]:
        """Obter lista de todos os testes"""
        all_tests = []
        for test_list in self.tests.values():
            all_tests.extend(test_list)
        return all_tests
    
    def run_test(self, test_file: str, desc: str) -> bool:
        """Executar um teste específico"""
        print(f"\n🚀 Executando: {desc}")
        print("-" * 50)
        
        test_path = os.path.join(self.tests_dir, test_file)
        
        try:
            # Verificar se precisa ativar conda
            if test_file.endswith('.py'):
                # Executar com conda activate se disponível
                cmd = f"cd {os.path.dirname(test_path)} && conda activate opencv 2>/dev/null && python {os.path.basename(test_path)} || python {os.path.basename(test_path)}"
                result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
                
                if result.returncode == 0:
                    print(f"\n✅ {desc}: PASSOU")
                    return True
                else:
                    print(f"\n❌ {desc}: FALHOU (código {result.returncode})")
                    return False
            else:
                print(f"⚠️ Arquivo {test_file} não é um script Python válido")
                return False
                
        except Exception as e:
            print(f"\n❌ Erro ao executar {desc}: {e}")
            return False
    
    def run_category(self, category: str) -> Tuple[int, int]:
        """Executar todos os testes de uma categoria"""
        print(f"\n🎯 Executando categoria: {category}")
        print("=" * 60)
        
        passed = 0
        total = 0
        
        for test_file, desc, purpose in self.tests[category]:
            total += 1
            if self.run_test(test_file, desc):
                passed += 1
            print()  # Linha em branco entre testes
            
        return passed, total
    
    def run_all_tests(self) -> None:
        """Executar todos os testes"""
        print("\n🚀 Executando TODOS os testes...")
        print("=" * 60)
        
        start_time = time.time()
        total_passed = 0
        total_tests = 0
        
        for category in self.tests:
            passed, count = self.run_category(category)
            total_passed += passed
            total_tests += count
            print()
        
        # Resultado final
        elapsed = time.time() - start_time
        print("=" * 60)
        print(f"🏁 RESULTADO FINAL:")
        print(f"   ✅ Passou: {total_passed}/{total_tests}")
        print(f"   ⏱️ Tempo: {elapsed:.2f}s")
        
        if total_passed == total_tests:
            print("   🎉 Todos os testes passaram!")
        else:
            print(f"   ⚠️ {total_tests - total_passed} teste(s) falharam")
    
    def run_interactive(self) -> None:
        """Modo interativo"""
        while True:
            self.show_menu()
            
            try:
                choice = input("\n👉 Escolha uma opção: ").strip()
                
                if choice == "0":
                    print("👋 Saindo...")
                    break
                
                choice_num = int(choice)
                all_tests = self.get_all_tests()
                
                if choice_num == len(all_tests) + 1:
                    # Executar todos
                    self.run_all_tests()
                elif choice_num == len(all_tests) + 2:
                    # Executar por categoria
                    self.category_menu()
                elif 1 <= choice_num <= len(all_tests):
                    # Executar teste específico
                    test_file, desc, purpose = all_tests[choice_num - 1]
                    self.run_test(test_file, desc)
                else:
                    print("❌ Opção inválida!")
                
            except ValueError:
                print("❌ Por favor, digite um número!")
            except KeyboardInterrupt:
                print("\n\n👋 Interrompido pelo usuário")
                break
            
            input("\n⏸️  Pressione Enter para continuar...")
            print("\n" * 2)  # Limpar tela
    
    def category_menu(self) -> None:
        """Menu de seleção de categoria"""
        print("\n📂 Escolha uma categoria:")
        print("-" * 30)
        
        categories = list(self.tests.keys())
        for i, category in enumerate(categories, 1):
            test_count = len(self.tests[category])
            print(f"  {i}. {category} ({test_count} testes)")
        
        try:
            choice = int(input("\n👉 Categoria: "))
            if 1 <= choice <= len(categories):
                category = categories[choice - 1]
                passed, total = self.run_category(category)
                print(f"\n📊 Categoria {category}: {passed}/{total} testes passaram")
            else:
                print("❌ Categoria inválida!")
        except ValueError:
            print("❌ Por favor, digite um número!")

def main():
    """Função principal"""
    manager = TestManager()
    
    if len(sys.argv) > 1:
        # Modo não-interativo
        if sys.argv[1] == "--all":
            manager.run_all_tests()
        elif sys.argv[1] == "--list":
            print("📋 Testes disponíveis:")
            for category, tests in manager.tests.items():
                print(f"\n{category}:")
                for test_file, desc, purpose in tests:
                    print(f"  • {test_file}: {desc}")
        else:
            print("❌ Uso: python run_tests.py [--all|--list]")
    else:
        # Modo interativo
        manager.run_interactive()

if __name__ == "__main__":
    main()