# Testes, benchmarks e resultados (Integrante 4)

Validação do código do Integrante 1 e medição de desempenho para N = 10, 100, 1.000 e 10.000.

- **Análise dos resultados (para o PDF e os slides):** [RESULTADOS.md](RESULTADOS.md)
- **Tabelas geradas:** [resultados/tabelas.md](resultados/tabelas.md)
- **Gráficos:** [resultados/graficos/](resultados/graficos/)

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `test_escalonamento.py` | 21 testes de correção (`unittest`): casos manuais, casos de borda, validação da entrada, comparação com força bruta, consistência entre as duas versões e contagem da operação fundamental |
| `geradores.py` | Geração automática de entradas com semente fixa: cenários aleatório, pior caso e melhor caso |
| `benchmark.py` | Bateria de desempenho. Gera `resultados/benchmark.csv`, `tabelas.md`, `ambiente.txt` e as entradas de N = 10.000 |
| `graficos.py` | Lê `benchmark.csv` e gera os PNGs de `resultados/graficos/` |
| `requirements.txt` | `matplotlib`, usado só para desenhar os gráficos |

## Como reproduzir (na raiz do repositório)

```bash
# 1) Testes de correção (biblioteca padrão, cerca de 2 s)
python3 -m unittest discover -s testes -v

# 2) Bateria de desempenho (biblioteca padrão, cerca de 2 min por causa do pior caso O(n²))
python3 testes/benchmark.py                # 5 repetições, mediana
python3 testes/benchmark.py --rapido       # só N <= 1000, para conferir o script

# 3) Gráficos (precisa de matplotlib)
python3 -m venv .venv && .venv/bin/pip install -r testes/requirements.txt
.venv/bin/python testes/graficos.py
```

As entradas grandes ficam salvas em `resultados/entradas/` e podem ser abertas no programa principal:

```bash
cd codigo && python3 main.py --arquivo ../testes/resultados/entradas/pior_n10000.csv --metodo dsu
```

## Cenários de entrada

| Cenário | Como é gerado | Custo esperado do clássico (testes de slot) |
|---|---|---|
| Aleatório | prazo ~ U{1..n}, lucro ~ U{1..1000} | entre n e n(n+1)/2, conforme a instância |
| Pior caso | todos os prazos = n | exatamente n(n+1)/2, ou seja, O(n²) |
| Melhor caso | prazos distintos 1..n, embaralhados | exatamente n |

A semente de cada entrada é `2026 + N`, então rodar de novo gera as mesmas entradas.
