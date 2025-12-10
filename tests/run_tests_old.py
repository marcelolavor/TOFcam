#!/usr/bin/env python3
"""
Script principal para execução de testes do sistema TOFcam.
"""

import sys
import os

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    """Executar todos os testes do sistema."""
    
    print("🧪 EXECUTANDO TESTES DO TOFcam")
    print("=" * 60)
    
    try:
        # Teste 1: Direções das setas
        print("\n1️⃣ TESTE DE DIREÇÕES DAS SETAS")
        print("-" * 30)
        from test_arrows import test_arrow_directions, test_extreme_values
        test_arrow_directions()
        test_extreme_values()
        
        # Teste 2: Comparação de algoritmos
        print("\n2️⃣ TESTE DE ALGORITMOS")
        print("-" * 30)
        from test_algorithms import test_algorithm_comparison, test_edge_cases
        test_algorithm_comparison()
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("📊 Sistema validado e pronto para uso")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Certifique-se de que todos os módulos estão no diretório correto")
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")

def show_menu():
    """Mostrar menu de opções."""
    
    print("\n🎯 MENU DE TESTES - TOFcam")
    print("=" * 40)
    print("1 - Executar todos os testes")
    print("2 - Teste de direções das setas")
    print("3 - Teste de algoritmos")
    print("4 - Exemplo básico de uso")
    print("5 - Comparação visual de algoritmos")
    print("0 - Sair")
    print("-" * 40)
    
    choice = input("Escolha uma opção (0-5): ").strip()
    
    if choice == "1":
        run_tests()
    elif choice == "2":
        from test_arrows import test_arrow_directions, test_extreme_values
        test_arrow_directions()
        test_extreme_values()
    elif choice == "3":
        from test_algorithms import test_algorithm_comparison, test_edge_cases
        test_algorithm_comparison()
        test_edge_cases()
    elif choice == "4":
        print("\n🚀 Iniciando exemplo básico...")
        print("💡 Execute: python examples/basic_usage.py")
    elif choice == "5":
        print("\n🔄 Iniciando comparação visual...")
        print("💡 Execute: python examples/algorithm_comparison.py")
    elif choice == "0":
        print("👋 Saindo...")
        return False
    else:
        print("❌ Opção inválida!")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            run_tests()
        elif sys.argv[1] == "arrows":
            from test_arrows import test_arrow_directions, test_extreme_values
            test_arrow_directions()
            test_extreme_values()
        elif sys.argv[1] == "algorithms":
            from test_algorithms import test_algorithm_comparison, test_edge_cases
            test_algorithm_comparison()
            test_edge_cases()
        else:
            print("❌ Argumento inválido!")
            print("💡 Uso: python run_tests.py [all|arrows|algorithms]")
    else:
        # Menu interativo
        while show_menu():
            input("\nPressione ENTER para continuar...")