import json
from collections import defaultdict, deque
from itertools import combinations

INPUT_FILE = "github_repos_contributors.json"
OUTPUT_CENTRALIDADES = "centralidades_usuarios.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# 1. Criar grafo bipartido manualmente
repos = data.keys()
usuarios = set()
edges = defaultdict(set)

for repo, users in data.items():
    for user in users:
        usuarios.add(user)
        edges[user].add(repo)
        edges[repo].add(user)

# 2. Criar grafo projetado entre usuários (ligar usuários que contribuíram para o mesmo repositório)
grafo_usuarios = defaultdict(lambda: defaultdict(int))

for repo, users in data.items():
    for u1, u2 in combinations(users, 2):
        grafo_usuarios[u1][u2] += 1
        grafo_usuarios[u2][u1] += 1

# 3. Calcular centralidades

def grau(grafo):
    return {n: len(vizinhos) for n, vizinhos in grafo.items()}

def grau_normalizado(grafo):
    n = len(grafo) - 1
    return {node: len(adj)/n for node, adj in grafo.items()}

def bfs_distances(graph, start):
    visited = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited[neighbor] = visited[node] + 1
                queue.append(neighbor)
    return visited

def proximidade(grafo):
    result = {}
    for node in grafo:
        dist = bfs_distances(grafo, node)
        if len(dist) > 1:
            result[node] = (len(dist) - 1) / sum(dist.values())
        else:
            result[node] = 0
    return result

def intermediacao(grafo):
    # Algoritmo de Brandes simplificado para grafos não ponderados
    centralidade = dict.fromkeys(grafo, 0.0)
    for s in grafo:
        stack = []
        pred = {w: [] for w in grafo}
        sigma = dict.fromkeys(grafo, 0.0); sigma[s] = 1.0
        dist = dict.fromkeys(grafo, -1); dist[s] = 0
        queue = deque([s])
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
                centralidade[w] += delta[w]
    return centralidade

# 4. Calcular e salvar centralidades
centralidades = {
    "grau": grau(grafo_usuarios),
    "grau_normalizado": grau_normalizado(grafo_usuarios),
    "proximidade": proximidade(grafo_usuarios),
    "intermediacao": intermediacao(grafo_usuarios)
}

with open(OUTPUT_CENTRALIDADES, "w", encoding="utf-8") as f:
    json.dump(centralidades, f, indent=2)

print(f"Centralidades salvas em: {OUTPUT_CENTRALIDADES}")