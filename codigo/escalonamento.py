"""
escalonamento.py
================

Fundamentos de Projeto e Análise de Algoritmos (FPAA) — PUC Minas
Trabalho Prático — Técnica de Projeto: ALGORITMOS GULOSOS
Problema: Escalonamento de Tarefas com Prazos (Job Sequencing with Deadlines)

Bibliotecas externas: NENHUMA. Usamos só a biblioteca padrão do Python 3
(csv, dataclasses, typing), atendendo à regra do enunciado de informar
bibliotecas externas.

-------------------------------------------------------------------------------
1) O PROBLEMA
-------------------------------------------------------------------------------
Temos n tarefas. Cada tarefa Ti tem:
  - di = prazo (deadline): a tarefa precisa terminar até o instante di;
  - pi = lucro (profit)  : valor recebido se a tarefa terminar dentro do prazo.

Há UM processador, o tempo é dividido em "slots" 1, 2, 3, ... e cada tarefa
gasta exatamente 1 slot. Queremos escolher QUAIS tarefas executar, e em QUAL
slot, para obter o MAIOR lucro possível.

    Função objetivo:  maximizar  Z = soma dos pi das tarefas escalonadas
    Restrições     :  (a) cada slot recebe no máximo uma tarefa;
                      (b) a tarefa Ti só pode ocupar um slot t com t <= di.

-------------------------------------------------------------------------------
2) COMO O ALGORITMO SEGUE O MODELO DE ALGORITMO GULOSO DA AULA 10
-------------------------------------------------------------------------------
  Conjunto de opções ......... as tarefas ainda não analisadas.
  Critério guloso de escolha .. pegar a tarefa de MAIOR LUCRO
                                (por isso ordenamos por lucro decrescente).
  Função de viabilidade ...... existe algum slot LIVRE t com t <= prazo?
                                Procuramos do slot mais tardio para o mais cedo.
  Função de solução .......... terminou quando todas as tarefas foram analisadas.

  Procedimento (igual ao pseudocódigo da aula):
    REPETIR enquanto houver tarefas a considerar:
        escolher a tarefa de maior lucro (critério guloso);
        verificar se ela é viável (função de viabilidade);
        SE for viável:  incorporar à solução (ocupar o slot);
        SENÃO:          descartar DEFINITIVAMENTE.
    A escolha feita nunca é revista (característica de algoritmo guloso).

  Por que usar o slot MAIS TARDIO possível? Assim os slots iniciais ficam
  livres para tarefas que vierem depois com prazo curto. Ex.: colocar uma
  tarefa de prazo 3 no slot 1 tiraria a única vaga de uma tarefa de prazo 1.

  Diferente do exemplo do troco (Aula 10), em que o guloso NÃO dá a resposta
  ótima, neste problema o critério "maior lucro + slot mais tardio" SEMPRE
  encontra a solução ótima. A prova está na fundamentação teórica (Integrante 5).

-------------------------------------------------------------------------------
3) DUAS IMPLEMENTAÇÕES (mesmo critério guloso, mesma resposta)
-------------------------------------------------------------------------------
  escalonar_classico : procura o slot livre com um laço simples   -> O(n²)
  escalonar_dsu      : procura o slot livre com Union-Find, a
                       mesma estrutura do algoritmo de Kruskal    -> O(n log n)

  Observação: chamamos a 2ª versão de "versão com Union-Find" e não de
  "otimizada", seguindo o alerta da Aula 10 sobre a palavra "otimização".
  As duas dão a MESMA solução ótima; a 2ª apenas gasta menos operações.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from typing import List, Optional, Sequence


# =============================================================================
# PARTE 1 — ESTRUTURAS DE DADOS
# =============================================================================

@dataclass(frozen=True)
class Tarefa:
    """
    Uma tarefa Ti = (di, pi).

    Por que uma `dataclass`?
      - O código fica legível: `tarefa.prazo` e `tarefa.lucro` em vez de t[0], t[1].
      - Com frozen=True ela é IMUTÁVEL: o algoritmo nunca altera a entrada.

    Atributos:
        id    : nome da tarefa (ex.: "a", "T1").
        prazo : di, inteiro >= 1.
        lucro : pi, número >= 0.
    """
    id: str
    prazo: int
    lucro: float

    def __post_init__(self) -> None:
        # Rejeita entradas sem sentido para o problema.
        if not isinstance(self.prazo, int) or self.prazo < 1:
            raise ValueError(f"Tarefa {self.id}: prazo deve ser inteiro >= 1 (recebido {self.prazo!r})")
        if self.lucro < 0:
            raise ValueError(f"Tarefa {self.id}: lucro não pode ser negativo (recebido {self.lucro!r})")

    def __str__(self) -> str:
        return f"{self.id}(d={self.prazo}, p={formatar_numero(self.lucro)})"


@dataclass
class ResultadoEscalonamento:
    """
    Solução devolvida pelos algoritmos.

    Atributos:
        agenda       : vetor indexado pelo slot. agenda[t] = tarefa executada no
                       slot t (t = 1..num_slots). A posição 0 não é usada (fica
                       None) para que o índice do vetor seja igual ao número do slot.
        rejeitadas   : tarefas descartadas pela função de viabilidade.
        lucro_total  : valor da função objetivo Z.
        verificacoes : nº de vezes que a OPERAÇÃO FUNDAMENTAL foi executada
                       (Aula 02): o teste "este slot está livre?". É uma medida
                       de custo que não depende do computador usado.
        metodo       : nome da implementação que gerou o resultado.
    """
    agenda: List[Optional[Tarefa]]
    rejeitadas: List[Tarefa] = field(default_factory=list)
    lucro_total: float = 0
    verificacoes: int = 0
    metodo: str = ""

    @property
    def escalonadas(self) -> List[Tarefa]:
        """Tarefas escolhidas, na ordem de execução (slot 1, 2, 3, ...)."""
        return [t for t in self.agenda[1:] if t is not None]

    @property
    def num_slots(self) -> int:
        """Quantidade de slots de tempo da agenda."""
        return len(self.agenda) - 1

    def __str__(self) -> str:
        linhas = [f"[{self.metodo}] Lucro total Z = {formatar_numero(self.lucro_total)}",
                  "  Agenda final (slot -> tarefa):"]
        for slot in range(1, len(self.agenda)):
            tarefa = self.agenda[slot]
            linhas.append(f"    slot {slot:>3}: {tarefa if tarefa else '(vazio)'}")
        if self.rejeitadas:
            linhas.append("  Descartadas: " + ", ".join(str(t) for t in self.rejeitadas))
        return "\n".join(linhas)


def formatar_numero(valor: float) -> str:
    """Mostra 142 em vez de 142.0 quando o número é inteiro."""
    return str(int(valor)) if float(valor).is_integer() else f"{valor:.2f}"


# =============================================================================
# PARTE 2 — PASSOS COMUNS ÀS DUAS IMPLEMENTAÇÕES
# =============================================================================

def ordenar_por_lucro(tarefas: Sequence[Tarefa]) -> List[Tarefa]:
    """
    CRITÉRIO GULOSO DE ESCOLHA: ordena as tarefas por lucro DECRESCENTE.
    Depois disso, "escolher a melhor opção" é só pegar a próxima da lista.

    Custo: `sorted` do Python usa o Timsort (um MergeSort adaptado): O(n log n).
    Ele é estável, ou seja, tarefas com o mesmo lucro mantêm a ordem da entrada.
    Assim, a mesma entrada sempre gera a mesma agenda.
    """
    return sorted(tarefas, key=lambda t: t.lucro, reverse=True)


def calcular_num_slots(tarefas: Sequence[Tarefa]) -> int:
    """
    Quantos slots a agenda precisa: min(n, maior prazo).

      - Nenhuma tarefa roda depois do maior prazo, então slots além dele são inúteis.
      - Com n tarefas, no máximo n slots são ocupados.

    Isso mantém o vetor `agenda` com tamanho O(n), mesmo que um prazo seja enorme.
    """
    if not tarefas:
        return 0
    maior_prazo = max(t.prazo for t in tarefas)
    return min(len(tarefas), maior_prazo)


def _imprimir_cabecalho(ordenadas: Sequence[Tarefa], num_slots: int) -> None:
    """Saída didática: mostra a ordem gulosa e o cabeçalho da tabela de etapas."""
    print("Critério guloso -> ordem por lucro decrescente:")
    print("  " + ", ".join(str(t) for t in ordenadas))
    print(f"Slots disponíveis: 1 a {num_slots}\n")
    print(f"  {'Etapa':<6}{'Escolha':<16}{'Slots testados':<16}{'Decisão':<26}{'Lucro acumulado'}")
    print("  " + "-" * 78)


def _imprimir_etapa(etapa: int, tarefa: Tarefa, testados: str, decisao: str, lucro: float) -> None:
    """Saída didática: imprime uma linha da tabela de etapas (como o exemplo do troco na Aula 10)."""
    print(f"  {etapa:<6}{str(tarefa):<16}{testados:<16}{decisao:<26}{formatar_numero(lucro)}")


# =============================================================================
# PARTE 3 — IMPLEMENTAÇÃO CLÁSSICA: busca linear do slot livre — O(n²)
# =============================================================================

def escalonar_classico(tarefas: Sequence[Tarefa], verbose: bool = False) -> ResultadoEscalonamento:
    """
    Algoritmo guloso com a função de viabilidade feita por um laço simples.

    Parâmetros:
        tarefas : lista de Tarefa.
        verbose : se True, imprime a tabela de etapas (usado na demonstração).

    FUNÇÃO DE CUSTO (operação fundamental = testar se um slot está livre):
      Para a i-ésima tarefa analisada, o laço `while` testa no máximo i slots,
      porque antes dela no máximo (i - 1) slots foram ocupados.

        Pior caso   (todos os prazos iguais a n): T(n) = soma de i, para i = 1..n
                                                       = n(n + 1) / 2
        Melhor caso (cada tarefa acha vaga no 1º teste): T(n) = soma de 1 = n

      Tempo total = ordenação + busca = O(n log n) + O(n²) = O(max) = O(n²)
                    (regra da soma da notação O, Aula 05).
      Espaço: O(n) (vetor `agenda` + lista ordenada).
    """
    # --- Preparação ----------------------------------------------------------
    ordenadas = ordenar_por_lucro(tarefas)            # critério guloso: O(n log n)
    num_slots = calcular_num_slots(tarefas)
    agenda: List[Optional[Tarefa]] = [None] * (num_slots + 1)   # todos os slots livres
    rejeitadas: List[Tarefa] = []
    lucro_total = 0
    verificacoes = 0                                  # contador da operação fundamental

    if verbose:
        _imprimir_cabecalho(ordenadas, num_slots)

    # --- REPETIR enquanto houver tarefas a considerar -------------------------
    for etapa, tarefa in enumerate(ordenadas, start=1):   # escolhe a de maior lucro restante

        # FUNÇÃO DE VIABILIDADE: procura um slot livre <= prazo,
        # começando pelo mais tardio e andando para trás.
        slot = min(tarefa.prazo, num_slots)
        testados = []
        while slot >= 1:
            verificacoes += 1                         # 1 execução da operação fundamental
            testados.append(str(slot))
            if agenda[slot] is None:                  # slot livre encontrado
                break
            slot -= 1                                 # ocupado: tenta o slot anterior

        if slot >= 1:
            # SE viável: incorpora a escolha à solução
            agenda[slot] = tarefa
            lucro_total += tarefa.lucro
            decisao = f"incorporada no slot {slot}"
        else:
            # SENÃO: descarta definitivamente (nunca será reconsiderada)
            rejeitadas.append(tarefa)
            decisao = "descartada (sem vaga)"

        if verbose:
            _imprimir_etapa(etapa, tarefa, ",".join(testados), decisao, lucro_total)

    # FUNÇÃO DE SOLUÇÃO: todas as tarefas foram analisadas -> solução completa.
    return ResultadoEscalonamento(agenda, rejeitadas, lucro_total, verificacoes,
                                  "Guloso clássico (busca linear) O(n²)")


# =============================================================================
# PARTE 4 — IMPLEMENTAÇÃO COM UNION-FIND — O(n log n)
# =============================================================================

class SlotsLivres:
    """
    Union-Find (conjuntos disjuntos), a mesma estrutura usada no algoritmo de
    Kruskal (Aula 10). Aqui ela responde rápido à pergunta:

        "Qual é o MAIOR slot livre que seja <= t ?"

    Como funciona:
      - pai[t] guarda um slot candidato a estar livre (sempre <= t).
      - Se pai[t] == t, o slot t está livre.
      - O slot 0 é uma sentinela que significa "não há slot livre".
      - Ocupar o slot s faz pai[s] = s - 1 (une s ao conjunto do slot anterior).
        Quem procurar a partir de s é mandado direto para s-1, s-2, ...

    Exemplo com 3 slots:  pai = [0, 1, 2, 3]   (todos livres)
      ocupar(2)       ->  pai = [0, 1, 1, 3]
      encontrar(2)    ->  2 aponta para 1, e 1 é livre  -> resposta 1
      ocupar(1)       ->  pai = [0, 0, 1, 3]
      encontrar(2)    ->  2 -> 1 -> 0                    -> resposta 0 (sem vaga)

    Com COMPRESSÃO DE CAMINHO, cada busca custa O(α(n)) amortizado. α é a
    inversa da função de Ackermann e, na prática, é uma constante (Aula 10).
    """

    def __init__(self, num_slots: int) -> None:
        self.pai = list(range(num_slots + 1))   # cada slot começa apontando para si (livre)
        self.verificacoes = 0                   # operação fundamental: consultar pai[]

    def encontrar(self, t: int) -> int:
        """Devolve o maior slot livre <= t, ou 0 se não houver."""
        # 1º laço: sobe pelos ponteiros até achar um slot que aponta para si mesmo.
        raiz = t
        self.verificacoes += 1
        while self.pai[raiz] != raiz:
            raiz = self.pai[raiz]
            self.verificacoes += 1
        # 2º laço: compressão de caminho. Todos os slots do caminho passam a
        # apontar direto para a raiz, então a próxima busca será mais curta.
        # (Feito com laço, e não recursão, para não estourar a pilha com n grande.)
        while self.pai[t] != raiz:
            proximo = self.pai[t]
            self.pai[t] = raiz
            t = proximo
        return raiz

    def ocupar(self, slot: int) -> None:
        """Marca o slot como ocupado, unindo-o ao conjunto do slot anterior."""
        self.pai[slot] = slot - 1


def escalonar_dsu(tarefas: Sequence[Tarefa], verbose: bool = False) -> ResultadoEscalonamento:
    """
    Mesmo algoritmo guloso; muda só COMO a função de viabilidade acha o slot.
    Em vez do laço que anda de slot em slot, perguntamos ao Union-Find.

    FUNÇÃO DE CUSTO:
      Ordenação ............................ O(n log n)
      n consultas ao Union-Find ............ n · O(α(n)), praticamente O(n)
      Tempo total = O(n log n) + O(n · α(n)) = O(n log n)   (regra da soma)
      Espaço: O(n) (vetor `agenda` + vetor `pai`).

    O resultado (agenda e lucro) é IDÊNTICO ao de `escalonar_classico`.
    """
    # --- Preparação ----------------------------------------------------------
    ordenadas = ordenar_por_lucro(tarefas)            # critério guloso: O(n log n)
    num_slots = calcular_num_slots(tarefas)
    agenda: List[Optional[Tarefa]] = [None] * (num_slots + 1)
    rejeitadas: List[Tarefa] = []
    lucro_total = 0
    livres = SlotsLivres(num_slots)

    if verbose:
        _imprimir_cabecalho(ordenadas, num_slots)

    # --- REPETIR enquanto houver tarefas a considerar -------------------------
    for etapa, tarefa in enumerate(ordenadas, start=1):

        # FUNÇÃO DE VIABILIDADE: o Union-Find devolve direto o maior slot livre <= prazo.
        limite = min(tarefa.prazo, num_slots)
        slot = livres.encontrar(limite)

        if slot > 0:
            # SE viável: incorpora e marca o slot como ocupado
            agenda[slot] = tarefa
            lucro_total += tarefa.lucro
            livres.ocupar(slot)
            decisao = f"incorporada no slot {slot}"
        else:
            # SENÃO: descarta definitivamente
            rejeitadas.append(tarefa)
            decisao = "descartada (sem vaga)"

        if verbose:
            _imprimir_etapa(etapa, tarefa, f"busca <= {limite}", decisao, lucro_total)

    # FUNÇÃO DE SOLUÇÃO: todas as tarefas foram analisadas.
    return ResultadoEscalonamento(agenda, rejeitadas, lucro_total, livres.verificacoes,
                                  "Guloso com Union-Find O(n log n)")


# =============================================================================
# PARTE 5 — LEITURA DE ENTRADA (arquivo CSV)
# =============================================================================

def ler_tarefas_csv(caminho: str) -> List[Tarefa]:
    """
    Lê tarefas de um arquivo CSV com cabeçalho:  id,prazo,lucro
    Linhas vazias ou que começam com '#' são ignoradas (servem de comentário).
    """
    tarefas = []
    with open(caminho, newline="", encoding="utf-8") as f:
        linhas = (l for l in f if l.strip() and not l.lstrip().startswith("#"))
        for linha in csv.DictReader(linhas):
            lucro = float(linha["lucro"])
            tarefas.append(Tarefa(linha["id"].strip(), int(linha["prazo"]),
                                  int(lucro) if lucro.is_integer() else lucro))
    return tarefas


# Implementações disponíveis, por nome (usado pelo main.py e por quem importar o módulo).
ALGORITMOS = {
    "classico": escalonar_classico,
    "dsu": escalonar_dsu,
}
