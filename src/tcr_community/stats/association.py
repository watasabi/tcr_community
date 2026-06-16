"""Testes de associação bi-variados."""

from dataclasses import dataclass

import pandas as pd
from scipy import stats

from tcr_community.cleaning.standardize import simplify_for_association
from tcr_community.schemas.columns import COL_DESFECHO_PADRONIZADO

FISHER_MIN_CELL = 5
MIN_GROUPS = 2


@dataclass
class AssociationResult:
    """Resultado de um teste de associação."""

    variable: str
    target: str
    test: str
    statistic: float
    p_value: float
    n: int
    note: str | None = None


def _crosstab_clean(
    df: pd.DataFrame,
    col_a: str,
    col_b: str,
) -> pd.DataFrame:
    """Crosstab sem valores nulos."""
    subset = df[[col_a, col_b]].dropna()
    return pd.crosstab(subset[col_a], subset[col_b])


def chi_square_or_fisher(
    df: pd.DataFrame,
    predictor: str,
    target: str = COL_DESFECHO_PADRONIZADO,
) -> AssociationResult:
    """Teste χ² ou Fisher para associação categórica × categórica.

    Usa Fisher quando alguma célula da tabela tem contagem < 5.

    Args:
        df: Dataset.
        predictor: Coluna preditora.
        target: Coluna alvo.

    Returns:
        AssociationResult com estatística e p-valor.
    """
    table = _crosstab_clean(df, predictor, target)
    n = int(table.values.sum())

    if table.shape == (0, 0) or n == 0:
        return AssociationResult(
            variable=predictor,
            target=target,
            test="none",
            statistic=0.0,
            p_value=1.0,
            n=0,
            note="sem dados",
        )

    use_fisher = table.shape == (MIN_GROUPS, MIN_GROUPS) and (
        table.values.min() < FISHER_MIN_CELL
    )
    if use_fisher:
        _, p_value = stats.fisher_exact(table.values)
        return AssociationResult(
            variable=predictor,
            target=target,
            test="fisher_exact",
            statistic=0.0,
            p_value=float(p_value),
            n=n,
            note="células < 5",
        )

    chi2, p_value, _, _ = stats.chi2_contingency(table.values)
    return AssociationResult(
        variable=predictor,
        target=target,
        test="chi2",
        statistic=float(chi2),
        p_value=float(p_value),
        n=n,
    )


def continuous_vs_categorical(
    df: pd.DataFrame,
    predictor: str,
    target: str = COL_DESFECHO_PADRONIZADO,
) -> AssociationResult:
    """Compara variável contínua entre grupos categóricos.

    Usa Mann-Whitney para 2 grupos; Kruskal-Wallis para 3+ grupos.

    Args:
        df: Dataset.
        predictor: Coluna numérica.
        target: Coluna categórica de grupos.

    Returns:
        AssociationResult.
    """
    subset = df[[predictor, target]].copy()
    subset[predictor] = pd.to_numeric(subset[predictor], errors="coerce")
    subset = subset.dropna()

    groups = [
        g[predictor].values for _, g in subset.groupby(target, observed=True)
    ]
    n = sum(len(g) for g in groups)

    if len(groups) < MIN_GROUPS:
        return AssociationResult(
            variable=predictor,
            target=target,
            test="none",
            statistic=0.0,
            p_value=1.0,
            n=n,
            note="grupos insuficientes",
        )

    if len(groups) == MIN_GROUPS:
        stat, p_value = stats.mannwhitneyu(
            groups[0], groups[1], alternative="two-sided"
        )
        test_name = "mannwhitneyu"
    else:
        stat, p_value = stats.kruskal(*groups)
        test_name = "kruskal"

    return AssociationResult(
        variable=predictor,
        target=target,
        test=test_name,
        statistic=float(stat),
        p_value=float(p_value),
        n=n,
    )


def run_association_battery(
    df: pd.DataFrame,
    predictors: list[str],
    target: str = COL_DESFECHO_PADRONIZADO,
    numeric_predictors: list[str] | None = None,
) -> pd.DataFrame:
    """Executa battery de testes de associação com o desfecho.

    Args:
        df: Dataset limpo.
        predictors: Colunas categóricas (ou tratadas como categóricas).
        target: Coluna alvo padronizada.
        numeric_predictors: Colunas para testes contínuos vs categórico.

    Returns:
        DataFrame com resultados de todos os testes.
    """
    work = df.copy()
    numeric_set = set(numeric_predictors or [])

    for col in predictors:
        if col not in numeric_set and col in work.columns:
            work[col] = work[col].map(simplify_for_association)

    results: list[AssociationResult] = []

    for col in predictors:
        if col not in work.columns:
            continue
        if col in numeric_set:
            results.append(continuous_vs_categorical(work, col, target))
        else:
            results.append(chi_square_or_fisher(work, col, target))

    return pd.DataFrame([r.__dict__ for r in results])
