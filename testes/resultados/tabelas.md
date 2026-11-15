# Resultados da bateria de testes

Gerado por `testes/benchmark.py` em 15/11/2026 16:53. Tempos = mediana de 5 execuções, em milissegundos (ms). Ambiente em `ambiente.txt`.

## Tabela 1 — Tempo de execução (ms) para N = 10, 100, 1.000 e 10.000

| Cenário | N | Clássico O(n²) | Union-Find O(n log n) | Clássico ÷ Union-Find |
|---|---:|---:|---:|---:|
| Aleatório (prazo ~ U{1..n}) | 10 | 0,007 | 0,008 | 0,9× |
| Aleatório (prazo ~ U{1..n}) | 100 | 0,098 | 0,065 | 1,5× |
| Aleatório (prazo ~ U{1..n}) | 1.000 | 2,10 | 0,707 | 3,0× |
| Aleatório (prazo ~ U{1..n}) | 10.000 | 57,00 | 7,70 | 7,4× |
| Pior caso (todos os prazos = n) | 10 | 0,011 | 0,009 | 1,2× |
| Pior caso (todos os prazos = n) | 100 | 0,595 | 0,066 | 9,0× |
| Pior caso (todos os prazos = n) | 1.000 | 59,24 | 0,697 | 85,0× |
| Pior caso (todos os prazos = n) | 10.000 | 5.914,2 | 7,28 | 812,5× |
| Melhor caso (prazos distintos 1..n) | 10 | 0,007 | 0,008 | 0,8× |
| Melhor caso (prazos distintos 1..n) | 100 | 0,041 | 0,048 | 0,9× |
| Melhor caso (prazos distintos 1..n) | 1.000 | 0,404 | 0,485 | 0,8× |
| Melhor caso (prazos distintos 1..n) | 10.000 | 4,27 | 4,94 | 0,9× |

## Tabela 2 — Operação fundamental (testes de slot), independe da máquina

| Cenário | N | Clássico (medido) | Clássico (teórico) | Union-Find (medido) |
|---|---:|---:|---:|---:|
| Aleatório (prazo ~ U{1..n}) | 10 | 14 | — | 17 |
| Aleatório (prazo ~ U{1..n}) | 100 | 585 | — | 279 |
| Aleatório (prazo ~ U{1..n}) | 1.000 | 14.788 | — | 2.833 |
| Aleatório (prazo ~ U{1..n}) | 10.000 | 438.586 | — | 29.539 |
| Pior caso (todos os prazos = n) | 10 | 55 | 55 = n(n+1)/2 | 27 |
| Pior caso (todos os prazos = n) | 100 | 5.050 | 5.050 = n(n+1)/2 | 297 |
| Pior caso (todos os prazos = n) | 1.000 | 500.500 | 500.500 = n(n+1)/2 | 2.997 |
| Pior caso (todos os prazos = n) | 10.000 | 50.005.000 | 50.005.000 = n(n+1)/2 | 29.997 |
| Melhor caso (prazos distintos 1..n) | 10 | 10 | 10 = n | 10 |
| Melhor caso (prazos distintos 1..n) | 100 | 100 | 100 = n | 100 |
| Melhor caso (prazos distintos 1..n) | 1.000 | 1.000 | 1.000 = n | 1.000 |
| Melhor caso (prazos distintos 1..n) | 10.000 | 10.000 | 10.000 = n | 10.000 |

## Tabela 3 — Fator de crescimento do tempo quando N é multiplicado por 10

Referência teórica: O(n²) → ×100; O(n log n) → ≈ ×13 (de 1.000 para 10.000); O(n) → ×10.

| Cenário | Método | 10 → 100 | 100 → 1.000 | 1.000 → 10.000 |
|---|---|---:|---:|---:|
| Aleatório (prazo ~ U{1..n}) | Clássico O(n²) | ×13,2 | ×21,5 | ×27,1 |
| Aleatório (prazo ~ U{1..n}) | Union-Find O(n log n) | ×7,8 | ×10,8 | ×10,9 |
| Pior caso (todos os prazos = n) | Clássico O(n²) | ×55,7 | ×99,6 | ×99,8 |
| Pior caso (todos os prazos = n) | Union-Find O(n log n) | ×7,3 | ×10,5 | ×10,4 |
| Melhor caso (prazos distintos 1..n) | Clássico O(n²) | ×6,2 | ×9,9 | ×10,6 |
| Melhor caso (prazos distintos 1..n) | Union-Find O(n log n) | ×6,1 | ×10,2 | ×10,2 |

## Tabela 4 — Todos os pontos medidos (base dos gráficos), tempo em ms

| N | Aleatório — Clássico | Aleatório — Union-Find | Pior caso — Clássico | Pior caso — Union-Find | Melhor caso — Clássico | Melhor caso — Union-Find |
|---:|---:|---:|---:|---:|---:|---:|
| 10 | 0,007 | 0,008 | 0,011 | 0,009 | 0,007 | 0,008 |
| 100 | 0,098 | 0,065 | 0,595 | 0,066 | 0,041 | 0,048 |
| 500 | 0,644 | 0,338 | 15,13 | 0,324 | 0,199 | 0,246 |
| 1.000 | 2,10 | 0,707 | 59,24 | 0,697 | 0,404 | 0,485 |
| 2.500 | 8,39 | 1,87 | 369,3 | 1,75 | 1,03 | 1,22 |
| 5.000 | 22,51 | 3,81 | 1.465,2 | 3,68 | 2,11 | 2,46 |
| 7.500 | 26,16 | 5,90 | 3.392,0 | 5,56 | 3,23 | 3,72 |
| 10.000 | 57,00 | 7,70 | 5.914,2 | 7,28 | 4,27 | 4,94 |

Em todos os casos as duas versões devolveram o **mesmo lucro Z** (conferido pelo script).
