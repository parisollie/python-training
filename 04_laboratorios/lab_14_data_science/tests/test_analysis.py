"""Tests para analysis.py."""

import pandas as pd
import pytest
from analysis import (
    add_features,
    clean,
    explore,
    load_data,
    summary_by_species,
    summary_by_status,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """DataFrame de prueba con 4 personajes."""
    return pd.DataFrame(
        [
            {
                "id": 1,
                "name": "Rick",
                "species": "Human",
                "origin": "Earth",
                "episodes_count": 51,
                "has_powers": 1,
                "status": "Alive",
            },
            {
                "id": 2,
                "name": "Morty",
                "species": "Human",
                "origin": "Earth",
                "episodes_count": 51,
                "has_powers": 0,
                "status": "Alive",
            },
            {
                "id": 3,
                "name": "Birdperson",
                "species": "Alien",
                "origin": "Bird World",
                "episodes_count": 8,
                "has_powers": 1,
                "status": "Dead",
            },
            {
                "id": 4,
                "name": "Unknown",
                "species": "Alien",
                "origin": "unknown",
                "episodes_count": 1,
                "has_powers": 0,
                "status": "unknown",
            },
        ]
    )


# ============================================
# load_data
# ============================================


def test_load_data() -> None:
    """load_data carga el CSV real del laboratorio."""
    df = load_data()
    assert len(df) == 100
    assert "name" in df.columns
    assert "status" in df.columns


def test_load_data_path_custom(tmp_path: pytest.TempPathFactory) -> None:
    """load_data acepta una ruta personalizada."""
    csv = tmp_path / "test.csv"  # type: ignore[operator]
    csv.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
    df = load_data(csv)
    assert len(df) == 2
    assert list(df.columns) == ["a", "b"]


# ============================================
# explore
# ============================================


def test_explore(sample_df: pd.DataFrame) -> None:
    """explore devuelve shape, columns y dtypes."""
    result = explore(sample_df)
    assert result["shape"] == (4, 7)
    assert "name" in result["columns"]  # type: ignore[operator]
    assert "id" in result["dtypes"]  # type: ignore[operator]
    assert "nulls" in result
    assert "describe" in result


# ============================================
# clean
# ============================================


def test_clean_normaliza_origin(sample_df: pd.DataFrame) -> None:
    """clean normaliza origin."""
    cleaned = clean(sample_df)
    assert cleaned["origin"].isnull().sum() == 0


def test_clean_no_modifica_original(sample_df: pd.DataFrame) -> None:
    """clean no modifica el DataFrame original."""
    original_shape = sample_df.shape
    _ = clean(sample_df)
    assert sample_df.shape == original_shape


def test_clean_tipos(sample_df: pd.DataFrame) -> None:
    """clean asegura tipos int."""
    cleaned = clean(sample_df)
    assert cleaned["episodes_count"].dtype == "int64"
    assert cleaned["has_powers"].dtype == "int64"


# ============================================
# summary_by_status
# ============================================


def test_summary_by_status(sample_df: pd.DataFrame) -> None:
    """summary_by_status agrupa correctamente."""
    summary = summary_by_status(sample_df)
    assert "Alive" in summary.index
    assert "Dead" in summary.index
    assert summary.loc["Alive", "count"] == 2
    assert summary.loc["Dead", "count"] == 1


# ============================================
# summary_by_species
# ============================================


def test_summary_by_species(sample_df: pd.DataFrame) -> None:
    """summary_by_species hace pivot correcto."""
    by_species = summary_by_species(sample_df)
    assert "Human" in by_species.index
    assert "Alien" in by_species.index
    assert by_species.loc["Human", "Alive"] == 2
    assert by_species.loc["Alien", "Dead"] == 1


# ============================================
# add_features
# ============================================


def test_add_features(sample_df: pd.DataFrame) -> None:
    """add_features agrega is_human, is_famous, is_alive."""
    df = add_features(sample_df)
    assert "is_human" in df.columns
    assert "is_famous" in df.columns
    assert "is_alive" in df.columns

    # Rick es humano, famoso y alive
    rick = df[df["name"] == "Rick"].iloc[0]
    assert rick["is_human"] == 1
    assert rick["is_famous"] == 1
    assert rick["is_alive"] == 1

    # Birdperson es alien, no famoso, dead
    bird = df[df["name"] == "Birdperson"].iloc[0]
    assert bird["is_human"] == 0
    assert bird["is_famous"] == 1  # 8 > 5
    assert bird["is_alive"] == 0


def test_add_features_no_modifica_original(sample_df: pd.DataFrame) -> None:
    """add_features devuelve copia."""
    original_cols = set(sample_df.columns)
    df = add_features(sample_df)
    assert set(sample_df.columns) == original_cols  # no modificado
    assert "is_human" in df.columns
