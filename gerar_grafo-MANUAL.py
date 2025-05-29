import json

# Caminhos dos arquivos de entrada e saída
INPUT_FILE = "github_repos_contributors.json"           # Arquivo JSON com o mapeamento: repositório → usuários
OUTPUT_GEXF_USUARIOS = "grafo_usuarios.gexf"             # Saída do grafo projetado apenas com usuários
OUTPUT_GEXF_BIPARTIDO = "grafo_bipartido.gexf"           # Saída do grafo bipartido (usuário ↔ repositório)

# === 1. Carrega os dados do JSON ===
# Estrutura esperada:
# {
#   "owner1/repo1": ["userA", "userB", ...],
#   "owner2/repo2": ["userA", "userC", ...],
# }
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# === 2. Constrói o grafo bipartido ===
# - Um conjunto de repositórios (repos)
# - Um conjunto de usuários (usuarios)
# - Um dicionário 'bipartido' onde cada chave é um repo e o valor é o conjunto de usuários que contribuíram nele
repos = set(data.keys())
usuarios = set()
bipartido = {}

for repo, devs in data.items():
    bipartido[repo] = set()
    for user in devs:
        bipartido[repo].add(user)
        usuarios.add(user)

# === 3. Projeta o grafo apenas com usuários ===
# - Dois usuários são conectados se contribuíram para o mesmo repositório
# - O peso da aresta representa quantos repositórios os dois têm em comum
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
# - Nós de tipo "repo" e "user"
# - Arestas conectando usuário → repositório com peso 1
with open(OUTPUT_GEXF_BIPARTIDO, "w", encoding="utf-8") as f:
    f.write("""<?xml version="1.0" encoding="UTF-8"?>
<gexf version="1.2" xmlns="http://www.gexf.net/1.2draft">
  <graph mode="static" defaultedgetype="undirected">
    <nodes>
""")
    # Adiciona os repositórios como nós do tipo "repo"
    for repo in repos:
        f.write(f'      <node id="{repo}" label="{repo}" type="repo" />\n')
    # Adiciona os usuários como nós do tipo "user"
    for user in usuarios:
        f.write(f'      <node id="{user}" label="{user}" type="user" />\n')

    f.write("""    </nodes>
    <edges>\n""")

    # Cria arestas entre usuários e repositórios com peso fixo 1
    edge_id = 0
    for repo, devs in bipartido.items():
        for user in devs:
            f.write(f'      <edge id="{edge_id}" source="{user}" target="{repo}" weight="1" />\n')
            edge_id += 1

    f.write("""    </edges>
  </graph>
</gexf>
""")

print(f"Grafo bipartido salvo em: {OUTPUT_GEXF_BIPARTIDO}")

# === 5. Exporta o grafo de usuários em formato GEXF ===
# - Apenas nós do tipo usuário
# - Arestas entre usuários com pesos baseados na quantidade de repositórios compartilhados
with open(OUTPUT_GEXF_USUARIOS, "w", encoding="utf-8") as f:
    f.write("""<?xml version="1.0" encoding="UTF-8"?>
<gexf version="1.2" xmlns="http://www.gexf.net/1.2draft">
  <graph mode="static" defaultedgetype="undirected">
    <nodes>
""")
    # Adiciona todos os usuários como nós
    for user in usuarios:
        f.write(f'      <node id="{user}" label="{user}" />\n')

    f.write("""    </nodes>
    <edges>\n""")

    # Cria arestas ponderadas entre usuários
    edge_id = 0
    added = set()  # evita duplicação em grafos não direcionados
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

print(f"Grafo de usuários salvo em: {OUTPUT_GEXF_USUARIOS}")
