import requests
import json
import time

# === Autenticação na API do GitHub ===
usuario = os.getenv("GITHUB_USERNAME")
token = os.getenv("GITHUB_TOKEN")
auth = (usuario, token)

# === Parâmetros da coleta ===
REPO_COUNT = 50              # número de repositórios a coletar
CONTRIBUTOR_LIMIT = 100      # número máximo de contribuidores por repositório
OUTPUT_FILE = "github_repos_contributors.json"

# === Função para buscar os repositórios mais populares ===
def fetch_top_repositories(count=50):
    repos = []
    page = 1
    while len(repos) < count:
        # Busca repositórios com mais de 10000 estrelas e tamanho de código relevante (> 1000)
        url = f"https://api.github.com/search/repositories?q=stars:>10000+size:>1000&sort=stars&order=desc&per_page=100&page={page}"
        r = requests.get(url, auth=auth)
        data = r.json()
        
        if "items" not in data:
            break  # erro ou fim da busca
        
        for item in data["items"]:
            repos.append({
                "name": item["name"],
                "owner": item["owner"]["login"]
            })
            if len(repos) >= count:
                break

        page += 1
        time.sleep(1)  # pausa para evitar limite da API

    return repos

# === Função para buscar os contribuidores de cada repositório ===
def fetch_contributors(owner, repo, limit=500):
    contributors = []
    page = 1
    while len(contributors) < limit:
        url = f"https://api.github.com/repos/{owner}/{repo}/contributors?anon=1&per_page=100&page={page}"
        r = requests.get(url, auth=auth)
        
        if r.status_code != 200:
            break  # erro na requisição

        data = r.json()
        if not data:
            break

        for user in data:
            # === Filtro 1: Ignora bots ===
            if "login" in user and "contributions" in user:
                if "bot" in user["login"].lower():
                    continue  # ignora bots como dependabot[bot]

                # === Filtro 2: mínimo de 5 contribuições ===
                if user["contributions"] < 5:
                    continue  # ignora contribuições irrelevantes

                contributors.append((user["login"], user["contributions"]))

        if len(data) < 100:
            break  # última página
        page += 1
        time.sleep(0.5)  # pausa para evitar rate limit

    # Ordena os contribuidores por número de contribuições (decrescente)
    contributors.sort(key=lambda x: x[1], reverse=True)

    # Retorna apenas os logins dos top N contribuidores
    return [user[0] for user in contributors[:limit]]

# === Execução principal da coleta ===
repo_contrib_data = {}        # estrutura: { "repo": [user1, user2, ...] }
repos = fetch_top_repositories(REPO_COUNT)

# Para cada repositório, busca os contribuidores filtrados
for repo in repos:
    print(f"Coletando: {repo['owner']}/{repo['name']}")
    contributors = fetch_contributors(repo['owner'], repo['name'], CONTRIBUTOR_LIMIT)
    
    if contributors:
        key = f"{repo['owner']}/{repo['name']}"
        repo_contrib_data[key] = contributors
    
    time.sleep(1)  # pausa entre repositórios

# === Salva os dados no arquivo JSON ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(repo_contrib_data, f, indent=2, ensure_ascii=False)

print(f"Finalizado. Dados salvos em: {OUTPUT_FILE}")
