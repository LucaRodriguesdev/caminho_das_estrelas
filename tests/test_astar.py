import unittest
from src.astar import a_star, haversine
from src.utilities import normalize, parse_distance, load_graph, load_coordinates

# Grafo pequeno para testes controlados da lógica do A*
GRAPH_MOCK = {
    "A": {"B": 1.0, "D": 10.0},
    "B": {"A": 1.0, "C": 2.0},
    "C": {"B": 2.0, "D": 3.0},
    "D": {"A": 10.0, "C": 3.0},
    "ILHA": {},  # Sem conexões
}

COORDS_MOCK = {
    "A": (0.0, 0.00),
    "B": (0.0, 0.005),
    "C": (0.0, 0.015),
    "D": (0.0, 0.030),
    "ILHA": (0.0, 0.5),
}


class TestHaversine(unittest.TestCase):
    def test_mesmo_ponto(self):
        """A distância entre um ponto e ele mesmo deve ser zero."""
        self.assertEqual(haversine((0, 0), (0, 0)), 0.0)

    def test_um_grau_de_latitude(self):
        """Valida a precisão aproximada de 1 grau de latitude em km."""
        self.assertAlmostEqual(haversine((0, 0), (1, 0)), 111.19, delta=0.2)


class TestAStarLogic(unittest.TestCase):
    def test_caminho_mais_curto(self):
        """Garante que o A* escolhe o caminho ótimo (A -> B -> C -> D = 6.0) em vez do direto (10.0)."""
        self.assertEqual(a_star(GRAPH_MOCK, COORDS_MOCK, "A", "D"), (["A", "B", "C", "D"], 6.0))

    def test_sentido_contrario(self):
        """Valida a simetria da busca no sentido inverso."""
        self.assertEqual(a_star(GRAPH_MOCK, COORDS_MOCK, "D", "A"), (["D", "C", "B", "A"], 6.0))

    def test_cidades_vizinhas(self):
        """Testa a rota entre duas cidades diretamente conectadas."""
        self.assertEqual(a_star(GRAPH_MOCK, COORDS_MOCK, "A", "B"), (["A", "B"], 1.0))

    def test_mesma_cidade(self):
        """Origem igual ao destino deve retornar custo zero e apenas a cidade."""
        self.assertEqual(a_star(GRAPH_MOCK, COORDS_MOCK, "A", "A"), (["A"], 0.0))

    def test_sem_caminho_ilha(self):
        """Tentar ir para um nó isolado deve retornar None."""
        self.assertIsNone(a_star(GRAPH_MOCK, COORDS_MOCK, "A", "ILHA"))

    def test_origem_ou_destino_inexistente(self):
        """Cidades que não existem no grafo devem retornar None."""
        self.assertIsNone(a_star(GRAPH_MOCK, COORDS_MOCK, "A", "INEXISTENTE"))
        self.assertIsNone(a_star(GRAPH_MOCK, COORDS_MOCK, "INEXISTENTE", "D"))


class TestUtilities(unittest.TestCase):
    def test_normalize_acentos_e_caixa(self):
        """Verifica se acentos são removidos e o texto fica em maiúsculas."""
        self.assertEqual(normalize("Campina Grande"), "CAMPINA GRANDE")
        self.assertEqual(normalize("joão pessoa"), "JOAO PESSOA")
        self.assertEqual(normalize("  patos  "), "PATOS")

    def test_parse_distance_formatos(self):
        """Testa o tratamento de distâncias em string com vírgula ou ponto."""
        self.assertEqual(parse_distance("19,95"), 19.95)
        self.assertEqual(parse_distance("10.5"), 10.5)
        self.assertIsNone(parse_distance("invalido"))
        self.assertIsNone(parse_distance(-5.0))

    def test_parse_distance_tipos_diversos(self):
        """Garante que parse_distance lida corretamente com números float/int diretos e nulos."""
        self.assertEqual(parse_distance(15.5), 15.5)
        self.assertEqual(parse_distance(10), 10.0)
        self.assertIsNone(parse_distance(None))
        self.assertIsNone(parse_distance(""))

    def test_normalize_caracteres_especiais(self):
        """Verifica a limpeza de espaços nas pontas e remoção de acentos."""
        self.assertEqual(normalize("  patos - pb  "), "PATOS - PB")
        self.assertEqual(normalize("SÃO JOÃO"), "SAO JOAO")


class TestIntegrationWithRealData(unittest.TestCase):
    """Testes de integração baseados nos dados reais dos arquivos CSV fornecidos."""

    def test_carregamento_dos_dados_reais(self):
        """Garante que os CSVs de cidades e coordenadas carregam corretamente sem erros."""
        graph = load_graph()
        coordinates = load_coordinates()
        
        self.assertGreater(len(graph), 0)
        self.assertGreater(len(coordinates), 0)

    def test_rota_real_aguabranca_juru(self):
        """Testa uma rota real utilizando os dados do cities.csv (Água Branca -> Juru)."""
        graph = load_graph()
        coordinates = load_coordinates()
        
        origem = normalize("Água Branca")
        destino = normalize("Juru")
        
        resultado = a_star(graph, coordinates, origem, destino)
        self.assertIsNotNone(resultado)
        
        caminho, distancia = resultado
        self.assertEqual(caminho[0], origem)
        self.assertEqual(caminho[-1], destino)
        self.assertGreater(distancia, 0.0)

    def test_rota_real_campina_joaopessoa(self):
        """Testa uma rota de longa distância entre Campina Grande e João Pessoa."""
        graph = load_graph()
        coordinates = load_coordinates()
        
        origem = normalize("Campina Grande")
        destino = normalize("João Pessoa")
        
        resultado = a_star(graph, coordinates, origem, destino)
        self.assertIsNotNone(resultado)
        
        caminho, distancia = resultado
        self.assertEqual(caminho[0], origem)
        self.assertEqual(caminho[-1], destino)
        self.assertGreater(distancia, 0.0)


if __name__ == "__main__":
    unittest.main()