# Escalonamento de Tarefas com Prazos — Código-fonte (Integrante 1)

FPAA, PUC Minas. Trabalho prático com a técnica de projeto **Algoritmos Gulosos**.

- **Linguagem:** Python 3.10 ou superior.
- **Bibliotecas externas:** nenhuma. Só a biblioteca padrão é usada (`csv`, `dataclasses`, `typing`).

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `escalonamento.py` | Estruturas de dados, as duas implementações do algoritmo guloso e a leitura de CSV |
| `main.py` | Script de execução: demonstração passo a passo ou leitura de arquivo CSV |
| `exemplos/exemplo1.csv` | Entrada usada na demonstração |

## Como executar (dentro da pasta `codigo/`)

```bash
python main.py
```
Roda a demonstração com o exemplo clássico. Para cada etapa, mostra qual tarefa foi escolhida, quais slots foram testados, se ela foi incorporada ou descartada e o lucro acumulado.

```bash
python main.py --arquivo exemplos/exemplo1.csv --metodo classico --passos
```
Opções: `--metodo classico | dsu | ambos` (padrão: `ambos`) e `--passos`, que mostra a tabela de etapas.

## Como o código segue o modelo de algoritmo guloso (Aula 10)

| Elemento do algoritmo guloso | Neste problema | No código |
|---|---|---|
| Conjunto de opções | Tarefas ainda não analisadas | Lista `ordenadas` |
| Critério guloso de escolha | Maior lucro primeiro | `ordenar_por_lucro` |
| Função de viabilidade | Existe slot livre `t <= prazo`? (testa do mais tardio para o mais cedo) | Laço `while` em `escalonar_classico` / `SlotsLivres.encontrar` |
| Incorporar à solução | Ocupa o slot e soma o lucro | `agenda[slot] = tarefa` |
| Descartar definitivamente | Tarefa sem vaga nunca é reconsiderada | `rejeitadas.append(tarefa)` |
| Função de solução | Todas as tarefas foram analisadas | Fim do laço `for` |
| Função objetivo | Maximizar Z = soma dos lucros | `lucro_total` |

## Função de custo (Aulas 02, 03 e 05)

**Operação fundamental:** testar se um slot está livre. O campo `verificacoes` do resultado conta quantas vezes ela foi executada.

**`escalonar_classico` (busca linear):**
- A i-ésima tarefa testa no máximo i slots.
- Pior caso, com todos os prazos iguais a n: T(n) = Σ i (i = 1..n) = n(n+1)/2, ou seja, O(n²).
- Melhor caso, quando cada tarefa acha vaga no primeiro teste: T(n) = n.
- Tempo total: O(n log n) da ordenação + O(n²) da busca = O(max) = **O(n²)**, pela regra da soma.

**`escalonar_dsu` (Union-Find):**
- Usa a mesma estrutura de conjuntos disjuntos do algoritmo de Kruskal (Aula 10).
- Cada busca custa O(α(n)), praticamente constante.
- Tempo total: O(n log n) + O(n·α(n)) = **O(n log n)**.

**Espaço:** O(n) nas duas versões. O vetor `agenda` tem `min(n, maior prazo)` posições.

As duas versões aplicam o **mesmo critério guloso** e devolvem **a mesma solução**. A diferença é apenas o custo da função de viabilidade. Seguindo o alerta da Aula 10 sobre a palavra "otimização", a segunda versão é chamada "versão com Union-Find", e não "otimizada".

## Interface para o Integrante 4

```python
from escalonamento import Tarefa, escalonar_classico, escalonar_dsu, ler_tarefas_csv, ALGORITMOS

tarefas = [Tarefa("T1", 2, 100), Tarefa("T2", 1, 19)]   # Tarefa(id, prazo, lucro)
# ou: tarefas = ler_tarefas_csv("entrada.csv")          # colunas id,prazo,lucro

r = escalonar_classico(tarefas)   # ou escalonar_dsu(tarefas)
```

| Campo do resultado | Significado |
|---|---|
| `r.lucro_total` | Valor da função objetivo Z |
| `r.escalonadas` | Tarefas escolhidas, na ordem de execução |
| `r.rejeitadas` | Tarefas descartadas |
| `r.agenda` | `agenda[t]` = tarefa no slot t (a posição 0 não é usada) |
| `r.verificacoes` | Nº de execuções da operação fundamental (custo independente da máquina) |

Observações:
- Os algoritmos **não alteram** a lista de entrada.
- `verbose=True` imprime a tabela de etapas. Deixe `False` ao medir tempo.
- `ALGORITMOS = {"classico": ..., "dsu": ...}` permite percorrer as duas versões em um laço.
- `Tarefa` lança `ValueError` se o prazo for menor que 1 ou se o lucro for negativo.

## Escolha das estruturas de dados

- **`Tarefa` como `dataclass(frozen=True)`:** o código fica legível (`t.prazo`, `t.lucro`), e a tarefa é imutável, então o algoritmo não altera a entrada.
- **Vetor `agenda`, em que o índice é o número do slot:** responder "o slot t está livre?" custa O(1).
- **Union-Find (`SlotsLivres`):** `pai[t]` aponta para o maior slot possivelmente livre ≤ t. Ocupar o slot s faz `pai[s] = s - 1`. Com compressão de caminho, cada busca custa O(α(n)).
- **`sorted` (Timsort, O(n log n), estável):** tarefas com lucros empatados mantêm a ordem da entrada, então o resultado é sempre o mesmo.
