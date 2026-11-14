"""
main.py — Script de execução do trabalho.

Modos de uso (rodar dentro da pasta `codigo/`):

  python main.py
      Demonstração passo a passo com o exemplo clássico (5 tarefas).

  python main.py --arquivo exemplos/exemplo1.csv
      Resolve as tarefas de um arquivo CSV (colunas id,prazo,lucro).

  Opções:
      --metodo classico | dsu | ambos   (padrão: ambos)
      --passos                           mostra cada decisão do algoritmo
"""

from __future__ import annotations

import argparse
import sys

from escalonamento import ALGORITMOS, Tarefa, formatar_numero, ler_tarefas_csv

# Exemplo clássico da literatura usado na demonstração.
EXEMPLO_CLASSICO = [
    Tarefa("a", 2, 100),
    Tarefa("b", 1, 19),
    Tarefa("c", 2, 27),
    Tarefa("d", 1, 25),
    Tarefa("e", 3, 15),
]


def resolver(tarefas, metodo: str, passos: bool) -> None:
    """Executa o(s) algoritmo(s) escolhido(s) sobre `tarefas` e imprime o resultado."""
    print(f"Entrada ({len(tarefas)} tarefas):")
    if len(tarefas) <= 30:
        print("  " + ", ".join(str(t) for t in tarefas))
    print()

    nomes = list(ALGORITMOS) if metodo == "ambos" else [metodo]
    for nome in nomes:
        resultado = ALGORITMOS[nome](tarefas, verbose=passos)
        if passos:
            print()
        if resultado.num_slots <= 30:
            print(resultado)
            print(f"  Sequência de execução: {' -> '.join(t.id for t in resultado.escalonadas)}")
        else:
            # Entradas grandes: mostra só o resumo para não poluir o terminal.
            print(f"[{resultado.metodo}] Lucro total Z = {formatar_numero(resultado.lucro_total)} "
                  f"| escalonadas = {len(resultado.escalonadas)} "
                  f"| rejeitadas = {len(resultado.rejeitadas)}")
        print(f"  Operação fundamental (testes de slot) executada: {resultado.verificacoes} vezes\n")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Escalonamento de Tarefas com Prazos — algoritmo guloso")
    p.add_argument("--arquivo", help="CSV com colunas id,prazo,lucro")
    p.add_argument("--metodo", choices=["classico", "dsu", "ambos"], default="ambos")
    p.add_argument("--passos", action="store_true", help="imprime cada decisão do algoritmo")
    args = p.parse_args(argv)

    if args.arquivo:
        tarefas = ler_tarefas_csv(args.arquivo)
    else:
        print("=" * 80)
        print(" DEMONSTRAÇÃO — Escalonamento de Tarefas com Prazos (Algoritmo Guloso)")
        print("=" * 80)
        print(" Cada tarefa = (d = prazo, p = lucro). 1 processador, 1 slot por tarefa.")
        print(" Objetivo: maximizar Z = soma dos lucros das tarefas feitas no prazo.\n")
        tarefas = EXEMPLO_CLASSICO
        args.passos = True

    resolver(tarefas, args.metodo, args.passos)
    return 0


if __name__ == "__main__":
    # Garante acentuação correta no terminal do Windows.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
