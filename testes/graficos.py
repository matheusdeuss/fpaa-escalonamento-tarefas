"""
graficos.py — Gráficos de desempenho (Integrante 4)
===================================================

Lê testes/resultados/benchmark.csv (gerado por benchmark.py) e salva os
gráficos em testes/resultados/graficos/ (PNG em 200 dpi, prontos para o PDF
e os slides).

Única dependência externa do trabalho, e só para desenhar: matplotlib.
O algoritmo (codigo/) continua sem nenhuma biblioteca externa.

    python3 -m venv .venv && .venv/bin/pip install matplotlib
    .venv/bin/python testes/graficos.py
"""

import csv
import os
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "resultados")
OUT = os.path.join(RES, "graficos")

# Cor segue a entidade (o método), igual em todos os gráficos.
COR = {"classico": "#2a78d6", "dsu": "#eb6834"}
NOME = {"classico": "Clássico — O(n²)", "dsu": "Union-Find — O(n log n)"}
MARCA = {"classico": "o", "dsu": "s"}
CINZA_REF = "#8a8984"
TXT1, TXT2, GRADE = "#0b0b0b", "#52514e", "#e4e3df"
TITULO_CENARIO = {
    "aleatorio": "Aleatório (prazo ~ U{1..n})",
    "pior": "Pior caso (todos os prazos = n)",
    "melhor": "Melhor caso (prazos distintos)",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.edgecolor": GRADE,
    "axes.labelcolor": TXT2,
    "axes.titlecolor": TXT1,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "xtick.color": TXT2,
    "ytick.color": TXT2,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRADE,
    "grid.linewidth": 0.6,
    "legend.frameon": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
})


def br(x, casas=0):
    return f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


FMT_INT = FuncFormatter(lambda v, _: br(v))


def fmt_log_ms(v, _):
    if v >= 1:
        return br(v)
    return br(v, 3).rstrip("0").rstrip(",")


def carregar():
    dados = defaultdict(lambda: defaultdict(list))  # dados[cenario][metodo] = [(n, ms, verif)]
    with open(os.path.join(RES, "benchmark.csv"), encoding="utf-8") as f:
        for l in csv.DictReader(f):
            dados[l["cenario"]][l["metodo"]].append(
                (int(l["n"]), float(l["tempo_mediana_s"]) * 1000, int(l["verificacoes"])))
    for c in dados.values():
        for m in c:
            c[m].sort()
    return dados


def serie(ax, pts, metodo, y_idx=1, rotulo_final=True, fmt=None, dy=0, label=None):
    xs = [p[0] for p in pts]
    ys = [p[y_idx] for p in pts]
    ax.plot(xs, ys, color=COR[metodo], lw=2, marker=MARCA[metodo], ms=6,
            mec="white", mew=1.2, label=label or NOME[metodo], zorder=3)
    if rotulo_final:
        txt = fmt(ys[-1]) if fmt else br(ys[-1], 1)
        ax.annotate(txt, (xs[-1], ys[-1]), xytext=(6, dy), textcoords="offset points",
                    va="center", fontsize=9, color=TXT1)


def deslocamentos(dados_cen, y_idx=1):
    """Afasta os rótulos finais quando os dois valores estão próximos (evita sobreposição)."""
    c, d = dados_cen["classico"][-1][y_idx], dados_cen["dsu"][-1][y_idx]
    if max(c, d) / min(c, d) < 1.6:
        return ({"classico": -7, "dsu": 7} if c < d else {"classico": 7, "dsu": -7})
    return {"classico": 0, "dsu": 0}


def salvar(fig, nome):
    caminho = os.path.join(OUT, nome)
    fig.savefig(caminho)
    plt.close(fig)
    print(" ", caminho)


# ---------------------------------------------------------------------------
# 1. Tempo x N, escala log-log, um painel por cenário
# ---------------------------------------------------------------------------
def grafico_loglog(dados):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
    for ax, cen in zip(axes, ("aleatorio", "pior", "melhor")):
        dy = deslocamentos(dados[cen])
        for m in ("classico", "dsu"):
            serie(ax, dados[cen][m], m, fmt=lambda v: br(v, 1) + " ms", dy=dy[m])
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(TITULO_CENARIO[cen], loc="left")
        ax.set_xlabel("Tamanho da entrada N (escala log)")
        ax.xaxis.set_major_formatter(FMT_INT)
        ax.yaxis.set_major_formatter(FuncFormatter(fmt_log_ms))
        ax.set_xlim(right=ax.get_xlim()[1] * 3)
    axes[0].set_ylabel("Tempo (ms, escala log)")
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.06))
    fig.suptitle("Tempo de execução × tamanho da entrada", x=0.01, y=1.12, ha="left",
                 fontsize=13, fontweight="bold", color=TXT1)
    salvar(fig, "1_tempo_loglog_cenarios.png")


# ---------------------------------------------------------------------------
# 2 e 3. Tempo x N em escala linear (mostra a parábola do O(n²))
# ---------------------------------------------------------------------------
def grafico_linear(dados, cen, arquivo):
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    dy = deslocamentos(dados[cen])
    for m in ("classico", "dsu"):
        serie(ax, dados[cen][m], m, fmt=lambda v: br(v, 1) + " ms", dy=dy[m])
    ax.set_title(f"Tempo × N — {TITULO_CENARIO[cen]}", loc="left")
    ax.set_xlabel("Tamanho da entrada N")
    ax.set_ylabel("Tempo (ms)")
    ax.xaxis.set_major_formatter(FMT_INT)
    ax.yaxis.set_major_formatter(FMT_INT)
    ax.set_ylim(bottom=0)
    ax.set_xlim(0, 11500)
    ax.legend(loc="upper left")
    salvar(fig, arquivo)


# ---------------------------------------------------------------------------
# 4. Operação fundamental: medido x teórico
# ---------------------------------------------------------------------------
def grafico_operacao(dados):
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    pior = dados["pior"]
    ns = [p[0] for p in pior["classico"]]
    serie(ax, pior["classico"], "classico", y_idx=2, fmt=lambda v: br(v),
          label="Clássico (medido)")
    serie(ax, pior["dsu"], "dsu", y_idx=2, fmt=lambda v: br(v), label="Union-Find (medido)")
    # Teórico desenhado POR CIMA: coincide exatamente com o medido do clássico.
    ax.plot(ns, [n * (n + 1) / 2 for n in ns], color=TXT1, lw=1.2, ls=(0, (4, 3)),
            label="Teórico do clássico: n(n+1)/2", zorder=4)
    ax.plot(ns, ns, color=CINZA_REF, lw=1.5, ls=":", label="Referência linear: n", zorder=2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("Operação fundamental (testes de slot) — pior caso", loc="left")
    ax.set_xlabel("Tamanho da entrada N (escala log)")
    ax.set_ylabel("Nº de testes de slot (escala log)")
    ax.xaxis.set_major_formatter(FMT_INT)
    ax.yaxis.set_major_formatter(FMT_INT)
    ax.set_xlim(right=ax.get_xlim()[1] * 4)
    ax.legend(loc="upper left")
    salvar(fig, "4_operacao_fundamental_pior_caso.png")


def main():
    os.makedirs(OUT, exist_ok=True)
    dados = carregar()
    print("Gráficos gerados:")
    grafico_loglog(dados)
    grafico_linear(dados, "pior", "2_tempo_linear_pior_caso.png")
    grafico_linear(dados, "aleatorio", "3_tempo_linear_aleatorio.png")
    grafico_operacao(dados)


if __name__ == "__main__":
    main()
