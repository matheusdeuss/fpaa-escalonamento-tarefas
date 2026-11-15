"""
geradores.py — Geração automática de entradas (Integrante 4)
============================================================

Três cenários, escolhidos para mostrar o comportamento da função de custo
do guloso clássico (operação fundamental = "este slot está livre?"):

  aleatorio : prazo ~ U{1..n}, lucro ~ U{1..1000}.  Caso médio / realista.
  pior      : todos os prazos = n.  A i-ésima tarefa testa i slots antes de
              achar vaga  ->  T(n) = n(n+1)/2  ->  O(n²)  no clássico.
  melhor    : prazos distintos 1..n (embaralhados).  Toda tarefa encontra o
              seu próprio slot livre no 1º teste  ->  T(n) = n.

Todos usam semente fixa (random.Random(seed)), então os resultados são
reproduzíveis: a mesma semente gera sempre a mesma entrada.
"""

import csv
import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codigo"))
from escalonamento import Tarefa  # noqa: E402

LUCRO_MAX = 1000


def gerar_aleatorio(n, seed=0):
    rng = random.Random(seed)
    return [Tarefa(f"T{i}", rng.randint(1, n), rng.randint(1, LUCRO_MAX)) for i in range(1, n + 1)]


def gerar_pior(n, seed=0):
    rng = random.Random(seed)
    return [Tarefa(f"T{i}", n, rng.randint(1, LUCRO_MAX)) for i in range(1, n + 1)]


def gerar_melhor(n, seed=0):
    rng = random.Random(seed)
    prazos = list(range(1, n + 1))
    rng.shuffle(prazos)
    return [Tarefa(f"T{i}", d, rng.randint(1, LUCRO_MAX)) for i, d in enumerate(prazos, start=1)]


GERADORES = {
    "aleatorio": gerar_aleatorio,
    "pior": gerar_pior,
    "melhor": gerar_melhor,
}

DESCRICAO = {
    "aleatorio": "Aleatório (prazo ~ U{1..n})",
    "pior": "Pior caso (todos os prazos = n)",
    "melhor": "Melhor caso (prazos distintos 1..n)",
}


def salvar_csv(tarefas, caminho):
    """Grava no formato aceito por ler_tarefas_csv / main.py --arquivo."""
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "prazo", "lucro"])
        for t in tarefas:
            w.writerow([t.id, t.prazo, t.lucro])
