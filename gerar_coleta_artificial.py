import json

# Esse script gera dados artificiais de usuários e repositórios 
# para simular uma grande base de contribuições sem depender da coleta real pela API do GitHub
# que é lenta e limitada por restrições de taxa. 
# Assim, é possível testar e desenvolver funcionalidades com uma grande quantidade de dados 
# de forma rápida, controlada e sem sobrecarregar serviços externos.

REPO_COUNT = 200
USER_COUNT = 5000
OUTPUT_FILE = "github_repos_contributors.json"

repo_contrib_data = {}

for i in range(1, REPO_COUNT + 1):
    owner = f"owner_{i:03d}"
    repo = f"repo_{i:03d}"
    key = f"{owner}/{repo}"
    
    contributors = [f"user_{j:05d}" for j in range(1, USER_COUNT + 1)]
    repo_contrib_data[key] = contributors

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(repo_contrib_data, f, indent=2, ensure_ascii=False)

print(f"Dados artificiais salvos em: {OUTPUT_FILE}")