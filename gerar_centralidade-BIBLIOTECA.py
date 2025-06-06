import json
import networkx as nx

INPUT_FILE = "github_repos_contributors.json"
OUTPUT_BIPARTIDO = "grafo_bipartido.gexf"
OUTPUT_USUARIOS = "grafo_usuarios_centralidade-BIBLIOTECA.gexf"
OUTPUT_CENTRALIDADES = "centralidades_usuarios.json"

# Carrega JSON
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# Cria grafo bipartido 
B = nx.Graph()
for repo, users in data.items():
    B.add_node(repo, type="repo")
    for user in users:
        B.add_node(user, type="user")
        B.add_edge(user, repo)

# Separa usuários
usuarios = {n for n, d in B.nodes(data=True) if d["type"] == "user"}

# Projeta grafo de usuários (grafo unipartido com pesos)
G = nx.bipartite.weighted_projected_graph(B, usuarios)

# Calcula centralidades
centralidades = {
    "grau": dict(G.degree()),
    "grau_normalizado": nx.degree_centrality(G),
    "intermediacao": nx.betweenness_centrality(G, weight='weight'),
    "proximidade": nx.closeness_centrality(G),
    "agrupamento": nx.clustering(G, weight='weight'),
}

# Adiciona centralidades como atributos dos nós
for node in G.nodes():
    G.nodes[node]["grau"] = centralidades["grau"][node]
    G.nodes[node]["grau_normalizado"] = centralidades["grau_normalizado"][node]
    G.nodes[node]["intermediacao"] = centralidades["intermediacao"][node]
    G.nodes[node]["proximidade"] = centralidades["proximidade"][node]
    G.nodes[node]["agrupamento"] = centralidades["agrupamento"][node]

# Salva grafos
nx.write_gexf(B, OUTPUT_BIPARTIDO)
nx.write_gexf(G, OUTPUT_USUARIOS)

# Salva centralidades em JSON 
with open(OUTPUT_CENTRALIDADES, "w", encoding="utf-8") as f:
    json.dump(centralidades, f, indent=2)

print(f"Grafos salvos: {OUTPUT_BIPARTIDO}, {OUTPUT_USUARIOS}")
print(f"Centralidades salvas: {OUTPUT_CENTRALIDADES}")
