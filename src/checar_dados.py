from utilities import load_graph, load_coordinates
from astar import haversine

graph = load_graph()
coords = load_coordinates()
print(f"{len(graph)} cidades no grafo, {len(coords)} nas coordenadas")

for cidade in graph:
    if cidade not in coords:
        print("Sem coordenada:", cidade)

for cidade, vizinhas in graph.items():
    for nome, dist in vizinhas.items():
        if cidade in coords and nome in coords:
            if haversine(coords[cidade], coords[nome]) > dist:
                print(f"Heurística superestima: {cidade} -> {nome}")