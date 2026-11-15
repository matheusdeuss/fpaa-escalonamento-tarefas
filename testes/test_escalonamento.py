"""
test_escalonamento.py — Testes de correção (Integrante 4)
=========================================================

Valida o código do Integrante 1 (codigo/escalonamento.py) antes de medir
desempenho. Só usa a biblioteca padrão (unittest).

Como executar (na raiz do repositório):
    python3 -m unittest discover -s testes -v

Grupos de teste:
  1. Casos pequenos montados à mão, com resposta conferida no papel.
  2. Casos de borda (lista vazia, uma tarefa, prazos enormes, empates...).
  3. Validação da entrada (prazo < 1, lucro negativo).
  4. Comparação com FORÇA BRUTA: para n <= 10 testamos todos os 2^n
     subconjuntos e conferimos que o guloso acha o lucro MÁXIMO.
  5. Consistência entre as duas versões (clássica x Union-Find) em entradas
     grandes geradas automaticamente.
  6. Contagem da operação fundamental: pior caso = n(n+1)/2, melhor caso = n.
"""

import itertools
import os
import random
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "codigo"))

from escalonamento import (  # noqa: E402
    ALGORITMOS,
    Tarefa,
    escalonar_classico,
    escalonar_dsu,
    ler_tarefas_csv,
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geradores import GERADORES  # noqa: E402


# -----------------------------------------------------------------------------
# Funções auxiliares
# -----------------------------------------------------------------------------

def forca_bruta(tarefas):
    """
    Lucro ótimo testando TODOS os subconjuntos (O(2^n · n log n)).
    Um subconjunto é viável se, ordenado por prazo, a k-ésima tarefa
    (k = 1, 2, ...) tem prazo >= k  — ou seja, dá para encaixar todas.
    """
    melhor = 0
    for r in range(len(tarefas) + 1):
        for sub in itertools.combinations(tarefas, r):
            prazos = sorted(t.prazo for t in sub)
            if all(d >= k for k, d in enumerate(prazos, start=1)):
                melhor = max(melhor, sum(t.lucro for t in sub))
    return melhor


def tarefas_de(pares):
    """[(prazo, lucro), ...] -> [Tarefa('T1', ...), Tarefa('T2', ...), ...]"""
    return [Tarefa(f"T{i}", d, p) for i, (d, p) in enumerate(pares, start=1)]


class VerificaAgenda:
    """Mixin com a checagem de que uma solução respeita as restrições."""

    def assert_solucao_valida(self, tarefas, r):
        # (b) cada tarefa escalonada está num slot t <= prazo
        for slot in range(1, len(r.agenda)):
            t = r.agenda[slot]
            if t is not None:
                self.assertLessEqual(slot, t.prazo, f"{t} no slot {slot} fora do prazo")
        # (a) nenhuma tarefa aparece duas vezes; escalonadas + rejeitadas = entrada
        ids = [t.id for t in r.escalonadas] + [t.id for t in r.rejeitadas]
        self.assertCountEqual(ids, [t.id for t in tarefas])
        # Z bate com a soma das escalonadas
        self.assertAlmostEqual(r.lucro_total, sum(t.lucro for t in r.escalonadas))
        self.assertEqual(r.agenda[0], None)


# -----------------------------------------------------------------------------
# 1. Casos pequenos manuais
# -----------------------------------------------------------------------------

class TestCasosManuais(unittest.TestCase, VerificaAgenda):

    def rodar_ambos(self, tarefas, lucro_esperado, ids_esperados=None):
        for nome, alg in ALGORITMOS.items():
            with self.subTest(metodo=nome):
                r = alg(tarefas)
                self.assertEqual(r.lucro_total, lucro_esperado)
                self.assert_solucao_valida(tarefas, r)
                if ids_esperados is not None:
                    self.assertEqual([t.id for t in r.escalonadas], ids_esperados)

    def test_exemplo_da_demonstracao(self):
        # a(2,100) b(1,19) c(2,27) d(1,25) e(3,15) -> c, a, e  Z = 142
        caminho = os.path.join(RAIZ, "codigo", "exemplos", "exemplo1.csv")
        self.rodar_ambos(ler_tarefas_csv(caminho), 142, ["c", "a", "e"])

    def test_exemplo_classico_livros(self):
        # Exemplo clássico: (4,20) (1,10) (1,40) (1,30) -> T3 no slot 1, T1 no slot 4. Z = 60
        self.rodar_ambos(tarefas_de([(4, 20), (1, 10), (1, 40), (1, 30)]), 60, ["T3", "T1"])

    def test_exemplo_seis_tarefas(self):
        # (2,200) (1,180) (2,190) (1,300) (3,120) (2,100) -> T4, T1, T5  Z = 620
        self.rodar_ambos(tarefas_de([(2, 200), (1, 180), (2, 190), (1, 300), (3, 120), (2, 100)]),
                         620, ["T4", "T1", "T5"])

    def test_todas_cabem(self):
        # prazos distintos 1..4: todas são escalonadas
        self.rodar_ambos(tarefas_de([(1, 5), (2, 6), (3, 7), (4, 8)]), 26, ["T1", "T2", "T3", "T4"])

    def test_slot_mais_tardio_preserva_prazos_curtos(self):
        # A de maior lucro tem prazo 2; ir para o slot 2 deixa o slot 1 para a de prazo 1.
        self.rodar_ambos(tarefas_de([(2, 50), (1, 40)]), 90, ["T2", "T1"])


# -----------------------------------------------------------------------------
# 2. Casos de borda
# -----------------------------------------------------------------------------

class TestCasosDeBorda(unittest.TestCase, VerificaAgenda):

    def test_lista_vazia(self):
        for alg in ALGORITMOS.values():
            r = alg([])
            self.assertEqual(r.lucro_total, 0)
            self.assertEqual(r.escalonadas, [])
            self.assertEqual(r.num_slots, 0)

    def test_uma_tarefa(self):
        for alg in ALGORITMOS.values():
            r = alg([Tarefa("x", 1, 7)])
            self.assertEqual(r.lucro_total, 7)

    def test_todos_os_prazos_iguais_a_1(self):
        # só cabe a de maior lucro
        t = tarefas_de([(1, 3), (1, 9), (1, 4)])
        for alg in ALGORITMOS.values():
            r = alg(t)
            self.assertEqual(r.lucro_total, 9)
            self.assertEqual(len(r.rejeitadas), 2)

    def test_prazo_muito_maior_que_n(self):
        # prazo enorme não pode criar um vetor gigante: agenda tem min(n, maior prazo) slots
        t = tarefas_de([(10**9, 1), (10**9, 2), (10**9, 3)])
        for alg in ALGORITMOS.values():
            r = alg(t)
            self.assertEqual(r.num_slots, 3)
            self.assertEqual(r.lucro_total, 6)

    def test_lucros_empatados_resultado_deterministico(self):
        t = tarefas_de([(1, 10), (1, 10), (1, 10)])
        for alg in ALGORITMOS.values():
            r = alg(t)
            self.assertEqual([x.id for x in r.escalonadas], ["T1"])  # ordenação estável

    def test_lucro_zero_e_fracionario(self):
        t = tarefas_de([(1, 0), (2, 2.5), (2, 1.25)])
        for alg in ALGORITMOS.values():
            self.assertAlmostEqual(alg(t).lucro_total, 3.75)

    def test_entrada_nao_e_alterada(self):
        t = tarefas_de([(2, 1), (1, 5), (3, 2)])
        copia = list(t)
        for alg in ALGORITMOS.values():
            alg(t)
            self.assertEqual(t, copia)

    def test_leitura_csv_com_comentarios(self):
        conteudo = "# comentário\nid,prazo,lucro\n\nx,2,10\ny,1,3.5\n"
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(conteudo)
        try:
            t = ler_tarefas_csv(f.name)
        finally:
            os.remove(f.name)
        self.assertEqual(t, [Tarefa("x", 2, 10), Tarefa("y", 1, 3.5)])


# -----------------------------------------------------------------------------
# 3. Validação da entrada
# -----------------------------------------------------------------------------

class TestValidacao(unittest.TestCase):

    def test_prazo_zero(self):
        with self.assertRaises(ValueError):
            Tarefa("x", 0, 10)

    def test_prazo_nao_inteiro(self):
        with self.assertRaises(ValueError):
            Tarefa("x", 1.5, 10)

    def test_lucro_negativo(self):
        with self.assertRaises(ValueError):
            Tarefa("x", 1, -1)


# -----------------------------------------------------------------------------
# 4. Otimalidade: guloso x força bruta
# -----------------------------------------------------------------------------

class TestOtimalidade(unittest.TestCase, VerificaAgenda):

    def test_guloso_igual_forca_bruta(self):
        rng = random.Random(2026)
        casos = 400
        for caso in range(casos):
            n = rng.randint(1, 10)
            t = tarefas_de([(rng.randint(1, n), rng.randint(0, 50)) for _ in range(n)])
            otimo = forca_bruta(t)
            for nome, alg in ALGORITMOS.items():
                with self.subTest(caso=caso, metodo=nome):
                    r = alg(t)
                    self.assertEqual(r.lucro_total, otimo)
                    self.assert_solucao_valida(t, r)


# -----------------------------------------------------------------------------
# 5. Consistência entre as versões em entradas grandes
# -----------------------------------------------------------------------------

class TestConsistenciaEntradasGrandes(unittest.TestCase, VerificaAgenda):

    def test_classico_e_dsu_iguais(self):
        for cenario, gerar in GERADORES.items():
            for n in (1000, 5000):
                with self.subTest(cenario=cenario, n=n):
                    t = gerar(n, seed=n)
                    rc = escalonar_classico(t)
                    rd = escalonar_dsu(t)
                    self.assertEqual(rc.lucro_total, rd.lucro_total)
                    self.assertEqual(rc.agenda, rd.agenda)
                    self.assert_solucao_valida(t, rc)


# -----------------------------------------------------------------------------
# 6. Função de custo (operação fundamental)
# -----------------------------------------------------------------------------

class TestFuncaoDeCusto(unittest.TestCase):

    def test_pior_caso_classico_n_n_mais_1_sobre_2(self):
        for n in (1, 10, 100, 1000):
            r = escalonar_classico(GERADORES["pior"](n, seed=1))
            self.assertEqual(r.verificacoes, n * (n + 1) // 2)

    def test_melhor_caso_classico_n(self):
        for n in (1, 10, 100, 1000):
            r = escalonar_classico(GERADORES["melhor"](n, seed=1))
            self.assertEqual(r.verificacoes, n)

    def test_dsu_cresce_linearmente(self):
        # com compressão de caminho, cada busca faz poucas consultas (nº constante):
        # o total fica limitado por c·n, longe de n(n+1)/2
        for cenario, gerar in GERADORES.items():
            n = 10000
            r = escalonar_dsu(gerar(n, seed=1))
            self.assertLessEqual(r.verificacoes, 4 * n, cenario)


if __name__ == "__main__":
    unittest.main()
