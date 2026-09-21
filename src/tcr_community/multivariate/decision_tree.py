"""Árvore de decisão interpretável para o desfecho."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text

from tcr_community.cleaning.standardize import simplify_for_association
from tcr_community.schemas.columns import (
    COL_APACHE_II,
    COL_DESFECHO_PADRONIZADO,
    TREE_PREDICTORS,
)

MIN_SAMPLES_FOR_STRATIFY = 2


@dataclass
class TreeFitResult:
    """Resultado do ajuste da árvore.

    Attributes:
        model: ``DecisionTreeClassifier`` ajustado.
        feature_names: Nomes das colunas de features (pós one-hot),
            na ordem usada pelo modelo.
        class_names: Rótulos de classe (categorias do desfecho).
        train_accuracy: Acurácia no conjunto de treino.
        test_accuracy: Acurácia no conjunto de teste (holdout).
        n_train: Tamanho do conjunto de treino.
        n_test: Tamanho do conjunto de teste.
        x_test: Features do conjunto de teste (holdout).
        y_test: Alvo do conjunto de teste (holdout).
    """

    model: DecisionTreeClassifier
    feature_names: list[str]
    class_names: list[str]
    train_accuracy: float
    test_accuracy: float
    n_train: int
    n_test: int
    x_test: pd.DataFrame
    y_test: pd.Series


def prepare_tree_features(
    df: pd.DataFrame,
    predictors: list[str] | None = None,
    target: str = COL_DESFECHO_PADRONIZADO,
) -> tuple[pd.DataFrame, pd.Series]:
    """Prepara X (one-hot em categóricas + numéricas) e y para a árvore.

    Args:
        df: Dataset limpo.
        predictors: Preditoras (default: ``TREE_PREDICTORS``).
        target: Coluna alvo.

    Returns:
        Tupla (X, y): X com dummies para categóricas e colunas
        numéricas já em float; y como série categórica sem valores
        ausentes. Linhas com y ausente são removidas antes do split.
    """
    cols = predictors or TREE_PREDICTORS
    cat_cols = [c for c in cols if c != COL_APACHE_II and c in df.columns]
    num_cols = [c for c in cols if c == COL_APACHE_II and c in df.columns]

    work = df[[*cat_cols, *num_cols, target]].copy()
    for col in cat_cols:
        work[col] = work[col].map(simplify_for_association)
    for col in num_cols:
        work[col] = pd.to_numeric(work[col], errors="coerce")

    work = work.dropna(subset=[target])
    y = work[target].astype(str)

    x_cat = pd.get_dummies(work[cat_cols], dummy_na=False)
    x_num = work[num_cols].fillna(work[num_cols].mean())
    x = pd.concat([x_cat, x_num], axis=1)

    return x, y


def fit_decision_tree(
    x: pd.DataFrame,
    y: pd.Series,
    *,
    max_depth: int = 4,
    test_size: float = 0.25,
    random_state: int = 42,
) -> TreeFitResult:
    """Ajusta árvore de decisão com holdout simples.

    Args:
        x: Features (saída de ``prepare_tree_features``).
        y: Alvo.
        max_depth: Profundidade máxima (interpretabilidade; n pequeno).
        test_size: Fração para o conjunto de teste.
        random_state: Semente.

    Returns:
        TreeFitResult com modelo, acurácias e metadados.

    Note:
        Usa split estratificado por padrão; se alguma classe do alvo
        tiver menos de 2 amostras (o que impede estratificação), cai
        para split aleatório simples.
    """
    min_class_count = y.value_counts().min()
    can_stratify = min_class_count >= MIN_SAMPLES_FOR_STRATIFY
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y if can_stratify else None,
    )

    model = DecisionTreeClassifier(
        max_depth=max_depth,
        random_state=random_state,
    )
    model.fit(x_train, y_train)

    return TreeFitResult(
        model=model,
        feature_names=list(x.columns),
        class_names=list(model.classes_),
        train_accuracy=float(model.score(x_train, y_train)),
        test_accuracy=float(model.score(x_test, y_test)),
        n_train=len(x_train),
        n_test=len(x_test),
        x_test=x_test,
        y_test=y_test,
    )


def feature_importance_table(result: TreeFitResult) -> pd.DataFrame:
    """Tabela de importância de features, ordenada decrescente.

    Args:
        result: Saída de ``fit_decision_tree``.

    Returns:
        DataFrame com colunas ``feature`` e ``importance``.
    """
    return (
        pd.DataFrame(
            {
                "feature": result.feature_names,
                "importance": result.model.feature_importances_,
            }
        )
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def classification_report_table(result: TreeFitResult) -> pd.DataFrame:
    """Precisão, sensibilidade e F1 por categoria no conjunto de teste.

    Args:
        result: Saída de ``fit_decision_tree``.

    Returns:
        DataFrame com colunas ``categoria``, ``precisao``,
        ``sensibilidade``, ``f1_score`` e ``n``, uma linha por
        categoria do alvo mais uma linha ``macro avg``. Categorias
        ausentes do conjunto de teste ficam com ``n=0`` e métricas
        ``0.0`` (não avaliáveis nesse holdout).
    """
    y_pred = result.model.predict(result.x_test)
    report = classification_report(
        result.y_test,
        y_pred,
        labels=result.class_names,
        output_dict=True,
        zero_division=0,
    )
    rows = []
    for category in result.class_names:
        metrics = report[category]
        rows.append(
            {
                "categoria": category,
                "precisao": metrics["precision"],
                "sensibilidade": metrics["recall"],
                "f1_score": metrics["f1-score"],
                "n": int(metrics["support"]),
            }
        )
    macro = report["macro avg"]
    rows.append(
        {
            "categoria": "macro avg",
            "precisao": macro["precision"],
            "sensibilidade": macro["recall"],
            "f1_score": macro["f1-score"],
            "n": int(macro["support"]),
        }
    )
    return pd.DataFrame(rows)


def tree_text_rules(result: TreeFitResult) -> str:
    """Regras da árvore em texto (sklearn.tree.export_text).

    Args:
        result: Saída de ``fit_decision_tree``.

    Returns:
        String com as regras legíveis da árvore.
    """
    return export_text(result.model, feature_names=result.feature_names)
