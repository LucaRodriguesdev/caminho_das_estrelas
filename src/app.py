import time

import streamlit as st
import folium
from streamlit_folium import st_folium

from utilities import load_graph, load_coordinates, load_display_names
from astar import a_star

import base64
from pathlib import Path

FONTE = Path(__file__).parent / "fonts" / "LEMONMILK-Bold.otf"
FONTE_INFO = Path(__file__).parent / "fonts" / "Gotham-Bold.otf"

MIME = {".woff2": "font/woff2", ".woff": "font/woff", ".otf": "font/otf", ".ttf": "font/ttf"}
FORMATO = {".woff2": "woff2", ".woff": "woff", ".otf": "opentype", ".ttf": "truetype"}


@st.cache_data
def css_fonte(caminho: Path) -> str:
    ext = caminho.suffix.lower()
    dados = base64.b64encode(caminho.read_bytes()).decode()
    return f"""
    <style>
    @font-face {{
        font-family: 'LEMONMILK-Bold';
        src: url(data:{MIME[ext]};base64,{dados}) format('{FORMATO[ext]}');
        font-weight: normal;
        font-style: normal;
    }}
    .stApp h1.titulo-app {{
        font-family: 'LEMONMILK-Bold', monospace !important;
        font-size: 4rem;
        line-height: 1.1;
        text-align: center !important;
        padding: 2rem 0 !important;
        margin: 0 !important;
        color: #fff;
        text-shadow:
            0 0 30px rgba(255, 255, 255, 0.1),
            0 0 50px rgba(120, 170, 255, 0.2),
            0 0 60px rgba(80, 130, 255, 0.2),
            0 0 120px rgba(80, 130, 255, 0.3);
        animation: flutuar 4s ease-in-out infinite;
    }}

        @keyframes flutuar {{
        0%, 100% {{ transform: translateY(0); }}
        50%      {{ transform: translateY(-12px); }}
    }}

        @keyframes brilho {{
        0%, 100% {{ text-shadow: 0 0 6px rgba(255,255,255,0.4), 0 0 14px rgba(120,170,255,0.3), 0 0 30px rgba(80,130,255,0.2); }}
        50%      {{ text-shadow: 0 0 10px rgba(255,255,255,0.5), 0 0 24px rgba(120,170,255,0.4), 0 0 50px rgba(80,130,255,0.3), 0 0 90px rgba(80,130,255,0.1); }}
    }}

    </style>
    """

@st.cache_data
def css_gotham(caminho: Path) -> str:
    ext = caminho.suffix.lower()
    dados = base64.b64encode(caminho.read_bytes()).decode()
    return f"""
    <style>
    @font-face {{
        font-family: 'Gotham';
        src: url(data:{MIME[ext]};base64,{dados}) format('{FORMATO[ext]}');
        font-weight: normal;
        font-style: normal;
    }}
    .info-rota, .info-rota p {{
        font-family: 'Gotham', 'Montserrat', sans-serif !important;
    }}
    .info-rota .dist {{
        font-size: 1.3rem;
        font-weight: normal;
        margin-bottom: 0.4rem;
        animation: aparecer 0.8s ease-out both;
    }}
    .info-rota .caminho {{
        font-size: 1rem;
        line-height: 1.6;
        opacity: 0.9;
        animation: aparecer 0.8s ease-out 0.3s both;
    }}

     @keyframes aparecer {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}

    </style>
    """




st.markdown(css_gotham(FONTE_INFO), unsafe_allow_html=True)


st.markdown(css_fonte(FONTE), unsafe_allow_html=True)
st.markdown('<h1 class="titulo-app">Algoritmo A* para cidades</h1>', unsafe_allow_html=True)

TILES_ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"

