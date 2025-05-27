import requests
import json
import time

usuario = "seu_usuario"
token = "seu_token"
auth = (usuario, token)

REPO_COUNT = 50
CONTRIBUTOR_LIMIT = 500
OUTPUT_FILE = "github_repos_contributors.json"

def fetch_top_repositories(count=50):
    repos = []
    page = 1
    while len(repos) < count:
        url = f"https://api.github.com/search/repositories?q=stars:>10000&sort=stars&order=desc&per_page=100&page={page}"
        r = requests.get(url, auth=auth)
        data = r.json()
        if "items" not in data:
            break
        for item in data["items"]:
            repos.append({"name": item["name"], "owner": item["owner"]["login"]})
            if len(repos) >= count:
                break
        page += 1
        time.sleep(1)
    return repos

def fetch_contributors(owner, repo, limit=500):
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
        contributors.extend([(user["login"], user.get("contributions", 0)) for user in data if "login" in user])
        if len(data) < 100:
            break
        page += 1
        time.sleep(0.5)
    
    # ordena por nº de contribuições e retorna os logins dos top contribuidores
    contributors.sort(key=lambda x: x[1], reverse=True)
    return [user[0] for user in contributors[:limit]]

# Coleta
repo_contrib_data = {}
repos = fetch_top_repositories(REPO_COUNT)

for repo in repos:
    print(f"Coletando: {repo['owner']}/{repo['name']}")
    contributors = fetch_contributors(repo['owner'], repo['name'], CONTRIBUTOR_LIMIT)
    if contributors:
        key = f"{repo['owner']}/{repo['name']}"
        repo_contrib_data[key] = contributors
    time.sleep(1)

# Salva JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(repo_contrib_data, f, indent=2, ensure_ascii=False)

print(f"Finalizado. Dados salvos em: {OUTPUT_FILE}")
