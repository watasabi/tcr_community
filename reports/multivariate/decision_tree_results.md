# Árvore de decisão — preditores do desfecho

Esta análise usa uma árvore de decisão para identificar quais
características clínicas mais pesam na previsão do desfecho do
paciente, de forma que qualquer pessoa consiga seguir a lógica das
perguntas feitas pelo modelo.

- Arquivos de origem: `reports/multivariate/tree_*.csv`,
  `tree_rules.txt`
- Pacientes analisados: 205 (153 para treino, 52 para teste)
- Preditoras usadas: comorbidades, ventilação mecânica, drogas
  vasoativas, transfusão sanguínea, hemodiálise, procedimento
  cirúrgico, cuidados paliativos, escala APACHE II
- Profundidade máxima da árvore: 4
- Acurácia no treino: **90.8%** — Acurácia no teste (dados não vistos
  pelo modelo): **80.8%**

## O que é uma árvore de decisão?

É um conjunto de perguntas sim/não em sequência (ex.: "APACHE II é
menor ou igual a 17.5?", "paciente está em cuidados paliativos?") que
leva a uma previsão do desfecho. Cada pergunta ("nó" da árvore) foi
escolhida automaticamente pelo algoritmo por ser a que melhor separa os
pacientes entre os diferentes desfechos naquele ponto.

## Como ler a árvore

Na figura `reports/figures/tree_decision_tree.png` (e em texto em
`tree_rules.txt`):

- Cada caixa é um **nó**: mostra a pergunta feita, o `gini` (uma medida
  de quão "misturados" estão os desfechos ali — 0 = grupo totalmente
  homogêneo), `samples` (quantos pacientes de treino passaram por
  aquele nó), `value` (quantos pacientes de cada categoria de desfecho)
  e `class` (o desfecho mais comum ali).
- Seguindo as setas ("True"/"False") a partir do topo, chegamos a uma
  **folha** (caixa sem setas saindo dela) — essa é a previsão final
  para aquele caminho de respostas.
- A pergunta do topo (`escala_apache_ii <= 17.5`) é a mais importante:
  ela sozinha já separa bem pacientes com maior e menor risco de óbito.

## Principais preditores

| Preditor | Importância |
|---|---|
| escala_apache_ii | 52.8% |
| cuidados_paliativos = SIM | 22.4% |
| procedimento_cirurgico = SIM | 8.9% |
| cuidados_paliativos = NAO | 8.1% |
| comorbidades = SIM | 3.6% |
| drogas_vasoativas = SIM | 3.0% |
| ventilacao_mecanica = NAO | 1.2% |

"Importância" indica o quanto cada variável contribuiu para as
decisões da árvore — quanto maior, mais peso teve nas divisões dos
pacientes. As demais variáveis testadas (hemodiálise, transfusão
sanguínea, algumas categorias de ventilação mecânica) tiveram
importância zero nesta árvore, ou seja, não foram usadas em nenhuma
pergunta — não significa que sejam irrelevantes clinicamente, apenas
que, dado o que as outras variáveis já explicam, o algoritmo não
precisou delas para separar os grupos.

## Desempenho por categoria (conjunto de teste)

A acurácia geral (80.8%) esconde diferenças grandes entre categorias.
A tabela abaixo (`tree_classification_report.csv`) mostra, para cada
categoria de desfecho nos 52 pacientes de teste:

- **Precisão**: das vezes que o modelo previu essa categoria, quantas
  estavam certas.
- **Sensibilidade (recall)**: dos pacientes que realmente tiveram essa
  categoria, quantos o modelo acertou.
- **F1-score**: média entre precisão e sensibilidade (quanto mais
  perto de 1, melhor).

| Categoria | Precisão | Sensibilidade | F1-score | n no teste |
|---|---|---|---|---|
| ÓBITO | 0.88 | 0.95 | 0.92 | 40 |
| ALTA | 0.40 | 0.29 | 0.33 | 7 |
| TRANSFERÊNCIA | 0.50 | 0.40 | 0.44 | 5 |
| Média macro (não ponderada) | 0.36 | 0.33 | 0.34 | 52 |

O modelo prevê ÓBITO com boa confiança (precisão e sensibilidade acima
de 0.85), mas o desempenho cai bastante para ALTA e TRANSFERÊNCIA —
categorias com poucos pacientes tanto para o modelo aprender quanto
para ser avaliado. Nenhum paciente de teste tinha as categorias OUTRO
ou DESCONHECIDO, então essas não puderam ser avaliadas nesta rodada.

## Limitações

- **Tamanho da amostra**: com apenas 205 pacientes (52 no conjunto de
  teste), os resultados podem mudar se novos dados forem incluídos —
  os números de acurácia devem ser vistos como uma estimativa inicial,
  não uma medida definitiva.
- **Desbalanceamento de classes**: a maioria dos pacientes teve o
  desfecho ÓBITO (166 de 205, 81%); as demais categorias (ALTA,
  TRANSFERÊNCIA, OUTRO, DESCONHECIDO) têm poucos casos. Isso significa
  que o modelo tende a prever ÓBITO com mais confiança do que as
  categorias minoritárias (ver tabela acima), e a acurácia geral
  (80.8%) é puxada para cima pelo grande volume de casos de óbito —
  previsões de ALTA/TRANSFERÊNCIA devem ser lidas com cautela.
- **Correlacional, não causal**: a árvore mostra quais variáveis, em
  conjunto, ajudam a prever o desfecho nos dados observados — não prova
  que uma variável "causa" o desfecho.
- **Profundidade limitada de propósito**: escolhemos profundidade
  máxima 4 para manter a árvore interpretável por um público não
  técnico, o que pode sacrificar um pouco de acurácia em troca de
  clareza — não fizemos ajuste fino (tuning) do modelo, o que seria um
  nível de rigor desproporcional para uma amostra deste tamanho.

## Como usar este relatório

- Veja `tree_feature_importance.csv` para a tabela completa de
  importâncias.
- Veja `tree_metrics.csv` para acurácias e tamanhos de treino/teste.
- Veja `tree_classification_report.csv` para precisão, sensibilidade e
  F1-score por categoria.
- Veja `tree_rules.txt` para as regras completas da árvore em texto.
- Veja a figura `reports/figures/tree_decision_tree.png` para a árvore
  completa.

## Gerar relatório HTML interativo

```bash
uv run python reports/generate_profile_report.py
```