st.markdown(
    """
    <style>
    .stApp {
        background-color: #05060f;
        background-image:
            radial-gradient(1.5px 1.5px at 20px 30px, #fff, transparent),
            radial-gradient(1px 1px at 90px 80px, #fff, transparent),
            radial-gradient(1.5px 1.5px at 160px 20px, #cfe0ff, transparent),
            radial-gradient(1px 1px at 230px 120px, #fff, transparent),
            radial-gradient(2px 2px at 300px 60px, #ffe9b0, transparent);
        background-size: 340px 160px;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    iframe[title="streamlit_folium.st_folium"] {
        border-radius: 12px;
        box-shadow: 0 0 12px rgba(120, 170, 255, 0.35),
                    0 0 32px rgba(80, 130, 255, 0.18);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def carregar():
    return load_graph(), load_coordinates(), load_display_names()


graph, coords, nomes = carregar()
chaves = sorted(graph)


def bonito(chave):
    return nomes.get(chave, chave)

CSS_MAPA = """
<style>
.leaflet-overlay-pane path.rota-final {
    filter: drop-shadow(3px 5px 4px rgba(0, 0, 0, 0.75))
            drop-shadow(0 0 6px rgba(25, 113, 255, 0.5));
}
.leaflet-overlay-pane path.rota-parcial {
    filter: drop-shadow(3px 5px 4px rgba(0, 0, 0, 0.7));
}
.leaflet-container {
    box-shadow: inset 0 0 40px rgba(5, 6, 15, 0.5);
}
</style>
"""


# callbacks dos botões de passo (rodam antes da recarga, então podem alterar o slider)
def passo_anterior():
    st.session_state["passo"] = max(0, st.session_state["passo"] - 1)


def passo_seguinte(total):
    st.session_state["passo"] = min(total, st.session_state["passo"] + 1)




origem = st.selectbox("Origem", chaves, format_func=bonito)
destino = st.selectbox("Destino", chaves, format_func=bonito)

if st.button("Calcular rota"):
    st.session_state["mostrar_metricas"] = False
    st.session_state["mostrar_exploracao"] = False
    if origem == destino:
        st.session_state["rota"] = None
        st.warning("Escolha cidades diferentes.")
    else:
        inicio = time.perf_counter()
        resultado = a_star(graph, coords, origem, destino, return_stats=True)
        tempo_ms = (time.perf_counter() - inicio) * 1000

        if resultado is None:
            st.session_state["rota"] = None
            st.error("Não existe caminho entre essas cidades.")
        else:
            caminho, km, stats = resultado
            st.session_state["rota"] = {
                "id": time.time(),
                "origem": origem,
                "destino": destino,
                "caminho": caminho,
                "km": km,
                "expandidas": stats["expandidas"],
                "descobertas": stats["descobertas"],
                "detalhes": stats["detalhes"],
                "tempo_ms": tempo_ms,
            }
            # nova rota: a animação começa no último passo (busca completa)
            st.session_state["passo"] = len(stats["detalhes"])

rota = st.session_state.get("rota")

if rota:
    trajeto = " → ".join(bonito(c) for c in rota["caminho"])
    st.markdown(
        f'<div class="info-rota"><p class="dist">Distância total: {rota["km"]:.1f} km</p>'
        f'<p class="caminho">{trajeto}</p></div>',
        unsafe_allow_html=True,
    )

    mostrando = st.session_state.get("mostrar_metricas", False)
    if st.button("Visualizar métricas"):
        st.session_state["mostrar_metricas"] = True

    mostrando = st.session_state.get("mostrar_metricas", False)

    if mostrando:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Cidades expandidas", rota["expandidas"])
        c2.metric("Cidades descobertas", rota["descobertas"])
        c3.metric("Cidades na rota", len(rota["caminho"]))
        c4.metric("Tempo", f"{rota['tempo_ms']:.3f} ms")

    detalhes = rota["detalhes"]
    total = len(detalhes)

    if st.button("Visualizar exploração"):
        st.session_state["mostrar_exploracao"] = True

    mostrar_exploracao = st.session_state.get("mostrar_exploracao", False)

    passo = total
    if mostrar_exploracao:
        st.session_state.setdefault("passo", total)
        st.session_state["passo"] = min(st.session_state["passo"], total)

        b1, b2, b3 = st.columns([1, 1, 6])
        b1.button("◀", on_click=passo_anterior, help="Passo anterior")
        b2.button("▶", on_click=passo_seguinte, args=(total,), help="Próximo passo")
        b3.slider("Passo da busca", 0, total, key="passo")
        passo = st.session_state["passo"]

        if passo == 0:
            st.caption("Início: nenhuma cidade expandida ainda.")
        else:
            d = detalhes[passo - 1]
            f = d["g"] + d["h"]
            st.caption(
                f"Passo {passo} de {total}: expandindo **{bonito(d['cidade'])}**  ·  "
                f"g = {d['g']:.1f} km (percorrido)  ·  h = {d['h']:.1f} km (reta até o destino)  ·  "
                f"f = {f:.1f} km"
            )
        st.caption("🟠 expandidas  ·  🟣 cidade atual  ·  🟤 caminho parcial  ·  🔵 rota final (último passo)")

    # ---------- mapa ----------
    mapa = folium.Map(location=[-7.2, -36.8], zoom_start=7, tiles=None)
    folium.TileLayer(tiles=TILES_ESRI, attr="Tiles © Esri", opacity=0.45).add_to(mapa)

    mapa.get_root().header.add_child(folium.Element(CSS_MAPA))

    # cidades-base: pequenas e discretas
    for chave, (lat, lon) in coords.items():
        folium.CircleMarker(
            [lat, lon], radius=2, color="#888", weight=1,
            fill=True, fill_opacity=0.5, opacity=0.6, tooltip=bonito(chave),
        ).add_to(mapa)

    # enquadramento fixo (todas as cidades expandidas + rota), para o mapa não "pular" entre passos
    pontos_bounds = [coords[d["cidade"]] for d in detalhes] + [coords[c] for c in rota["caminho"]]

    mapa.fit_bounds(pontos_bounds)

    busca = folium.FeatureGroup(name="busca")

    if mostrar_exploracao and passo < total:
        # passos 0..total-1: mostra a busca parcial
        feitas = detalhes[:passo]

        # arestas da árvore de busca (pai -> cidade) das cidades já expandidas
        for d in feitas:
            if d["pai"] is not None:
                folium.PolyLine(
                    [coords[d["pai"]], coords[d["cidade"]]],
                    color="#e8590c", weight=1.5, opacity=0.6,
                ).add_to(busca)

        # cidades expandidas até agora, com g/h/f no tooltip
        for i, d in enumerate(feitas, start=1):
            f = d["g"] + d["h"]
            folium.CircleMarker(
                coords[d["cidade"]], radius=4, color="#e8590c", fill=True, fill_opacity=0.9,
                tooltip=f"{i}º: {bonito(d['cidade'])} (g={d['g']:.1f}, h={d['h']:.1f}, f={f:.1f})",
            ).add_to(busca)

        if feitas:
            # caminho parcial: da origem até a cidade atual, seguindo os pais
            pai_de = {d["cidade"]: d["pai"] for d in feitas}
            atual = feitas[-1]["cidade"]
            parcial = []
            c = atual
            while c is not None:
                parcial.append(coords[c])
                c = pai_de.get(c)
            folium.PolyLine(parcial, color="#00ff15", weight=5, opacity=0.9, class_name="rota-parcial").add_to(busca)

            # cidade atual em destaque
            folium.CircleMarker(
                coords[atual], radius=8, color="#7b2cbf", fill=True, fill_opacity=1,
                tooltip=f"Atual: {bonito(atual)}",
            ).add_to(busca)
    else:
        # sem animação, ou no último passo: árvore completa + rota final
        if mostrar_exploracao:
            for d in detalhes:
                if d["pai"] is not None:
                    folium.PolyLine(
                        [coords[d["pai"]], coords[d["cidade"]]],
                        color="#141414", weight=1.5, opacity=0.6,
                    ).add_to(busca)
            for i, d in enumerate(detalhes, start=1):
                f = d["g"] + d["h"]
                folium.CircleMarker(
                    coords[d["cidade"]], radius=4, color="#e8590c", fill=True, fill_opacity=0.9,
                    tooltip=f"{i}º: {bonito(d['cidade'])} (g={d['g']:.1f}, h={d['h']:.1f}, f={f:.1f})",
                ).add_to(busca)

        pontos = [coords[c] for c in rota["caminho"]]
        folium.PolyLine(pontos, color="#4400FD", weight=6, opacity=1, class_name="rota-final").add_to(busca)

    folium.Marker(coords[rota["origem"]], tooltip=bonito(rota["origem"]), icon=folium.Icon(color="green")).add_to(mapa)
    folium.Marker(coords[rota["destino"]], tooltip=bonito(rota["destino"]), icon=folium.Icon(color="red")).add_to(mapa)

    st_folium(
        mapa,
        feature_group_to_add=busca,
        key=f"mapa_{rota['id']}",
        width=700,
        height=450,
        returned_objects=[],
    )