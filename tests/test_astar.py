import unittest

from src.astar import a_star, haversine

# Grafo pequeno: o caminho direto A->D (10) é pior que A->B->C->D (1+2+3 = 6)
GRAPH = {
    "A": {"B": 1.0, "D": 10.0},
    "B": {"A": 1.0, "C": 2.0},
    "C": {"B": 2.0, "D": 3.0},
    "D": {"A": 10.0, "C": 3.0},
    "ILHA": {},  # sem conexão
}
# coordenadas no equador (1 grau de longitude ~ 111 km): linha reta sempre
# fica abaixo da distância do grafo, então a heurística é admissível
COORDS = {
    "A": (0.0, 0.00),
    "B": (0.0, 0.005),
    "C": (0.0, 0.015),
    "D": (0.0, 0.030),
    "ILHA": (0.0, 0.5),
}


class TestHaversine(unittest.TestCase):
    def test_mesmo_ponto(self):
        self.assertEqual(haversine((0, 0), (0, 0)), 0.0)

    def test_um_grau_de_latitude(self):
        self.assertAlmostEqual(haversine((0, 0), (1, 0)), 111.19, delta=0.2)


class TestAStar(unittest.TestCase):
    def test_caminho_mais_curto(self):
        self.assertEqual(a_star(GRAPH, COORDS, "A", "D"), (["A", "B", "C", "D"], 6.0))

    def test_sentido_contrario(self):
        self.assertEqual(a_star(GRAPH, COORDS, "D", "A"), (["D", "C", "B", "A"], 6.0))

    def test_cidades_vizinhas(self):
        self.assertEqual(a_star(GRAPH, COORDS, "A", "B"), (["A", "B"], 1.0))

    def test_mesma_cidade(self):
        self.assertEqual(a_star(GRAPH, COORDS, "A", "A"), (["A"], 0.0))

    def test_sem_caminho(self):
        self.assertIsNone(a_star(GRAPH, COORDS, "A", "ILHA"))


if __name__ == "__main__":
    unittest.main()
