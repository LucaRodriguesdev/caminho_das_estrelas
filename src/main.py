from src.astar import a_star
from src.utilities import load_coordinates, load_graph, normalize


def buscar(graph, coordinates, origem, destino) -> str:
    if origem not in graph or destino not in graph:
        return f"Erro: cidade(s) não encontrada(s): {origem if origem not in graph else ''} {destino if destino not in graph else ''}".strip()
    resultado = a_star(graph, coordinates, origem, destino)
    if resultado is None:
        return f"Não foi possível encontrar um caminho de {origem} para {destino}."
    caminho, km = resultado
    return f"A menor distância é {km:.1f} km.\nCaminho: {' -> '.join(caminho)}"

def main():
    graph = load_graph()
    coordinates = load_coordinates()
    while True:
        origem = input("Digite a cidade de origem? ")
        destino = input("Digite a cidade de destino? ")
        print(buscar(graph, coordinates, normalize(origem), normalize(destino)))
        if input("Digite 0 para sair ou Enter para continuar: ").strip() == "0":
            break


if __name__ == "__main__":
    main()