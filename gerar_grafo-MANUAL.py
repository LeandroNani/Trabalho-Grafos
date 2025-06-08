import json
import time  # Importa o módulo para medir tempo
import os
import psutil

# Marca o tempo de início
start_time = time.time()

# Caminhos dos arquivos de entrada e saída
INPUT_FILE = "github_repos_contributors.json"           # Arquivo JSON com o mapeamento: repositório → usuários
OUTPUT_GEXF_USUARIOS = "grafo_usuarios-MANUAL.gexf"             # Saída do grafo projetado apenas com usuários
OUTPUT_GEXF_BIPARTIDO = "grafo_bipartido-MANUAL.gexf"           # Saída do grafo bipartido (usuário ↔ repositório)

# === 1. Carrega os dados do JSON ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# === 2. Constrói o grafo bipartido ===
repos = set(data.keys())
usuarios = set()
bipartido = {}

for repo, devs in data.items():
    bipartido[repo] = set()
    for user in devs:
        bipartido[repo].add(user)
        usuarios.add(user)

# === 3. Projeta o grafo apenas com usuários ===
grafo_usuarios = {}

for repo, devs in bipartido.items():
    devs = list(devs)
    for i in range(len(devs)):
        for j in range(i + 1, len(devs)):
            u, v = devs[i], devs[j]
            if u not in grafo_usuarios:
                grafo_usuarios[u] = {}
            if v not in grafo_usuarios:
                grafo_usuarios[v] = {}
            grafo_usuarios[u][v] = grafo_usuarios[u].get(v, 0) + 1
            grafo_usuarios[v][u] = grafo_usuarios[v].get(u, 0) + 1

# === 4. Exporta o grafo bipartido em formato GEXF ===
with open(OUTPUT_GEXF_BIPARTIDO, "w", encoding="utf-8") as f:
    f.write("""<?xml version="1.0" encoding="UTF-8"?>
<gexf version="1.2" xmlns="http://www.gexf.net/1.2draft">
  <graph mode="static" defaultedgetype="undirected">
    <nodes>
""")
    for repo in repos:
        f.write(f'      <node id="{repo}" label="{repo}" type="repo" />\n')
    for user in usuarios:
        f.write(f'      <node id="{user}" label="{user}" type="user" />\n')

    f.write("""    </nodes>
    <edges>\n""")

    edge_id = 0
    for repo, devs in bipartido.items():
        for user in devs:
            f.write(f'      <edge id="{edge_id}" source="{user}" target="{repo}" weight="1" />\n')
            edge_id += 1

    f.write("""    </edges>
  </graph>
</gexf>
""")

print(f"✅ Grafo bipartido salvo em: {OUTPUT_GEXF_BIPARTIDO}")

# === 5. Exporta o grafo de usuários em formato GEXF ===
with open(OUTPUT_GEXF_USUARIOS, "w", encoding="utf-8") as f:
    f.write("""<?xml version="1.0" encoding="UTF-8"?>
<gexf version="1.2" xmlns="http://www.gexf.net/1.2draft">
  <graph mode="static" defaultedgetype="undirected">
    <nodes>
""")
    for user in usuarios:
        f.write(f'      <node id="{user}" label="{user}" />\n')

    f.write("""    </nodes>
    <edges>\n""")

    edge_id = 0
    added = set()
    for u in grafo_usuarios:
        for v, peso in grafo_usuarios[u].items():
            if (v, u) in added:
                continue
            f.write(f'      <edge id="{edge_id}" source="{u}" target="{v}" weight="{peso}" />\n')
            added.add((u, v))
            edge_id += 1

    f.write("""    </edges>
  </graph>
</gexf>
""")

print(f"✅ Grafo de usuários salvo em: {OUTPUT_GEXF_USUARIOS}")

# Marca o tempo final e calcula o tempo decorrido
end_time = time.time()
elapsed = end_time - start_time

# Medições adicionais
file_size_kb = os.path.getsize(INPUT_FILE) / 1024
num_usuarios = len(usuarios)
num_repos = len(repos)
num_nos_grafo_usuarios = len(grafo_usuarios)
num_arestas_grafo_usuarios = len(added)
process = psutil.Process(os.getpid())
mem_used = process.memory_info().rss / (1024 * 1024)

print(f"⏱️ Tempo total de execução grafo gerado manualmente: {elapsed:.2f} segundos")
print(f"📦 Tamanho do arquivo de entrada: {file_size_kb:.2f} KB")
print(f"👤 Número de usuários: {num_usuarios}")
print(f"📁 Número de repositórios: {num_repos}")
print(f"📊 Nós no grafo de usuários: {num_nos_grafo_usuarios}")
print(f"🔗 Arestas no grafo de usuários: {num_arestas_grafo_usuarios}")
print(f"🧠 Memória RAM usada durante execução: {mem_used:.2f} MB")