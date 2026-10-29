import logging
import math
from collections import defaultdict

import pandas as pd

logger = logging.getLogger(__name__)

def normalize(name) -> str:
    return str(name).strip().upper()


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