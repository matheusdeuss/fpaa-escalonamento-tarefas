"""
benchmark.py — Bateria de desempenho (Integrante 4)
===================================================

Mede o tempo real de execução das duas implementações do Integrante 1
(escalonar_classico e escalonar_dsu) para N = 10, 100, 1.000 e 10.000
(mais pontos intermediários, para as curvas dos gráficos), nos três cenários
de geradores.py.

Metodologia:
  - Cada (cenário, N) usa uma entrada gerada com semente fixa -> reproduzível.
  - A mesma entrada é dada às duas versões (comparação justa).
  - Tempo medido com time.perf_counter(), com o coletor de lixo desligado
    durante a medição para não somar pausas do GC.
  - Cada medição é repetida R vezes; reportamos a MEDIANA (robusta a ruído
    do sistema operacional) e o mínimo.
  - Também registramos o nº de execuções da operação fundamental
    (`verificacoes`), que independe da máquina, e o comparamos com a
    fórmula teórica do clássico: n(n+1)/2 no pior caso e n no melhor.
  - Conferimos que as duas versões devolvem o mesmo lucro Z.

Uso (na raiz do repositório):
    python3 testes/benchmark.py                 # bateria completa
    python3 testes/benchmark.py --rapido        # só N = 10, 100, 1000 (teste do script)
    python3 testes/benchmark.py --repeticoes 7

Saídas em testes/resultados/:
    benchmark.csv      — dados brutos (uma linha por cenário × N × método)
    tabelas.md         — tabelas prontas para o PDF e os slides
    ambiente.txt       — máquina e versão do Python usadas
    entradas/*.csv     — entradas geradas para N = 10.000 (podem ser abertas no main.py)

Os gráficos são gerados depois, por graficos.py (precisa de matplotlib).
"""

import argparse
import csv
import gc
import os
import platform
import statistics
import sys
import time
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), "codigo"))
sys.path.insert(0, AQUI)

from escalonamento import ALGORITMOS  # noqa: E402
from geradores import DESCRICAO, GERADORES, salvar_csv  # noqa: E402

N_OBRIGATORIOS = [10, 100, 1000, 10000]
N_TODOS = [10, 100, 500, 1000, 2500, 5000, 7500, 10000]
SAIDA = os.path.join(AQUI, "resultados")
SEMENTE_BASE = 2026

NOME_METODO = {"classico": "Clássico O(n²)", "dsu": "Union-Find O(n log n)"}


def medir(alg, tarefas, repeticoes):
    """Executa alg(tarefas) `repeticoes` vezes; devolve (lista de tempos em s, último resultado)."""
    tempos = []
    resultado = None
    for _ in range(repeticoes):
        gc.collect()
        gc.disable()
        try:
            t0 = time.perf_counter()
            resultado = alg(tarefas)
            t1 = time.perf_counter()
        finally:
            gc.enable()
        tempos.append(t1 - t0)
    return tempos, resultado


def teorico_classico(cenario, n):
    if cenario == "pior":
        return n * (n + 1) // 2
    if cenario == "melhor":
        return n
    return None


def fmt_br(x, casas):
    """Formato brasileiro: 1.234,56 (ponto no milhar, vírgula no decimal)."""
    return f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def fmt_ms(segundos):
    ms = segundos * 1000
    return fmt_br(ms, 3 if ms < 1 else 2 if ms < 100 else 1)


def fmt_int(x):
    return f"{x:,}".replace(",", ".")


def rodar(ns, repeticoes):
    linhas = []
    for cenario, gerar in GERADORES.items():
        for n in ns:
            tarefas = gerar(n, seed=SEMENTE_BASE + n)
            lucros = {}
            for metodo, alg in ALGORITMOS.items():
                # aquecimento (1 execução descartada) para estabilizar caches
                alg(tarefas)
                tempos, r = medir(alg, tarefas, repeticoes)
                lucros[metodo] = r.lucro_total
                linha = {
                    "cenario": cenario,
                    "n": n,
                    "metodo": metodo,
                    "repeticoes": repeticoes,
                    "tempo_mediana_s": statistics.median(tempos),
                    "tempo_min_s": min(tempos),
                    "tempo_max_s": max(tempos),
                    "verificacoes": r.verificacoes,
                    "verificacoes_teoricas": (teorico_classico(cenario, n) or "") if metodo == "classico" else "",
                    "lucro_total": r.lucro_total,
                    "escalonadas": len(r.escalonadas),
                }
                linhas.append(linha)
                print(f"  {cenario:<10} n={n:>6}  {metodo:<9} "
                      f"mediana={fmt_ms(linha['tempo_mediana_s']):>10} ms  "
                      f"verificações={fmt_int(r.verificacoes):>12}  Z={r.lucro_total}", flush=True)
            if len(set(lucros.values())) != 1:
                raise SystemExit(f"ERRO: versões discordam em {cenario}, n={n}: {lucros}")
    return linhas


def salvar_dados(linhas):
    caminho = os.path.join(SAIDA, "benchmark.csv")
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        for l in linhas:
            l2 = dict(l)
            for k in ("tempo_mediana_s", "tempo_min_s", "tempo_max_s"):
                l2[k] = f"{l[k]:.9f}"
            w.writerow(l2)
    return caminho


