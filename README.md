# Escalonamento de Tarefas com Prazos — Algoritmo Guloso

Trabalho prático da disciplina **Fundamentos de Projeto e Análise de Algoritmos (FPAA)**, PUC Minas, Sistemas de Informação, 2026/2.

- **Técnica de projeto:** Algoritmos Gulosos (Aula 10)
- **Problema:** Escalonamento de Tarefas com Prazos (*Job Sequencing with Deadlines*)
- **Linguagem:** Python 3.10 ou superior, sem bibliotecas externas

---

## O problema em uma frase

Há *n* tarefas, cada uma com um **prazo** *d* e um **lucro** *p*. Um único processador executa uma tarefa por unidade de tempo (slot). O objetivo é escolher quais tarefas executar, e em que ordem, para **maximizar o lucro total** Z, recebendo o lucro apenas das tarefas concluídas até o prazo.

## Início rápido

```bash
cd codigo
python main.py
```

Saída resumida da demonstração:

```
  Etapa Escolha         Slots testados  Decisão                   Lucro acumulado
  ------------------------------------------------------------------------------
  1     a(d=2, p=100)   2               incorporada no slot 2     100
  2     c(d=2, p=27)    2,1             incorporada no slot 1     127
  3     d(d=1, p=25)    1               descartada (sem vaga)     127
  4     b(d=1, p=19)    1               descartada (sem vaga)     127
  5     e(d=3, p=15)    3               incorporada no slot 3     142

[Guloso clássico (busca linear) O(n²)] Lucro total Z = 142
  Sequência de execução: c -> a -> e
```

Para resolver as tarefas de um arquivo CSV com as colunas `id,prazo,lucro`:

```bash
python main.py --arquivo exemplos/exemplo1.csv --metodo classico --passos
```

## Estrutura do repositório

```
.
├── README.md                      ← este arquivo
├── codigo/                        ← Integrante 1
│   ├── escalonamento.py           ← estruturas de dados + algoritmos gulosos
│   ├── main.py                    ← script de execução (linha de comando)
│   ├── exemplos/exemplo1.csv      ← entrada da demonstração
│   └── README.md                  ← documentação técnica do código e interface
├── testes/                        ← Integrante 4
│   ├── test_escalonamento.py      ← testes de correção (manuais, borda, força bruta)
│   ├── geradores.py               ← geração automática de entradas
│   ├── benchmark.py               ← bateria N = 10 … 10.000 → tabelas
│   ├── graficos.py                ← gráficos de tempo (matplotlib)
│   ├── RESULTADOS.md              ← análise dos resultados (para o PDF e os slides)
│   └── resultados/                ← benchmark.csv, tabelas.md, graficos/*.png, entradas/
└── docs/
    ├── FLUXO_EXECUCAO.md          ← fluxo de execução e referência das funções (Integrante 1)
    ├── ROTEIRO_APRESENTACAO.md    ← roteiro do bloco de demonstração (Integrante 1)
    └── referencias/               ← cronograma do grupo + fundamentação teórica (João Fróis)
```

## O que foi implementado (Integrante 1)

| Item | Onde |
|---|---|
| Estrutura de dados da tarefa (`Tarefa`) e da solução (`ResultadoEscalonamento`) | `codigo/escalonamento.py`, Parte 1 |
| Critério guloso: ordenação por lucro decrescente | `ordenar_por_lucro` |
| Guloso clássico com busca linear de slot, **O(n²)** | `escalonar_classico` |
| Guloso com Union-Find (mesma estrutura do Kruskal), **O(n log n)** | `SlotsLivres` e `escalonar_dsu` |
| Contagem da operação fundamental (testes de slot) | campo `verificacoes` |
| Leitura de entrada em CSV | `ler_tarefas_csv` |
| Script de execução com demonstração passo a passo | `codigo/main.py` |
| Interface para as baterias de teste do Integrante 4 | [codigo/README.md](codigo/README.md#interface-para-o-integrante-4) |

As duas implementações seguem o mesmo critério guloso e chegam à mesma solução ótima. A diferença está só no custo da função de viabilidade.

Detalhes:
- [Documentação técnica do código](codigo/README.md): mapeamento para o modelo guloso da Aula 10, função de custo e estruturas de dados.
- [Fluxo de execução](docs/FLUXO_EXECUCAO.md): diagrama, passo a passo e referência das funções.
- [Roteiro da apresentação](docs/ROTEIRO_APRESENTACAO.md): bloco "Demonstração do Código e Fluxo de Execução".

## Complexidade (resumo)

| Implementação | Tempo | Espaço |
|---|---|---|
| `escalonar_classico` | O(n log n) + O(n²) = **O(n²)** | O(n) |
| `escalonar_dsu` | O(n log n) + O(n·α(n)) = **O(n log n)** | O(n) |

A análise formal (escolha gulosa, subestrutura ótima, prova de correção) fica a cargo do Integrante 5 (João Fróis).

## Divisão do grupo

| Papel | Integrante | Responsabilidade | Bloco na apresentação |
|---|---|---|---|
| **Integrante 1** | Matheus Deus | **Código-fonte, interface para testes, comentários** (este repositório) | Demonstração do código e fluxo de execução |
| Integrante 2 | Lucas Gabriel | Documentação em PDF e entrega do .zip no Canvas | Introdução e contextualização do problema |
| Integrante 3 | Gabriel | Slides e condução da apresentação | Conclusão, considerações finais e transições |
| Integrante 4 | Lucas Almeida | Casos de teste, benchmarks, tabelas e gráficos | Resultados obtidos e análise de desempenho |
| Integrante 5 | João Fróis | Fundamentação teórica e análise de complexidade | Técnica de projeto e complexidade assintótica |

**Prazos:** entrega no Canvas até 17/11/2026. Apresentação em 18/11/2026, com 10 a 12 minutos por grupo.

## Referências (bibliografia da disciplina)

- CORMEN, T. H. et al. *Algoritmos: teoria e prática*. 4. ed. Rio de Janeiro: GEN, 2024.
- ZIVIANI, N. *Projeto de algoritmos com implementações em Pascal e C*. 3. ed. São Paulo: Cengage Learning, 2011.
- TOSCANI, L. V.; VELOSO, P. A. S. *Complexidade de algoritmos: análise, projeto e métodos*. 3. ed. Porto Alegre: Bookman, 2012.
