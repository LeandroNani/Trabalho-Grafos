import json
import networkx as nx

INPUT_FILE = "github_repos_contributors.json"
OUTPUT_BIPARTIDO = "grafo_bipartido.gexf"
OUTPUT_USUARIOS = "grafo_usuarios.gexf"

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

# Projeta grafo de usuários
G = nx.bipartite.weighted_projected_graph(B, usuarios)

# Salva arquivos para Gephi
nx.write_gexf(B, OUTPUT_BIPARTIDO)
nx.write_gexf(G, OUTPUT_USUARIOS)

print(f"Grafo bipartido salvo em: {OUTPUT_BIPARTIDO}")
print(f"Grafo de usuários salvo em: {OUTPUT_USUARIOS}")