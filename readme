# 📊 Análise de Redes de Contribuição no GitHub

## 📄 Resumo do projeto
### 🔹 Coleta de dados
Um script em Python acessa a API pública do GitHub com autenticação via token. O algoritmo busca os **50 repositórios mais populares** (com base em estrelas) e coleta até **100 contribuidores** para cada repositório, ordenados por número de contribuições.

Os dados são armazenados em um arquivo JSON: github_repos_contributors.json.

Esse arquivo contém um mapeamento de repositórios para seus respectivos contribuidores.

### 🧹 Filtragem de Dados
Durante as primeiras execuções do projeto, foi identificado um problema: o grafo gerado tinha um **nó central artificial**, representado por `dependabot[bot]`. Esse bot do GitHub contribui automaticamente em centenas de repositórios, o que fazia com que ele se conectasse a quase todos os outros nós da rede.

Além disso, percebemos que muitas conexões entre usuários tinham peso **muito baixo** (no máximo 3), indicando que poucos usuários colaboravam juntos em múltiplos repositórios.

Para resolver esses problemas, aplicamos a seguinte filtragem na etapa de mineração:

- **Bots** (como `dependabot[bot]`) foram ignorados, removendo contribuições automatizadas da rede;
- Apenas usuários com **5 ou mais contribuições** foram considerados, garantindo relevância nas interações;
- A busca por repositórios passou a considerar apenas projetos **populares e ativos**, com **mais de 10.000 estrelas** e **tamanho superior a 1000 linhas de código**.

Essas mudanças aumentaram a qualidade do grafo, reduziram ruídos e tornaram as métricas de centralidade, agrupamento e comunidades mais confiáveis no Gephi.

---

### 🔹 Construção do Grafo Bipartido
A partir dos dados coletados, é construído um **grafo bipartido** contendo dois tipos de nós:

- Usuários (contribuidores)
- Repositórios

As arestas representam a relação de contribuição entre usuários e repositórios.

---

### 🔹 Projeção do Grafo de Usuários

A partir do grafo bipartido, é gerado um grafo contendo apenas usuários, onde:

- Cada nó representa um usuário;
- Há uma aresta entre dois usuários se eles contribuíram para ao menos um repositório em comum;
- O **peso da aresta** representa o número de repositórios compartilhados.

Esse grafo é utilizado para análises de:

- Grau
- Centralidade
- Agrupamento
- Comunidades

---

### 🔹 Exportação dos Grafos

A exportação dos grafos foi feita em **dois modos distintos**:

- `gerar_grafo-MANUAL.py`: gera os arquivos `.gexf` manualmente, **sem uso de bibliotecas externas**, apenas com escrita direta no formato XML/GEXF;
- `gerar_grafo-BIBLIOTECA.py`: utiliza a biblioteca `networkx` para geração e exportação automática dos grafos.

Ambas versões geram os seguintes arquivos:

- `grafo_bipartido.gexf`
- `grafo_usuarios.gexf`

Esses arquivos são compatíveis com o **Gephi** para visualização e análise.

---

### 🔹 Visualização com Gephi – ForceAtlas 2

Para explorar os grafos visualmente, recomenda-se utilizar o layout **ForceAtlas 2** no Gephi.

Esse layout simula forças físicas:

- **Arestas agem como molas** entre os nós conectados;
- **Nós desconectados se repelem**;
- **Grupos altamente conectados se agrupam naturalmente**.

Com isso, o ForceAtlas 2 permite:

- Identificar **comunidades** visualmente;
- Detectar **usuários centrais** ou influentes;
- Facilitar a análise de estruturas densas ou periféricas.

---

## 🧰 Tecnologias Utilizadas

- Python 3.x
- API REST do GitHub
- Gephi 0.10+ (para visualização)
- `networkx` (opcional, apenas na versão com biblioteca)
