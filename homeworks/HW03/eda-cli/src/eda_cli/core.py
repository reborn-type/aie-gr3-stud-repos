from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd
from pandas.api import types as ptypes


@dataclass
class ColumnSummary:
    name: str
    dtype: str
    non_null: int
    missing: int
    missing_share: float
    not_unique_count: int
    unique_percent: float
    zeros: int
    zeros_shape: float
    unique: int
    example_values: List[Any]
    is_numeric: bool
    min: Optional[float] = None
    max: Optional[float] = None
    mean: Optional[float] = None
    std: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DatasetSummary:
    n_rows: int
    n_cols: int
    columns: List[ColumnSummary]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_rows": self.n_rows,
            "n_cols": self.n_cols,
            "columns": [c.to_dict() for c in self.columns],
        }


def summarize_dataset(
    df: pd.DataFrame,
    example_values_per_column: int = 3,
) -> DatasetSummary:
    """
    Полный обзор датасета по колонкам:
    - количество строк/столбцов;
    - типы;
    - пропуски;
    - количество уникальных;
    - несколько примерных значений;
    - базовые числовые статистики (для numeric).
    """
    n_rows, n_cols = df.shape
    columns: List[ColumnSummary] = []

    for name in df.columns:
        s = df[name]
        dtype_str = str(s.dtype)

        non_null = int(s.notna().sum())
        missing = n_rows - non_null
        missing_share = float(missing / n_rows) if n_rows > 0 else 0.0
        unique = int(s.nunique(dropna=True))
        
        not_unique_id_count = 0
        unique_id_percent = 1.0

        zeros = 0
        zeros_shape = 0.0

        if 'id' in name.lower(): 
            uniqie_val = len(df[name].unique())
            count_rows = len(df[name])
            if count_rows != uniqie_val:
                not_unique_id_count = count_rows - uniqie_val 
                unique_id_percent = uniqie_val / count_rows if count_rows > 0 else 0.0
        
        if ptypes.is_numeric_dtype(df[name]):
            zeros = (df[name] == 0).sum()
            zeros_shape = zeros / len(df[name])
        
        
        # Примерные значения выводим как строки
        examples = (
            s.dropna().astype(str).unique()[:example_values_per_column].tolist()
            if non_null > 0
            else []
        )

        is_numeric = bool(ptypes.is_numeric_dtype(s))
        min_val: Optional[float] = None
        max_val: Optional[float] = None
        mean_val: Optional[float] = None
        std_val: Optional[float] = None

        if is_numeric and non_null > 0:
            min_val = float(s.min())
            max_val = float(s.max())
            mean_val = float(s.mean())
            std_val = float(s.std())

        columns.append(
            ColumnSummary(
                name=name,
                dtype=dtype_str,
                non_null=non_null,
                missing=missing,
                missing_share=missing_share,
                not_unique_count=not_unique_id_count,
                unique_percent=unique_id_percent,
                zeros=zeros,
                zeros_shape=zeros_shape,
                unique=unique,
                example_values=examples,
                is_numeric=is_numeric,
                min=min_val,
                max=max_val,
                mean=mean_val,
                std=std_val,
            )
        )

    return DatasetSummary(n_rows=n_rows, n_cols=n_cols, columns=columns)

def zeros_table (df: pd.DataFrame) -> pd.DataFrame:
    """
    Таблица количества нулей по колонкам с числовыми типами данных.
    """
    
    numeric_df = df.select_dtypes(include='number')
    
    if numeric_df.empty:
        return pd.DataFrame(columns=["zeros_count", "zeros_share"])
    
    rows = [];
    
    
    for col in numeric_df.columns:
        zeros_per_column = (df[col] == 0).sum()
        zeros_share = zeros_per_column / len(df[col])
        rows.append({
            "column": col, 
            "zeros_count": zeros_per_column,
            "zeros_share": zeros_share
        })
    
    return pd.DataFrame(rows)

def is_unique_identificators (df: pd.DataFrame) -> pd.DataFrame:
    """
    Проверка уникальности идентификаторов.
    """
    
    rows = []; 
    
    if df.empty: 
        return pd.DataFrame(columns=["not_unique_count", "unique_percent"])
    
    for col in df.columns:
        if 'id' in col.lower(): 
            uniq = df[col].nunique(dropna=True)
            count_rows = len(df[col])
            rows.append({
                "column": col,
                "not_unique_count": count_rows - uniq,
                "unique_percent": uniq / count_rows if count_rows > 0 else 0.0,
            })
    
    return pd.DataFrame(rows)    
    
    
    

