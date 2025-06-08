import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# === Autenticação na API do GitHub ===
usuario = os.getenv("GITHUB_USERNAME")
token = os.getenv("GITHUB_TOKEN")
auth = (usuario, token)

# === Parâmetros da coleta ===
REPO_COUNT = 200              # número de repositórios a coletar
CONTRIBUTOR_LIMIT = 100      # número máximo de contribuidores por repositório
OUTPUT_FILE = "github_repos_contributors.json"

if os.path.exists(OUTPUT_FILE):
    print(f"Arquivo '{OUTPUT_FILE}' já existe. Pulando coleta de dados.")
    print("Para executar novamente, renomeie ou remova o arquivo existente.")
    print("⚠️  não é necessário executar novamente a coleta, a menos que queira atualizar os dados.")
    exit(0)

# === Função para buscar os repositórios mais populares ===
def fetch_top_repositories(count=50):
    repos = []
    page = 1
    while len(repos) < count:
        url = f"https://api.github.com/search/repositories?q=stars:>10000+size:>1000&sort=stars&order=desc&per_page=100&page={page}"
        r = requests.get(url, auth=auth)
        data = r.json()
        
        if "items" not in data:
            break
        
        for item in data["items"]:
            repos.append({
                "name": item["name"],
                "owner": item["owner"]["login"]
            })
            if len(repos) >= count:
                break

        page += 1
        time.sleep(1)

    return repos

# === Função para buscar os contribuidores de cada repositório ===
def fetch_contributors(owner, repo, limit=CONTRIBUTOR_LIMIT):
    contributors = []
    page = 1
    while len(contributors) < limit:
        url = f"https://api.github.com/repos/{owner}/{repo}/contributors?anon=1&per_page=100&page={page}"
        r = requests.get(url, auth=auth)
        
        if r.status_code != 200:
            break

        data = r.json()
        if not data:
            break

        for user in data:
            if "login" in user and "contributions" in user:
                if "bot" in user["login"].lower():
                    continue
                if user["contributions"] < 5:
                    continue
                contributors.append((user["login"], user["contributions"]))

        if len(data) < 100:
            break
        page += 1
        time.sleep(0.5)

    contributors.sort(key=lambda x: x[1], reverse=True)
    return [user[0] for user in contributors[:limit]]

# === Início do cronômetro ===
start_time = time.time()

# === Execução principal da coleta ===
repo_contrib_data = {}
repos = fetch_top_repositories(REPO_COUNT)

for repo in repos:
    print(f"Coletando: {repo['owner']}/{repo['name']}")
    contributors = fetch_contributors(repo['owner'], repo['name'], CONTRIBUTOR_LIMIT)
    
    if contributors:
        key = f"{repo['owner']}/{repo['name']}"
        repo_contrib_data[key] = contributors
    
    time.sleep(1)

# === Salva os dados no arquivo JSON ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(repo_contrib_data, f, indent=2, ensure_ascii=False)

# === Fim do cronômetro e exibição do tempo gasto ===
end_time = time.time()
elapsed = end_time - start_time
minutes, seconds = divmod(int(elapsed), 60)
print(f"\n✅ Finalizado. Dados salvos em: {OUTPUT_FILE}")
print(f"⏱️ Tempo total de execução: {minutes} minutos e {seconds} segundos.")