def gerar_tabelas(linhas, ns, repeticoes):
    idx = {(l["cenario"], l["n"], l["metodo"]): l for l in linhas}
    out = []
    out.append("# Resultados da bateria de testes\n")
    out.append(f"Gerado por `testes/benchmark.py` em {datetime.now():%d/%m/%Y %H:%M}. "
               f"Tempos = mediana de {repeticoes} execuções, em milissegundos (ms). "
               "Ambiente em `ambiente.txt`.\n")

    # Tabela 1: tempo por cenário (N obrigatórios)
    out.append("## Tabela 1 — Tempo de execução (ms) para N = 10, 100, 1.000 e 10.000\n")
    out.append("| Cenário | N | Clássico O(n²) | Union-Find O(n log n) | Clássico ÷ Union-Find |")
    out.append("|---|---:|---:|---:|---:|")
    for cenario in GERADORES:
        for n in [x for x in ns if x in N_OBRIGATORIOS]:
            c, d = idx[(cenario, n, "classico")], idx[(cenario, n, "dsu")]
            razao = c["tempo_mediana_s"] / d["tempo_mediana_s"]
            out.append(f"| {DESCRICAO[cenario]} | {fmt_int(n)} | {fmt_ms(c['tempo_mediana_s'])} | "
                       f"{fmt_ms(d['tempo_mediana_s'])} | {fmt_br(razao, 1)}× |")
    out.append("")

    # Tabela 2: operação fundamental
    out.append("## Tabela 2 — Operação fundamental (testes de slot), independe da máquina\n")
    out.append("| Cenário | N | Clássico (medido) | Clássico (teórico) | Union-Find (medido) |")
    out.append("|---|---:|---:|---:|---:|")
    for cenario in GERADORES:
        for n in [x for x in ns if x in N_OBRIGATORIOS]:
            c, d = idx[(cenario, n, "classico")], idx[(cenario, n, "dsu")]
            teo = c["verificacoes_teoricas"]
            teo_txt = fmt_int(teo) if teo != "" else "—"
            if cenario == "pior":
                teo_txt += " = n(n+1)/2"
            elif cenario == "melhor":
                teo_txt += " = n"
            out.append(f"| {DESCRICAO[cenario]} | {fmt_int(n)} | {fmt_int(c['verificacoes'])} | "
                       f"{teo_txt} | {fmt_int(d['verificacoes'])} |")
    out.append("")

    # Tabela 3: crescimento quando N multiplica por 10
    out.append("## Tabela 3 — Fator de crescimento do tempo quando N é multiplicado por 10\n")
    out.append("Referência teórica: O(n²) → ×100; O(n log n) → ≈ ×13 (de 1.000 para 10.000); O(n) → ×10.\n")
    out.append("| Cenário | Método | 10 → 100 | 100 → 1.000 | 1.000 → 10.000 |")
    out.append("|---|---|---:|---:|---:|")
    for cenario in GERADORES:
        for metodo in ALGORITMOS:
            fatores = []
            for a, b in ((10, 100), (100, 1000), (1000, 10000)):
                if (cenario, a, metodo) in idx and (cenario, b, metodo) in idx:
                    f_ = idx[(cenario, b, metodo)]["tempo_mediana_s"] / idx[(cenario, a, metodo)]["tempo_mediana_s"]
                    fatores.append("×" + fmt_br(f_, 1))
                else:
                    fatores.append("—")
            out.append(f"| {DESCRICAO[cenario]} | {NOME_METODO[metodo]} | " + " | ".join(fatores) + " |")
    out.append("")

    # Tabela 4: todos os pontos (base dos gráficos)
    out.append("## Tabela 4 — Todos os pontos medidos (base dos gráficos), tempo em ms\n")
    out.append("| N | " + " | ".join(f"{DESCRICAO[c].split(' (')[0]} — {NOME_METODO[m].split(' ')[0]}"
                                     for c in GERADORES for m in ALGORITMOS) + " |")
    out.append("|---:|" + "---:|" * (len(GERADORES) * len(ALGORITMOS)))
    for n in ns:
        cel = [fmt_ms(idx[(c, n, m)]["tempo_mediana_s"]) for c in GERADORES for m in ALGORITMOS]
        out.append(f"| {fmt_int(n)} | " + " | ".join(cel) + " |")
    out.append("")
    out.append("Em todos os casos as duas versões devolveram o **mesmo lucro Z** (conferido pelo script).\n")

    caminho = os.path.join(SAIDA, "tabelas.md")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    return caminho


def salvar_ambiente(repeticoes):
    info = [
        f"Data: {datetime.now():%d/%m/%Y %H:%M}",
        f"Python: {platform.python_version()} ({platform.python_implementation()})",
        f"Sistema: {platform.system()} {platform.release()} ({platform.machine()})",
        f"Processador: {platform.processor() or platform.machine()}",
        f"Repetições por medição: {repeticoes} (mediana reportada) + 1 aquecimento",
        "Relógio: time.perf_counter(); coletor de lixo desligado durante cada medição",
        f"Sementes: {SEMENTE_BASE} + N",
    ]
    with open(os.path.join(SAIDA, "ambiente.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(info) + "\n")
    print("\n".join(info))


def salvar_entradas():
    pasta = os.path.join(SAIDA, "entradas")
    os.makedirs(pasta, exist_ok=True)
    n = 10000
    for cenario, gerar in GERADORES.items():
        salvar_csv(gerar(n, seed=SEMENTE_BASE + n), os.path.join(pasta, f"{cenario}_n{n}.csv"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repeticoes", type=int, default=5)
    ap.add_argument("--rapido", action="store_true", help="só N = 10, 100, 1000")
    args = ap.parse_args()

    ns = [10, 100, 1000] if args.rapido else N_TODOS
    os.makedirs(SAIDA, exist_ok=True)
    salvar_ambiente(args.repeticoes)
    print()
    linhas = rodar(ns, args.repeticoes)
    print("\nArquivos gerados:")
    print(" ", salvar_dados(linhas))
    print(" ", gerar_tabelas(linhas, ns, args.repeticoes))
    if not args.rapido:
        salvar_entradas()
        print(" ", os.path.join(SAIDA, "entradas"))


if __name__ == "__main__":
    main()
