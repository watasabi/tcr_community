# Relatórios de Análise Multivariada (Fase 2)

Este diretório contém os artefatos das três análises multivariadas:
clustering K-Prototypes, MCA + clustering hierárquico/k-means, e árvore
de decisão. Para a explicação completa em linguagem simples de cada
análise, veja `kprototypes_results.md`, `mca_hierarchical_results.md` e
`decision_tree_results.md` neste mesmo diretório — este README é só o
inventário dos arquivos.

## K-Prototypes (clustering misto)

- `cluster_kprototypes_cost_by_k.csv` — custo do modelo para k de 2 a 7
  (usado para escolher k pelo método do cotovelo).
- `cluster_kprototypes_assignments.csv` — cluster atribuído a cada
  paciente + desfecho, para auditoria/rastreabilidade.
- `cluster_kprototypes_profile.csv` — perfil de cada cluster (moda das
  categóricas, média das numéricas).
- `cluster_kprototypes_vs_outcome.csv` — cruzamento cluster × desfecho
  (contagens e percentuais).

## MCA + clustering hierárquico/k-means

- `mca_coordinates.csv` — coordenadas de cada paciente nas 5 dimensões
  MCA retidas.
- `mca_explained_inertia.csv` — % de variância explicada por dimensão.
- `cluster_hierarchical_assignments.csv` — cluster atribuído a cada
  paciente pelo clustering hierárquico sobre as coordenadas MCA.
- `cluster_kmeans_mca_assignments.csv` — cluster atribuído a cada
  paciente pelo k-means sobre as coordenadas MCA.

## Árvore de decisão

- `tree_feature_importance.csv` — importância de cada variável na
  árvore, ordenada da mais para a menos importante.
- `tree_metrics.csv` — tamanho do treino/teste e acurácias.
- `tree_classification_report.csv` — precisão, sensibilidade (recall)
  e F1-score por categoria de desfecho, calculados no conjunto de
  teste (holdout).
- `tree_rules.txt` — regras completas da árvore em texto.

## Como interpretar

- Colunas `cluster` são inteiros identificando o grupo (0, 1, 2, ...);
  não há ordem ou hierarquia entre eles.
- Colunas `pct_*` são proporções (0–1), não percentuais formatados.
- `patient_index` nos arquivos de coordenadas/atribuições corresponde
  ao índice do paciente em `data/processed/tcr_patients_clean.parquet`.
- Figuras correspondentes (curva de cotovelo, dispersão MCA,
  dendrograma, árvore) estão em `reports/figures/` — ver
  `reports/figures/README.md`.
