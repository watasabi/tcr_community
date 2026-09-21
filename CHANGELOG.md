# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/), e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Added
- Setup inicial do projeto via template ds-template-v2.
- Fase 2: clustering K-Prototypes (categórico + numérico) com escolha de k
  por curva de custo/cotovelo, perfil de cluster e cruzamento cluster ×
  desfecho (`src/tcr_community/multivariate/kprototypes.py`,
  `reports/export_kprototypes.py`).
- Fase 2: Análise de Correspondência Múltipla (MCA) com clustering
  hierárquico e k-means sobre as coordenadas reduzidas, incluindo
  dispersão 2D e dendrograma
  (`src/tcr_community/multivariate/mca_hierarchical.py`,
  `reports/export_mca_hierarchical.py`).
- Fase 2: árvore de decisão interpretável (profundidade limitada) para o
  desfecho, com importância de variáveis e regras exportadas em texto
  (`src/tcr_community/multivariate/decision_tree.py`,
  `reports/export_decision_tree.py`).
- Relatórios `.md` em linguagem acessível para os três novos módulos de
  análise multivariada (`reports/multivariate/`), integrados ao gerador
  de relatório HTML (`reports/generate_profile_report.py`).
- Notebooks de demonstração em `notebooks/modeling/` para clustering
  K-Prototypes, MCA + hierárquico e árvore de decisão.

### Fixed
- Corrigido caminho hardcoded de `INTERIM_PATH`/`PROCESSED_PATH` em
  `pipeline/prepare_data.py`, que apontava para um diretório inexistente
  fora do repositório atual.