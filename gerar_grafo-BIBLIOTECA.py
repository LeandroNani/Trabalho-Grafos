import json
import networkx as nx
import time
import os
import psutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

start_time = time.time()

INPUT_FILE = "github_repos_contributors.json"
OUTPUT_BIPARTIDO = "grafo_bipartido-BIBLIOTECA.gexf"
OUTPUT_USUARIOS = "grafo_usuarios-BIBLIOTECA.gexf"

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

end_time = time.time()
elapsed_time = end_time - start_time

# Medições adicionais
file_size_kb = os.path.getsize(INPUT_FILE) / 1024
process = psutil.Process(os.getpid())
mem_used = process.memory_info().rss / (1024 * 1024)

print(f"✅ Grafo bipartido salvo em: {OUTPUT_BIPARTIDO}")
print(f"✅ Grafo de usuários salvo em: {OUTPUT_USUARIOS}")
print(f"⏱️ Tempo total de execução: {elapsed_time:.2f} segundos")
print(f"📦 Tamanho do arquivo de entrada: {file_size_kb:.2f} KB")
print(f"👤 Número de usuários: {len(usuarios)}")
print(f"📁 Número de repositórios: {len(data)}")
print(f"📊 Nós no grafo de usuários: {G.number_of_nodes()}")
print(f"🔗 Arestas no grafo de usuários: {G.number_of_edges()}")
print(f"🧠 Memória RAM usada durante execução: {mem_used:.2f} MB")