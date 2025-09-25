import osmnx as ox  # Biblioteca para baixar e manipular dados do OpenStreetMap
import networkx as nx  # Biblioteca para trabalhar com grafos e rotas
import matplotlib.pyplot as plt  # Biblioteca para gráficos e mapas
import contextily as ctx  # Biblioteca para adicionar mapa de fundo

# ============================
# Solicitar endereços ao usuário
# ============================
origem_nome = input("Digite o ponto de partida (ex: Av.Tuparendi, Santa Rosa, RS, Brazil): ")  # Recebe endereço de origem
destino_nome = input("Digite o destino (ex: Av.Tuparendi, Santa Rosa, RS, Brazil): ")  # Recebe endereço de destino

# ============================
# Converter endereços em coordenadas
# ============================
inicio_coords = ox.geocode(origem_nome)  # Converte endereço de origem em coordenadas (latitude, longitude)
destino_coords = ox.geocode(destino_nome)  # Converte endereço de destino em coordenadas (latitude, longitude)

# ============================
# Baixar o grafo da região
# ============================
grafo = ox.graph_from_point(inicio_coords, dist=7000, network_type="drive_service")  # Baixa grafo de ruas em raio de 7km

# ============================
# Adicionar velocidades médias e tempos estimados
# ============================
grafo = ox.add_edge_speeds(grafo)  # Adiciona velocidade média nas ruas
grafo = ox.add_edge_travel_times(grafo)  # Adiciona tempo estimado de viagem nas ruas

# ============================
# Encontrar os nós mais próximos
# ============================
orig_node = ox.distance.nearest_nodes(grafo, inicio_coords[1], inicio_coords[0])  # Encontra nó mais próximo da origem
dest_node = ox.distance.nearest_nodes(grafo, destino_coords[1], destino_coords[0])  # Encontra nó mais próximo do destino

# ============================
# Criar barreiras 
# ============================
barreiras = [  # Lista de coordenadas de barreiras
    (-27.851760459423247, -54.49118868655551),
    (-27.84710354436662, -54.48309745861554),
    (-27.863107821940233, -54.470706160794286),
    (-27.86348721192122, -54.46620708592884),
    (-27.863090198190353, -54.46956657579822),
]
barreiras_nodes = [ox.distance.nearest_nodes(grafo, lon, lat) for lat, lon in barreiras]  # Encontra nós mais próximos das barreiras

# Remove ruas ligadas às barreiras
for node in barreiras_nodes:  # Para cada nó de barreira
    if node in grafo:  # Se o nó existe no grafo
        grafo.remove_edges_from(list(grafo.edges(node)))  # Remove todas as ruas ligadas ao nó

# Verificar se origem e destino ainda existem
if orig_node not in grafo or dest_node not in grafo:  # Se origem ou destino foram removidos
    raise ValueError("Origem ou destino foram removidos pelo bloqueio!")  # Erro se não existem
if not nx.has_path(grafo, orig_node, dest_node):  # Se não existe caminho entre origem e destino
    raise ValueError("❌ Não existe rota disponível após aplicar barreiras.")  # Erro se não existe rota

# ============================
# Função auxiliar para distância euclidiana (heurística do A*)
# ============================
def distancia_euclidiana(u, v):
    x1, y1 = grafo.nodes[u]["x"], grafo.nodes[u]["y"]  # Coordenadas do nó u
    x2, y2 = grafo.nodes[v]["x"], grafo.nodes[v]["y"]  # Coordenadas do nó v
    return ((x1 - x2)**2 + (y1 - y2)**2)**0.5  # Distância euclidiana entre u e v

# ============================
# Função para calcular distância total (km) e tempo total (min) de uma rota
# ============================
def calcular_distancia_tempo(caminho, grafo_ref, peso="length"):
    distancia_m = sum(grafo_ref[u][v][0][peso] for u, v in zip(caminho[:-1], caminho[1:]))  # Soma das distâncias dos segmentos
    distancia_km = distancia_m / 1000  # Converte metros para quilômetros
    tempo_seg = sum(grafo_ref[u][v][0]["travel_time"] for u, v in zip(caminho[:-1], caminho[1:]))  # Soma dos tempos dos segmentos
    tempo_min = (tempo_seg / 60) * 1.4  # Converte para minutos e aumenta 40% para simular tráfego
    return distancia_km, tempo_min  # Retorna distância em km e tempo em minutos

# ============================
# Calcular rota curta usando A* (menor distância)
# ============================
rota_curta = nx.astar_path(
    grafo, orig_node, dest_node,
    weight="length",
    heuristic=distancia_euclidiana
)  # Calcula rota mais curta usando A* (menor distância)
dist_curta, tempo_curta = calcular_distancia_tempo(rota_curta, grafo, peso="length")  # Calcula distância e tempo da rota curta

# ============================
# Calcular rota longa usando Dijkstra (mais lenta, normal)
# ============================
rota_longa = nx.shortest_path(grafo, orig_node, dest_node, weight="travel_time")  # Calcula rota mais rápida (menor tempo)
dist_longa, tempo_longa = calcular_distancia_tempo(rota_longa, grafo, peso="length")  # Calcula distância e tempo da rota longa

# ============================
# Mostrar informações no console
# ============================
print(f"🚗 Rota Curta (A*): {dist_curta:.2f} km | ⏱️ {tempo_curta:.0f} min")  # Exibe dados da rota curta
print(f"🚗 Rota Longa (normal): {dist_longa:.2f} km | ⏱️ {tempo_longa:.0f} min")  # Exibe dados da rota longa

# ============================
# Plotar as rotas no mapa
# ============================
fig, ax = ox.plot_graph_routes(
    grafo, [rota_curta, rota_longa],
    route_colors=["blue", "red"],
    route_linewidth=3, node_size=0, bgcolor="white", show=False, close=False
)  # Plota as duas rotas no mapa

# Marcar início e fim
x_in, y_in = grafo.nodes[orig_node]['x'], grafo.nodes[orig_node]['y']  # Coordenadas do início
x_out, y_out = grafo.nodes[dest_node]['x'], grafo.nodes[dest_node]['y']  # Coordenadas do destino
ax.scatter(x_in, y_in, c="blue", s=30, label="Início")  # Marca início no mapa
ax.scatter(x_out, y_out, c="green", s=30, label="Destino")  # Marca destino no mapa

# Adicionar mapa de fundo real
ctx.add_basemap(ax, crs=grafo.graph['crs'], source=ctx.providers.CartoDB.Positron)  # Adiciona mapa real de fundo

# Adicionar textos com informações das rotas
ax.text(
    0.02, 0.97,
    f"Rota Curta (A*): {dist_curta:.2f} km | {tempo_curta:.0f} min",
    color="blue", fontsize=11, fontweight='bold',
    transform=ax.transAxes,
    bbox=dict(facecolor='white', alpha=0.7, edgecolor='blue')
)  # Texto com dados da rota curta
ax.text(
    0.02, 0.93,
    f"Rota Longa (normal): {dist_longa:.2f} km | {tempo_longa:.0f} min",
    color="red", fontsize=11, fontweight='bold',
    transform=ax.transAxes,
    bbox=dict(facecolor='white', alpha=0.7, edgecolor='red')
)  # Texto com dados da rota longa

# Salvar imagem final
fig.savefig("GPS.png", dpi=300, bbox_inches="tight")  # Salva imagem do mapa com rotas
plt.close(fig)  # Fecha figura para liberar memória

print("🖼️ Mapa salvo como GPS.png")  # Mensagem final de sucesso