# MCA + clustering hierárquico e k-means

Esta análise reduz as várias variáveis categóricas dos pacientes a
poucos "eixos" numéricos (dimensões MCA), permitindo visualizar os
pacientes como pontos em um mapa e agrupá-los por proximidade.

- Arquivos de origem: `reports/multivariate/mca_*.csv`,
  `cluster_hierarchical_assignments.csv`,
  `cluster_kmeans_mca_assignments.csv`
- Pacientes analisados: 205
- Dimensões MCA retidas: 5 (o gráfico de dispersão usa as duas
  primeiras)
- Número de clusters (hierárquico e k-means): **4**, o mesmo usado na
  análise K-Prototypes, para permitir comparação entre os dois métodos

## O que é MCA?

MCA (Análise de Correspondência Múltipla) é uma técnica que pega várias
variáveis categóricas (comorbidades, diagnóstico, ventilação mecânica,
gênero, faixa etária, etc.) e resume os principais padrões de variação
entre os pacientes em poucos números — as "dimensões" MCA. É como tirar
uma "foto panorâmica" de todas as variáveis categóricas ao mesmo tempo,
em vez de olhar uma de cada vez.

Neste conjunto de dados, cada dimensão MCA explica uma fração pequena
da variação total (por exemplo, a dimensão 1 explica cerca de 1.8%) —
isso é esperado quando há muitas variáveis categóricas com muitas
categorias diferentes (ex.: dezenas de diagnósticos distintos), e não
indica um problema nos dados. Ainda assim, as primeiras dimensões
concentram os padrões mais fortes de variação entre os pacientes.

## Como ler o gráfico de dispersão (scatter)

Nas figuras `reports/figures/mca_scatter_by_desfecho.png` e
`mca_scatter_by_cluster.png`, cada ponto é um paciente. Os eixos
("Dimensão MCA 1" e "Dimensão MCA 2") **não têm unidade clínica** — não
representam APACHE II, idade ou qualquer variável isolada. O que
importa é a **proximidade**: pacientes próximos no gráfico têm perfis
categóricos parecidos; pacientes distantes são mais diferentes entre
si.

- `mca_scatter_by_desfecho.png` colore os pontos pelo desfecho clínico
  (óbito, alta, transferência, etc.) — permite ver se pacientes com o
  mesmo desfecho tendem a ficar próximos no mapa.
- `mca_scatter_by_cluster.png` colore pelos clusters do agrupamento
  hierárquico — permite ver a que grupo cada paciente foi atribuído.

## Como ler o dendrograma

A figura `reports/figures/mca_dendrogram.png` mostra uma árvore que vai
juntando pacientes (e depois grupos de pacientes) progressivamente, do
mais parecido para o menos parecido. A altura de cada "galho" indica a
distância (dissimilaridade) entre os grupos unidos — galhos mais baixos
unem pacientes muito parecidos; galhos mais altos unem grupos bem
diferentes. Para obter 4 clusters, "cortamos" a árvore horizontalmente
no ponto que separa os dados em 4 ramos principais — foi esse corte que
gerou os rótulos em `cluster_hierarchical_assignments.csv`.

## Interpretação dos clusters

Os clusters obtidos por este método (hierárquico e k-means sobre as
coordenadas MCA) são derivados de forma diferente dos clusters
K-Prototypes (que usam distância mista categórica+numérica
diretamente), mas tendem a capturar padrões parecidos, já que ambos
partem das mesmas variáveis clínicas de base. Recomendamos ler este
relatório em conjunto com `kprototypes_results.md`: se os agrupamentos
concordam nas linhas gerais (por exemplo, um grupo concentrando
diagnósticos de maior gravidade), isso reforça a confiança nos perfis
identificados; se divergem bastante, é um sinal de que a estrutura de
grupos nos dados é menos definida.

## Como usar este relatório

- Veja `mca_coordinates.csv` para as coordenadas de cada paciente.
- Veja `mca_explained_inertia.csv` para a variância explicada por
  dimensão.
- Veja `cluster_hierarchical_assignments.csv` e
  `cluster_kmeans_mca_assignments.csv` para o cluster de cada paciente
  em cada método.
- Compare com `kprototypes_results.md` para uma segunda perspectiva
  sobre os mesmos grupos de pacientes.

## Gerar relatório HTML interativo

```bash
uv run python reports/generate_profile_report.py
```
