<a name="readme-top"></a>

<div align="center">
  <h1 align="center">tcr_community</h1>
  <p align="center">
    A short description of the project.
    <br />
    <br />
    <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Status-Development-yellow?style=for-the-badge" alt="Status">
  </p>
</div>


<details>
  <summary>Tabela de Conteúdos</summary>
  <ol>
    <li><a href="#sobre-o-projeto">Sobre o Projeto</a>
      <ul>
        <li><a href="#documentacao">Documentação</a></li>
        <li><a href="#principais-stakeholders">Principais Stakeholders</a></li>
      </ul>
    </li>
    <li><a href="#organizacao-e-estrutura">Organização e Estrutura</a></li>
    <li><a href="#configuracao-de-ambiente">Configuração de Ambiente</a></li>
    <li><a href="#convencao-de-commits">Convenção de Commits</a></li>
    <li><a href="#autor">Autor</a></li>
    <li><a href="#apendice-uv-sub-projects">Apêndice: UV Sub-projects</a></li>
  </ol>
</details>

---

## Sobre o Projeto

Este repositório reúne a análise exploratória de dados clínicos de pacientes de UTI coletados no estudo TCR.
O objetivo é documentar o perfil da amostra, gerar tabelas e gráficos de apoio e identificar fatores associados ao desfecho clínico padronizado.

### Objetivo do Estudo

- Descrever características demográficas e clínicas dos pacientes.
- Analisar associações entre intervenções clínicas e o desfecho (óbito / alta / transferência).
- Gerar artefatos visuais e tabelas que a equipe clínica possa consultar diretamente.

### Onde encontrar os resultados

- `reports/figures/` — gráficos exploratórios gerados.
- `reports/figures/README.md` — orientações para entender cada figura.
- `reports/descriptive/` — tabelas CSV com frequências e resumos descritivos.
- `reports/descriptive/README.md` — explicação de cada tabela.
- `reports/association_results.csv` — resultados brutos dos testes de associação.
- `reports/association_results.md` — interpretação dos testes estatísticos e do valor-p.
- `data/processed/tcr_patients_clean.parquet` — base de dados limpa usada nas análises.
- `notebooks/eda/01_descriptive_stats.ipynb` — geração de tabelas descritivas.
- `notebooks/eda/02_association_tests.ipynb` — execução de testes de associação.

### Autor

| Nome | Email |
|------|-------|
| **Rodrigo Watanabe Pisaia** | rodrigo.watanabe0107@gmail.com |

### Documentação

| Recurso | Link |
|---------|------|
| Confluence / Wiki | `<colar link aqui>` |
| Jira / Board | `<colar link aqui>` |
| GitLab Repo | `<colar link aqui>` |

### Principais Stakeholders
* **Nome** (Area/Cargo) - [email@exemplo.com]
* **Nome** (Area/Cargo) - [email@exemplo.com]

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## 📂 Organização e Estrutura

Este projeto segue uma estrutura padronizada para garantir reprodutibilidade.

> **Nota sobre Convenção de Nomes:**
> Arquivos numerados (ex: `01_load_data.py`) indicam **ordem de execução** em pipelines ou análises.
> Código reutilizável (funções/classes) deve residir em `src/` ou `utils/` e ser importado.

```text
.
├── config/                 # Configurações e variáveis de ambiente
│   ├── .env                # Variáveis de ambiente (NÃO commitar!)
│   └── .env.example        # Template com as variáveis necessárias
│
├── data/                   # Dados do projeto (Geralmente ignorados pelo Git)
│   ├── external/           # Dados de fontes terceiras
│   ├── interim/            # Dados transformados intermediários
│   ├── processed/          # Dados finais prontos para modelagem
│   └── raw/                # Dados originais imutáveis
│
├── notebooks/              # Jupyter Notebooks
│   ├── eda/                # Análise exploratória de dados
│   ├── get_data/           # Extração de dados (usa queries/)
│   ├── processing/         # Transformação e feature engineering
│   ├── training/           # Treinamento de modelos
│   ├── modeling/           # Experimentos e avaliação de modelos
│   └── qa/                 # Validação e quality assurance
│
├── queries/                # Queries SQL (.txt/.sql) para Databricks
│   └── get_data/           # Queries usadas por notebooks/get_data/
│
├── models/                 # Artefatos de modelos (ignorados pelo Git)
│
├── reports/                # Relatórios gerados, html, pdf
│   └── figures/            # Gráficos e imagens geradas pelos códigos
│
├── src/                    # Código Fonte Reutilizável (Library do projeto)
│   └── __init__.py         # Funções de engenharia de features
│
├── .cursorrules            # Regras para o Cursor AI
├── AGENT.md                # Guidelines para agentes AI
├── .gitignore              # Arquivos a serem ignorados pelo git
├── LICENSE                 # Licença do projeto
├── pyproject.toml          # Dependências e config (UV workspace)
└── README.md               # Documentação principal
```

