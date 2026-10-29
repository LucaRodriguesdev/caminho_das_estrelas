import logging
import unicodedata
import math
from collections import defaultdict

# NOVO: permite montar caminhos de arquivos que funcionam em qualquer sistema (Windows, Linux, Mac)
from pathlib import Path 

import pandas as pd

logger = logging.getLogger(__name__)


# NOVO: guarda o caminho absoluto da pasta "data". Parte do local deste arquivo (src/utilities.py),
# sobe uma pasta (a raiz do projeto) e entra em "data". Assim o programa acha os CSVs
# não importa de qual pasta você o execute.
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def normalize(name) -> str:
    texto = unicodedata.normalize("NFKD", str(name).strip())
    sem_acento = "".join(c for c in texto if not unicodedata.combining(c))
    return sem_acento.upper()


def parse_distance(value) -> float | None:
    try:
        distance = float(str(value).replace(",", "."))
    except ValueError:
        return None
    return distance if math.isfinite(distance) and distance >= 0 else None


def convert_to_graph(df: pd.DataFrame) -> dict[str, dict[str, float]]:
    graph: dict[str, dict[str, float]] = defaultdict(dict)

    for city_raw, *pairs in df.itertuples(index=False, name=None):
        city = normalize(city_raw)
        graph[city]

        for neighbor_raw, distance_raw in zip(pairs[0::2], pairs[1::2]):
            if pd.isna(neighbor_raw) or pd.isna(distance_raw):
                continue

            neighbor = normalize(neighbor_raw)
            distance = parse_distance(distance_raw)

            if distance is None:
                logger.warning("Distância inválida %r: %s -> %s", distance_raw, city, neighbor)
                continue
            if neighbor == city:
                continue

            graph[city][neighbor] = distance
            graph[neighbor][city] = distance

    return dict(graph)

# NOVO: lê o arquivo cities.csv e já devolve o grafo pronto para o A*.
# Junta dois passos em um: pd.read_csv (lê o arquivo) + convert_to_graph (transforma em dicionário).
# O parâmetro "path" tem um valor padrão (data/cities.csv), então normalmente você chama só load_graph().
def load_graph(path: Path = DATA_DIR / "cities.csv") -> dict[str, dict[str, float]]:
    """Lê o cities.csv e devolve o grafo {cidade: {vizinha: km}}."""
    return convert_to_graph(pd.read_csv(path))

# NOVO: lê o arquivo coordinates.csv e devolve um dicionário {cidade: (latitude, longitude)}.
# O A* precisa disso para calcular a distância em linha reta (heurística).
# Os nomes passam por normalize() para ficarem iguais aos do grafo (maiúsculas, sem espaços nas pontas);
# se não fossem iguais, o A* não acharia as coordenadas de cada cidade.
def load_coordinates(path: Path = DATA_DIR / "coordinates.csv") -> dict[str, tuple[float, float]]:
    """Lê o coordinates.csv e devolve {cidade: (latitude, longitude)}."""
    df = pd.read_csv(path)
    return {normalize(row.cidade): (row.latitude, row.longitude) for row in df.itertuples()}