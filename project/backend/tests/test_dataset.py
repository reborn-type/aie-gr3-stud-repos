import pandas as pd
import pytest

from settings import get_path

RU_DATASET_PATH = get_path("dataset")
EN_DATASET_PATH = get_path("it_support_dataset")


def test_rus_ds_is_ready():
    df = pd.read_csv(RU_DATASET_PATH, sep=";")

    assert not df.empty
    assert {"ID", "text", "label"}.issubset(df.columns)
    assert df["text"].notna().all()
    assert df["label"].notna().all()
    assert df["label"].nunique() >= 2


def test_rus_ds_has_exampls_for_cls():
    df = pd.read_csv(RU_DATASET_PATH, sep=";")
    duplicate_ratio = df["text"].duplicated().mean()

    assert df["label"].value_counts().min() >= 50
    assert duplicate_ratio <= 0.10


def test_eng_ds_is_ready():
    if not EN_DATASET_PATH.exists():
        pytest.skip(f"Optional dataset is not available: {EN_DATASET_PATH}")

    df = pd.read_csv(EN_DATASET_PATH)

    assert not df.empty
    assert {"Body", "Department"}.issubset(df.columns)
    assert df["Department"].nunique() >= 7
    assert df["Body"].notna().sum() > 1000