## ✅ Resultados já desenvolvidos

O projeto já possui análises exploratórias e tabelas prontas para leitura:

- `reports/descriptive/` — tabelas CSV com frequências e resumos descritivos
- `reports/descriptive/README.md` — guia rápido para entender cada tabela
- `reports/association_results.csv` — resultados brutos de testes de associação
- `reports/association_results.md` — resumo interpretável dos testes χ²/Kruskal-Wallis
- `reports/figures/` — gráficos exploratórios gerados para visualização
- `reports/figures/README.md` — lista dos gráficos e como usar cada um
- `data/processed/tcr_patients_clean.parquet` — base limpa usada para análise
- `notebooks/eda/01_descriptive_stats.ipynb` — geração de tabelas descritivas
- `notebooks/eda/02_association_tests.ipynb` — execução de testes de associação

### Como navegar

1. Leia `reports/descriptive/README.md` para começar pelas tabelas.
2. Veja `reports/association_results.md` para os resultados dos testes de associação.
3. Abra as imagens em `reports/figures/` para visualização de padrões clínicos.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## ⚙️ Configuração de Ambiente

As variáveis de ambiente do projeto ficam em `config/.env`. Para configurar:

```bash
cp config/.env.example config/.env
```

Edite o arquivo `config/.env` com as credenciais necessárias:

| Variável | Descrição |
|----------|-----------|
| `DATABRICKS_TOKEN` | Token de acesso ao Databricks (DAPI) |
| `DATABRICKS_HOSTNAME` | Host do workspace Databricks |
| `DATABRICKS_HTTP_PATH` | HTTP Databricks Warehouse |

> **IMPORTANTE:** O arquivo `config/.env` está no `.gitignore` e **nunca** deve ser commitado. Use `config/.env.example` como referência.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## 📝 Convenção de Commits

Este projeto segue o padrão **Conventional Commits**. Todas as mensagens de commit devem seguir o formato:

```
<tipo>(<escopo opcional>): <descrição>
```

### Tipos permitidos

| Tipo | Descrição |
|------|-----------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Alterações na documentação |
| `style` | Formatação (sem alteração de lógica) |
| `refactor` | Refatoração de código |
| `perf` | Melhoria de performance |
| `test` | Adição ou correção de testes |
| `chore` | Tarefas de manutenção |
| `infra` | Mudanças de infraestrutura |
| `imp` | Melhorias gerais |
| `breaking` | Mudança com quebra de compatibilidade |


### Exemplos

```bash
git commit -m "feat: adiciona modelo de classificação"
git commit -m "fix(pipeline): corrige leitura de dados raw"
git commit -m "docs: atualiza README com instruções de deploy"
git commit -m "refactor(src): simplifica feature engineering"
```

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## 👤 Autor

| Nome | Email |
|------|-------|
| **Rodrigo Watanabe Pisaia** | rodrigo.watanabe0107@gmail.com |

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## 📦 Apêndice: UV Sub-projects

Este projeto usa **UV workspaces**, o que permite criar sub-projetos com dependências isoladas dentro do mesmo repositório. Isso é útil quando você precisa, por exemplo, carregar um modelo legado que depende de versões específicas de bibliotecas que conflitam com o projeto principal.

### Quando usar sub-projects?

- Modelo antigo que requer versões específicas (ex: `scikit-learn==0.24`, `xgboost==1.5`)
- Serviço auxiliar com stack diferente
- Experimentação isolada sem afetar o ambiente principal

### Como criar um sub-project

```bash
# Dentro da raiz do projeto, crie o sub-project
uv init models/modelo_legado_v1

# Entre no sub-project e adicione as dependências específicas
cd models/modelo_legado_v1
uv add scikit-learn==0.24.2 xgboost==1.5.0
```

A estrutura resultante fica assim:

```text
.
├── pyproject.toml                  # Projeto principal (workspace root)
├── models/
│   └── modelo_legado_v1/           # Sub-project com deps isoladas
│       ├── pyproject.toml          # Dependências do modelo legado
│       └── src/
│           └── ...
├── src/                            # Código do projeto principal
└── ...
```

### Executando código dentro de um sub-project

```bash
# Rodar um script com as dependências do sub-project
uv run --package modelo_legado_v1 python predict.py

# Ou entre no diretório do sub-project
cd models/modelo_legado_v1
uv run python predict.py
```

### Referência do workspace no pyproject.toml

O UV detecta automaticamente sub-projetos. Para configuração explícita, adicione no `pyproject.toml` raiz:

```toml
[tool.uv.workspace]
members = ["models/*"]
```

> **Dica:** Cada sub-project tem seu próprio `pyproject.toml` e `.venv`, garantindo isolamento total de dependências.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>