def missing_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Таблица пропусков по колонкам: count/share.
    """
    if df.empty:
        return pd.DataFrame(columns=["missing_count", "missing_share"])

    total = df.isna().sum()
    share = total / len(df)
    result = (
        pd.DataFrame(
            {
                "missing_count": total,
                "missing_share": share,
            }
        )
        .sort_values("missing_share", ascending=False)
    )
    return result



def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Корреляция Пирсона для числовых колонок.
    """
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        return pd.DataFrame()
    return numeric_df.corr(numeric_only=True)


def top_categories(
    df: pd.DataFrame,
    max_columns: int = 5,
    top_k: int = 5,
) -> Dict[str, pd.DataFrame]:
    """
    Для категориальных/строковых колонок считает top-k значений.
    Возвращает словарь: колонка -> DataFrame со столбцами value/count/share.
    """
    result: Dict[str, pd.DataFrame] = {}
    candidate_cols: List[str] = []

    for name in df.columns:
        s = df[name]
        if ptypes.is_object_dtype(s) or isinstance(s.dtype, pd.CategoricalDtype):
            candidate_cols.append(name)

    for name in candidate_cols[:max_columns]:
        s = df[name]
        vc = s.value_counts(dropna=True).head(top_k)
        if vc.empty:
            continue
        share = vc / vc.sum()
        table = pd.DataFrame(
            {
                "value": vc.index.astype(str),
                "count": vc.values,
                "share": share.values,
            }
        )
        result[name] = table

    return result


def compute_quality_flags(summary: DatasetSummary, missing_df: pd.DataFrame, unique_df: pd.DataFrame, zeros_df: pd.DataFrame, min_missing_share: float = 0.5) -> Dict[str, Any]:
    """
    Простейшие эвристики «качества» данных:
    - слишком много пропусков;
    - подозрительно мало строк;
    и т.п.
    """
    flags: Dict[str, Any] = {}
    flags["too_few_rows"] = summary.n_rows < 100
    flags["too_many_columns"] = summary.n_cols > 100

    max_missing_share = float(missing_df["missing_share"].max()) if not missing_df.empty else 0.0
    flags["max_missing_share"] = max_missing_share
    flags["too_many_missing"] = max_missing_share > min_missing_share 
    
    min_unique_id_percent = float(unique_df['unique_percent'].min()) if not unique_df.empty else 1.0; 
    flags['unique_id_percent'] = min_unique_id_percent
    flags['too_little_unique_id'] = min_unique_id_percent < 0.8

    mean_zeros_share = float(zeros_df['zeros_share'].mean()) if not zeros_df.empty else 0.0
    flags["mean_zeros_share"] = mean_zeros_share
    flags["too_many_zeros"] = mean_zeros_share >= 0.45
    
    # Простейший «скор» качества
    score = 1.0
    score -= max_missing_share  # чем больше пропусков, тем хуже
    if summary.n_rows < 100:
        score -= 0.2
    if summary.n_cols > 100:
        score -= 0.1
    if min_unique_id_percent < 0.8:
        score -= 0.1
    if mean_zeros_share >= 0.45: 
        score -= 0.3

    score = max(0.0, min(1.0, score))
    flags["quality_score"] = score

    return flags


def flatten_summary_for_print(summary: DatasetSummary) -> pd.DataFrame:
    """
    Превращает DatasetSummary в табличку для более удобного вывода.
    """
    rows: List[Dict[str, Any]] = []
    for col in summary.columns:
        rows.append(
            {
                "name": col.name,
                "dtype": col.dtype,
                "non_null": col.non_null,
                "missing": col.missing,
                "missing_share": col.missing_share,
                "not_unique_count": col.not_unique_count,
                "unique_percent": col.unique_percent,
                "zeros": col.zeros,
                "zeros_shape": col.zeros_shape,
                "unique": col.unique,
                "is_numeric": col.is_numeric,
                "min": col.min,
                "max": col.max,
                "mean": col.mean,
                "std": col.std,
            }
        )
    return pd.DataFrame(rows)