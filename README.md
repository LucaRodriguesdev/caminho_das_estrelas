# astar-cities

Implementação do algoritmo A* para menor caminho entre cidades.

- `src/astar.py` — `haversine` e `a_star` (parte do A*)
- `tests/test_astar.py` — testes com um grafo pequeno

As outras partes (leitura de dados, interface, métricas, extração de grafo do
Google Maps) só precisam chamar `a_star(graph, coordinates, origem, destino)`;
o formato de `graph` e `coordinates` está descrito no topo de `src/astar.py`.

## Rodar os testes
pip install -r requirements.txt
python -m pytest tests
