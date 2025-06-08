import json
import time
import os
import psutil
from collections import defaultdict, deque
from itertools import combinations
import sys

sys.stdout.reconfigure(encoding='utf-8')

# === Timer começa ===
start_time = time.time()

INPUT_FILE              = "github_repos_contributors.json"
OUTPUT_CENTRALIDADES    = "centralidades_usuarios-MANUAL.json"
OUTPUT_USUARIOS         = "grafo_centralidade-MANUAL.gexf"

# ---------------------------------------------------------------------------
# 1. Carrega os dados
# ---------------------------------------------------------------------------
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# ---------------------------------------------------------------------------
# 2. Constrói grafo bipartido
# ---------------------------------------------------------------------------
repos     = data.keys()
usuarios  = set()
edges     = defaultdict(set)

for repo, users in data.items():
    for user in users:
        usuarios.add(user)
        edges[user].add(repo)
        edges[repo].add(user)

# ---------------------------------------------------------------------------
# 3. Projeta grafo de usuários
# ---------------------------------------------------------------------------
grafo_usuarios = defaultdict(lambda: defaultdict(int))

for repo, users in data.items():
    for u1, u2 in combinations(users, 2):
        grafo_usuarios[u1][u2] += 1
        grafo_usuarios[u2][u1] += 1

# ---------------------------------------------------------------------------
# 4. Funções de centralidade
# ---------------------------------------------------------------------------
def grau(grafo):
    return {n: len(vizinhos) for n, vizinhos in grafo.items()}

def grau_normalizado(grafo):
    n = len(grafo) - 1 or 1
    return {node: len(adj) / n for node, adj in grafo.items()}

def bfs_distances(graph, start):
    visited = {start: 0}
    queue   = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited[neighbor] = visited[node] + 1
                queue.append(neighbor)
    return visited

def proximidade(grafo):
    res = {}
    for node in grafo:
        dist = bfs_distances(grafo, node)
        if len(dist) > 1:
            res[node] = (len(dist) - 1) / sum(dist.values())
        else:
            res[node] = 0
    return res

def intermediacao(grafo):
    C = dict.fromkeys(grafo, 0.0)
    for s in grafo:
        stack, pred = [], {w: [] for w in grafo}
        sigma       = dict.fromkeys(grafo, 0.0); sigma[s] = 1.0
        dist        = dict.fromkeys(grafo, -1);  dist[s]  = 0
        queue       = deque([s])

        while queue:
            v = queue.popleft()
            stack.append(v)
            for w in grafo[v]:
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)

        delta = dict.fromkeys(grafo, 0)
        while stack:
            w = stack.pop()
            for v in pred[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
            if w != s:
                C[w] += delta[w]
    return C

def agrupamento(grafo):
    clustering = {}
    for node, neighbors in grafo.items():
        k = len(neighbors)
        if k < 2:
            clustering[node] = 0.0
            continue

        links = 0
        for u, v in combinations(neighbors, 2):
            if u in grafo[v]:
                links += 1

        clustering[node] = (2 * links) / (k * (k - 1))
    return clustering

# ---------------------------------------------------------------------------
# 5. Calcula e salva centralidades
# ---------------------------------------------------------------------------
centralidades = {
    "grau":             grau(grafo_usuarios),
    "grau_normalizado": grau_normalizado(grafo_usuarios),
    "proximidade":      proximidade(grafo_usuarios),
    "intermediacao":    intermediacao(grafo_usuarios),
    "agrupamento":      agrupamento(grafo_usuarios)
}

with open(OUTPUT_CENTRALIDADES, "w", encoding="utf-8") as f:
    json.dump(centralidades, f, indent=2)

print(f"✅ Centralidades salvas em: {OUTPUT_CENTRALIDADES}")

# ---------------------------------------------------------------------------
# 6. Exporta o grafo em GEXF
# ---------------------------------------------------------------------------
with open(OUTPUT_USUARIOS, "w", encoding="utf-8") as f:
    f.write(
"""<?xml version="1.0" encoding="UTF-8"?>
<gexf version="1.2" xmlns="http://www.gexf.net/1.2draft">
  <graph mode="static" defaultedgetype="undirected">
    <nodes>\n""")

    for user in usuarios:
        f.write(f'      <node id="{user}" label="{user}" />\n')

    f.write(
"""    </nodes>
    <edges>\n""")

    edge_id = 0
    seen    = set()
    for u in grafo_usuarios:
        for v, peso in grafo_usuarios[u].items():
            if (v, u) in seen:
                continue
            f.write(f'      <edge id="{edge_id}" source="{u}" target="{v}" weight="{peso}" />\n')
            seen.add((u, v))
            edge_id += 1

    f.write(
"""    </edges>
  </graph>
</gexf>
""")

print(f"✅ Grafos salvos em: {OUTPUT_USUARIOS}")

# ---------------------------------------------------------------------------
# Medições
# ---------------------------------------------------------------------------
elapsed_time = time.time() - start_time
file_size_kb = os.path.getsize(INPUT_FILE) / 1024
process = psutil.Process(os.getpid())
mem_used = process.memory_info().rss / (1024 * 1024)

num_nos = len(grafo_usuarios)
num_arestas = sum(len(v) for v in grafo_usuarios.values()) // 2

print(f"⏱️ Tempo total de execução: {elapsed_time:.2f} segundos")
print(f"📦 Tamanho do arquivo de entrada: {file_size_kb:.2f} KB")
print(f"👤 Número de usuários: {len(usuarios)}")
print(f"📁 Número de repositórios: {len(data)}")
print(f"📊 Nós no grafo de usuários: {num_nos}")
print(f"🔗 Arestas no grafo de usuários: {num_arestas}")
print(f"🧠 Memória RAM usada durante execução: {mem_used:.2f} MB")