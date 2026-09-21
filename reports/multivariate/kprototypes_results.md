# Clustering K-Prototypes — perfis de pacientes

Esta análise agrupa pacientes que se parecem entre si, considerando ao
mesmo tempo variáveis categóricas (comorbidades, ventilação mecânica,
diagnóstico, etc.) e numéricas (APACHE II, tempo de UTI).

- Arquivos de origem: `reports/multivariate/cluster_kprototypes_*.csv`
- Pacientes analisados: 205 (nenhum paciente foi descartado por dado
  ausente nas variáveis usadas)
- k (número de clusters) escolhido: **4**

## O que é um cluster?

Um cluster é um grupo de pacientes parecidos entre si nas variáveis
usadas — comorbidades, ventilação mecânica, drogas vasoativas,
transfusão, hemodiálise, procedimento cirúrgico, cuidados paliativos,
diagnóstico principal, gênero, faixa etária, local de residência,
escala APACHE II e tempo de internação na UTI. O algoritmo K-Prototypes
foi escolhido porque lida bem com essa mistura de categorias (SIM/NÃO,
diagnóstico) e números (APACHE II, dias de UTI) ao mesmo tempo — a
maioria dos algoritmos de clustering só funciona com um tipo de dado
por vez.

## Como escolhemos k?

Testamos o algoritmo para várias quantidades de clusters (k de 2 a 7) e
observamos o "custo" (quão parecidos os pacientes dentro de cada
cluster ficam) em cada caso — veja
`cluster_kprototypes_cost_by_k.csv` e a figura
`reports/figures/cluster_kprototypes_elbow.png`. O custo cai bastante
até k=4 e depois passa a cair de forma mais lenta e gradual — esse
"cotovelo" da curva é o ponto em que aumentar o número de clusters
deixa de trazer ganho relevante, por isso escolhemos **k=4**.

## O que cada cluster representa clinicamente

| Cluster | n | Perfil dominante |
|---|---|---|
| 0 | 10 | AVC isquêmico, homens, faixa etária mais jovem (32), com ventilação mecânica, drogas vasoativas, transfusão e procedimento cirúrgico — **tempo de UTI muito longo** (55 dias em média) e APACHE II alto (32.6). |
| 1 | 77 | Septicemia, mulheres, faixa etária avançada (80), com ventilação mecânica e drogas vasoativas — APACHE II mais alto do grupo (35.5), tempo de UTI curto (5.6 dias). |
| 2 | 48 | Pneumonia não especificada, homens, faixa etária avançada (76), em cuidados paliativos — APACHE II 28.4, tempo de UTI intermediário (23.9 dias). |
| 3 | 70 | DPOC exacerbado, homens, faixa etária avançada (83) — APACHE II mais baixo do grupo (19.5), tempo de UTI curto (6.1 dias). |

Essas descrições usam a **moda** (categoria mais comum) para variáveis
categóricas e a **média** para variáveis numéricas dentro de cada
cluster — não significa que 100% dos pacientes do grupo tenham
exatamente esse perfil, apenas que é o padrão predominante.

## Clusters e desfecho

| Cluster | % óbito | % alta | % transferência |
|---|---|---|---|
| 0 | 90.0% | 10.0% | 0.0% |
| 1 | 94.8% | 1.3% | 2.6% |
| 2 | 93.8% | 2.1% | 4.2% |
| 3 | 55.7% | 25.7% | 15.7% |

O cluster 3 (DPOC exacerbado, APACHE II mais baixo) se destaca por ter
uma proporção de óbito bem menor que os demais — coerente com o menor
APACHE II médio do grupo. Isso é **descritivo, não causal**: mostra que
esses pacientes tendem a estar juntos em outras variáveis, não que uma
variável específica "causa" o desfecho.

## Como usar este relatório

- Veja `cluster_kprototypes_assignments.csv` para o cluster de cada
  paciente individualmente.
- Veja `cluster_kprototypes_profile.csv` para os números completos por
  cluster.
- Compare com `reports/association_results.md` (Fase 1) para ver quais
  variáveis já eram individualmente associadas ao desfecho.
- Consulte a figura `reports/figures/cluster_kprototypes_elbow.png`
  para a curva de custo usada na escolha de k.

## Gerar relatório HTML interativo

```bash
uv run python reports/generate_profile_report.py
```
