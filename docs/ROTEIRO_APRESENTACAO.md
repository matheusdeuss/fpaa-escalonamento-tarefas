# Roteiro — Bloco "Demonstração do Código e Fluxo de Execução" (Integrante 1)

Tempo sugerido: **~2 min 30 s** (de 10 a 12 min no total). Os termos seguem as aulas de FPAA.

## 1. Estrutura de dados (≈30 s)
- Mostrar a classe `Tarefa` em `escalonamento.py`: `id`, `prazo` (d) e `lucro` (p).
  - "É uma dataclass imutável: o código fica legível e o algoritmo não altera a entrada."
- Mostrar o vetor `agenda`: "o índice é o número do slot; `agenda[t]` diz qual tarefa roda no instante t. Saber se um slot está livre custa O(1)."
- "O vetor tem tamanho min(n, maior prazo), então o espaço é O(n)."
- "Não usamos nenhuma biblioteca externa, só a biblioteca padrão do Python."

## 2. O algoritmo no modelo guloso da Aula 10 (≈60 s), função `escalonar_classico`
Mostrar os comentários do código, que seguem o pseudocódigo da aula:
1. **Critério guloso de escolha:** `ordenar_por_lucro`, lucro decrescente, O(n log n).
2. **REPETIR** para cada tarefa: **função de viabilidade**, que começa em `min(prazo, num_slots)` e anda para trás até achar um slot livre.
   - "Usamos o slot mais tardio para deixar os primeiros livres para tarefas de prazo curto."
3. **SE viável**, incorpora à solução. **SENÃO**, descarta definitivamente. "Como todo guloso, nunca volta atrás."
4. **Função de custo** (operação fundamental = testar um slot): no pior caso, T(n) = Σ i = n(n+1)/2, ou seja, **O(n²)**. Pela regra da soma, O(n log n) + O(n²) = O(n²).

## 3. Demonstração ao vivo (≈45 s)
```bash
python main.py
```
Ler a tabela de etapas, que tem o mesmo formato do exemplo do troco na Aula 10:

| Etapa | Escolha | Slots testados | Decisão | Lucro acumulado |
|---|---|---|---|---|
| 1 | a (p=100) | 2 | slot 2 | 100 |
| 2 | c (p=27) | 2, 1 | slot 1 | 127 |
| 3 | d (p=25) | 1 | descartada | 127 |
| 4 | b (p=19) | 1 | descartada | 127 |
| 5 | e (p=15) | 3 | slot 3 | 142 |

Resultado: **sequência c → a → e, Z = 142**.

Comentário opcional: "No troco da Aula 10, o guloso não dava a resposta ótima. Neste problema, o critério de maior lucro com o slot mais tardio sempre chega ao ótimo. Quem prova isso é o Integrante 5."

## 4. Versão com Union-Find (≈15 s), função `escalonar_dsu`
- "Trocamos o laço da função de viabilidade por um Union-Find, a mesma estrutura do algoritmo de Kruskal. `encontrar(t)` devolve direto o maior slot livre ≤ t."
- "O critério guloso e a resposta são os mesmos. O custo cai para O(n log n)."
- "Não chamamos essa versão de 'otimizada', seguindo o alerta da Aula 10: as duas dão a mesma solução ótima, só que esta gasta menos operações."
- Passar a palavra ao Integrante 4, que apresenta os tempos medidos.

## Perguntas prováveis
- **Por que não alocar no primeiro slot livre?** Uma tarefa com prazo 3 no slot 1 tiraria a única vaga de uma tarefa com prazo 1.
- **Qual é a operação fundamental?** Testar se um slot está livre. O campo `verificacoes` conta quantas vezes ela foi executada.
- **E os empates de lucro?** A ordenação é estável, então vale a ordem de entrada. O lucro total Z não muda.
- **E se um prazo for enorme?** O número de slots é limitado a min(n, maior prazo), então o espaço continua O(n).
