
import heapq
from math import asin, cos, radians, sin, sqrt


def haversine(coord1: tuple, coord2: tuple) -> float:
    latitude1, longitude1 = map(radians, coord1)
    latitude2, longitude2 = map(radians, coord2)

    delta_latitude = latitude2 - latitude1
    delta_longitude = longitude2 - longitude1

    a = sin(delta_latitude / 2)**2 + cos(latitude1) * cos(latitude2) * sin(delta_longitude / 2)**2
    c = 2 * asin(sqrt(a))
    return 6371 * c


def a_star(graph: dict, coordinates: dict, start: str, goal: str, return_stats: bool = False):
    if start not in graph or goal not in graph:
        return None
    distancia_percorrida = {start: 0}
    veio_de = {start: None}
    fila_prioridade = [(haversine(coordinates[start], coordinates[goal]), start)]
    ja_expandidas = set()
    detalhes = []  # um registro por expansão, na ordem em que aconteceram
    while fila_prioridade:
        _, atual = heapq.heappop(fila_prioridade)
        if atual in ja_expandidas:
            continue
        ja_expandidas.add(atual)
        detalhes.append({
            "cidade": atual,
            "pai": veio_de[atual],
            "g": distancia_percorrida[atual],
            "h": haversine(coordinates[atual], coordinates[goal]),
        })
        if atual == goal:
            caminho = []
            cidade = goal
            while cidade is not None:
                caminho.append(cidade)
                cidade = veio_de[cidade]
            caminho.reverse()
            if return_stats:
                stats = {
                    "expandidas": len(ja_expandidas),
                    "descobertas": len(distancia_percorrida),
                    "ordem_expansao": [d["cidade"] for d in detalhes],
                    "detalhes": detalhes,
                }
                return caminho, distancia_percorrida[goal], stats
            return caminho, distancia_percorrida[goal]
        for vizinho, km_ate_vizinha in graph[atual].items():
            nova_distancia = distancia_percorrida[atual] + km_ate_vizinha
            if nova_distancia < distancia_percorrida.get(vizinho, float("inf")):
                distancia_percorrida[vizinho] = nova_distancia
                veio_de[vizinho] = atual
                prioridade = nova_distancia + haversine(coordinates[vizinho], coordinates[goal])
                heapq.heappush(fila_prioridade, (prioridade, vizinho))
    return None
        
            
          