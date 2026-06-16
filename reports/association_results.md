# Associação entre variáveis clínicas e desfecho

Este relatório resume os testes de associação realizados entre preditores clínicos e o desfecho padronizado dos pacientes.

- Arquivo de origem: `reports/association_results.csv`
- Pacientes analisados: 205
- Variável alvo: `desfecho_padronizado`

## Sumário

As variáveis com associação estatisticamente significativa (p < 0.05) foram:

- `escala_apache_ii` — teste Kruskal-Wallis: p ≈ 1.48e-09
- `cuidados_paliativos` — teste χ²: p ≈ 7.47e-06
- `drogas_vasoativas` — teste χ²: p ≈ 0.0012

Outras variáveis avaliadas não mostraram associação significativa com o desfecho no conjunto atual de dados.

## Resultados dos testes

| Variável | Teste | Estatística | p-value | n |
|---|---|---|---|---|
| comorbidades | chi2 | 7.685155 | 0.103817 | 205 |
| ventilacao_mecanica | chi2 | 18.506856 | 0.101145 | 205 |
| drogas_vasoativas | chi2 | 18.020611 | 0.001223 | 205 |
| transfusao_sanguinea | chi2 | 4.624035 | 0.328092 | 205 |
| escala_apache_ii | kruskal | 47.061863 | 0.00000000148 | 205 |
| hemodialise | chi2 | 4.787500 | 0.309804 | 205 |
| procedimento_cirurgico | chi2 | 5.967610 | 0.201580 | 205 |
| cuidados_paliativos | chi2 | 29.096074 | 0.00000747 | 205 |

## Como usar este relatório

- Abra `reports/association_results.csv` para ver os dados brutos.
- Use os valores de `test` para saber se o cálculo foi feito com χ² ou com Kruskal-Wallis.
- Para análise visual, veja os gráficos em `reports/figures/` relacionados a desfecho e preditores clínicos.
