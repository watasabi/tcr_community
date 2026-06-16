# Associação entre variáveis clínicas e desfecho

Este relatório explica de forma simples os testes usados para avaliar se certas características clínicas estão associadas ao desfecho dos pacientes.

- Arquivo de origem: `reports/association_results.csv`
- Pacientes analisados: 205
- Variável alvo: `desfecho_padronizado`

## O que testamos?

Cada linha da tabela representa uma variável clínica testada contra o desfecho do paciente.

- Para variáveis que são categorias (como `SIM`/`NAO`), usamos o teste de **χ² (qui-quadrado)**.
- Para a variável numérica `escala_apache_ii`, usamos o teste **Kruskal-Wallis**, que compara a distribuição dos valores entre os grupos de desfecho.

### Por que esses testes foram usados?

- `χ²` serve para entender se a proporção de pacientes com determinado resultado é diferente entre grupos. Por exemplo: a proporção de óbitos entre pacientes com e sem ventilação mecânica.
- `Kruskal-Wallis` serve para comparar valores numéricos quando não podemos assumir que os dados seguem uma distribuição normal. Aqui ele verifica se a pontuação APACHE II é diferente entre os desfechos.

## Como entender o valor-p

O valor-p (p-value) mostra a probabilidade de observarmos o resultado atual se não houvesse associação real entre a variável e o desfecho.

- Se o valor-p for menor que 0.05, dizemos que a associação é **estatisticamente significativa**.
- Isso significa que é pouco provável que a diferença observada seja apenas por acaso.
- Se o valor-p for maior ou igual a 0.05, não há evidência suficiente para afirmar que existe uma associação.

### Hipótese nula

Para todos os testes, a hipótese nula é que **não existe associação** entre a variável e o desfecho.

- Quando rejeitamos a hipótese nula, concluímos que existe uma associação estatística.
- Quando não rejeitamos, não encontramos evidência suficiente para dizer que há associação.

## Resultados principais

As variáveis com associação estatisticamente significativa com `desfecho_padronizado` foram:

- `escala_apache_ii` — teste Kruskal-Wallis: p ≈ 0.00000000148. Isso indica que a pontuação APACHE II diferiu entre os grupos de desfecho.
- `cuidados_paliativos` — teste χ²: p ≈ 0.00000747. Isso indica associação entre cuidados paliativos e o desfecho.
- `drogas_vasoativas` — teste χ²: p ≈ 0.001223. Isso indica associação entre uso de drogas vasoativas e o desfecho.

As outras variáveis avaliadas não apresentaram evidência suficiente para rejeitar a hipótese nula no conjunto atual de dados.

## Resultados dos testes

| Variável | Tipo de teste | O que ele compara | p-value | Associação? |
|---|---|---|---|---|
| comorbidades | χ² | presença/ausência vs desfecho | 0.103817 | não significativa |
| ventilacao_mecanica | χ² | SIM/NAO vs desfecho | 0.101145 | não significativa |
| drogas_vasoativas | χ² | SIM/NAO vs desfecho | 0.001223 | significativa |
| transfusao_sanguinea | χ² | SIM/NAO vs desfecho | 0.328092 | não significativa |
| escala_apache_ii | Kruskal-Wallis | valor da escala vs desfecho | 0.00000000148 | significativa |
| hemodialise | χ² | SIM/NAO vs desfecho | 0.309804 | não significativa |
| procedimento_cirurgico | χ² | SIM/NAO vs desfecho | 0.201580 | não significativa |
| cuidados_paliativos | χ² | SIM/NAO vs desfecho | 0.00000747 | significativa |

## Como usar este relatório

- Veja `reports/association_results.csv` para detalhes completos.
- Os testes significativos ajudam a identificar fatores clínicos que estão relacionados ao desfecho.
- Compare essas conclusões com os gráficos em `reports/figures/` para ver os padrões visuais.
