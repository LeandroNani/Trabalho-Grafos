import json
import networkx as nx
import time
import os
import psutil  # Biblioteca para medições do sistema

start_time = time.time()
process = psutil.Process(os.getpid())

INPUT_FILE = "github_repos_contributors.json"
OUTPUT_USUARIOS = "grafo_usuarios_centralidade-BIBLIOTECA.gexf"
OUTPUT_CENTRALIDADES = "centralidades_usuarios-BIBLIOTECA.json"

# Medição inicial de memória
mem_before = process.memory_info().rss / (1024 * 1024)  # em MB

# === Carrega JSON e mede tamanho ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw_data = f.read()
    file_size_kb = len(raw_data.encode("utf-8")) / 1024
    data = json.loads(raw_data)

# === Cria grafo bipartido ===
B = nx.Graph()
for repo, users in data.items():
    B.add_node(repo, type="repo")
    for user in users:
        B.add_node(user, type="user")
        B.add_edge(user, repo)

# === Separa usuários ===
usuarios = {n for n, d in B.nodes(data=True) if d["type"] == "user"}

# === Projeta grafo de usuários ===
G = nx.bipartite.weighted_projected_graph(B, usuarios)

# === Calcula centralidades ===
centralidades = {
    "grau": dict(G.degree()),
    "grau_normalizado": nx.degree_centrality(G),
    "intermediacao": nx.betweenness_centrality(G, weight='weight'),
    "proximidade": nx.closeness_centrality(G),
    "agrupamento": nx.clustering(G, weight='weight'),
}

# === Adiciona centralidades como atributos ===
for node in G.nodes():
    G.nodes[node]["grau"] = centralidades["grau"][node]
    G.nodes[node]["grau_normalizado"] = centralidades["grau_normalizado"][node]
    G.nodes[node]["intermediacao"] = centralidades["intermediacao"][node]
    G.nodes[node]["proximidade"] = centralidades["proximidade"][node]
    G.nodes[node]["agrupamento"] = centralidades["agrupamento"][node]

# === Salva grafos e centralidades ===
nx.write_gexf(G, OUTPUT_USUARIOS)
with open(OUTPUT_CENTRALIDADES, "w", encoding="utf-8") as f:
    json.dump(centralidades, f, indent=2)

# === Medições finais ===
end_time = time.time()
elapsed_time = end_time - start_time
mem_after = process.memory_info().rss / (1024 * 1024)  # em MB
mem_used = mem_after - mem_before

print(f"✅ Grafos salvos em: {OUTPUT_USUARIOS}")
print(f"✅ Centralidades salvas em: {OUTPUT_CENTRALIDADES}")
print(f"⏱️ Tempo total de execução: {elapsed_time:.2f} segundos")
print(f"📦 Tamanho do arquivo de entrada: {file_size_kb:.2f} KB")
print(f"👤 Número de usuários: {len(usuarios)}")
print(f"📁 Número de repositórios: {len(data)}")
print(f"📊 Nós no grafo de usuários: {G.number_of_nodes()}")
print(f"🔗 Arestas no grafo de usuários: {G.number_of_edges()}")
print(f"🧠 Memória RAM usada durante execução: {mem_used:.2f} MB")