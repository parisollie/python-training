"""Tests para train.py y predict.py."""

from pathlib import Path

import pytest
from analysis import load_data
from predict import CharacterFeatures, load_model, predict_one
from train import evaluate, prepare_dataset, save_model, train_model

# ============================================
# prepare_dataset
# ============================================


def test_prepare_dataset_solo_alive_dead() -> None:
    """prepare_dataset filtra solo Alive/Dead."""
    df = load_data()
    x, y = prepare_dataset(df)

    # 100 total - 8 unknown = 92 muestras
    assert len(x) == 92
    # Target es binario
    assert set(y.unique()) == {0, 1}


def test_prepare_dataset_features() -> None:
    """prepare_dataset usa 4 features."""
    df = load_data()
    x, _ = prepare_dataset(df)
    assert list(x.columns) == ["episodes_count", "has_powers", "is_human", "is_famous"]


# ============================================
# train_model
# ============================================


def test_train_model() -> None:
    """Entrena un modelo con el dataset completo."""
    df = load_data()
    x, y = prepare_dataset(df)
    model = train_model(x, y)

    # El modelo debe poder predecir
    preds = model.predict(x.head(5))
    assert len(preds) == 5
    assert all(p in [0, 1] for p in preds)


def test_model_tiene_feature_importances() -> None:
    """RandomForest expone feature_importances_."""
    df = load_data()
    x, y = prepare_dataset(df)
    model = train_model(x, y)

    importances = model.feature_importances_
    assert len(importances) == 4
    assert sum(importances) == pytest.approx(1.0, abs=0.01)


# ============================================
# evaluate
# ============================================


def test_evaluate_accuracy() -> None:
    """evaluate devuelve accuracy entre 0 y 1."""
    df = load_data()
    x, y = prepare_dataset(df)
    model = train_model(x, y)

    metrics = evaluate(model, x, y)
    assert 0.0 <= float(metrics["accuracy"]) <= 1.0  # type: ignore[arg-type]
    assert "report" in metrics
    assert "confusion" in metrics


# ============================================
# save/load model
# ============================================


def test_save_load_model(tmp_path: Path) -> None:
    """save_model y load_model funcionan juntos."""
    df = load_data()
    x, y = prepare_dataset(df)
    model = train_model(x, y)

    path = tmp_path / "model.joblib"
    save_model(model, path)
    assert path.exists()

    loaded = load_model(path)
    # Ambos predicen igual
    preds_original = model.predict(x.head(3))
    preds_loaded = loaded.predict(x.head(3))  # type: ignore[attr-defined]
    assert list(preds_original) == list(preds_loaded)


# ============================================
# CharacterFeatures (Pydantic)
# ============================================


def test_character_features_validacion() -> None:
    """CharacterFeatures valida rangos."""
    # Valido
    CharacterFeatures(episodes_count=10, has_powers=1, is_human=1, is_famous=0)

    # has_powers debe ser 0 o 1
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CharacterFeatures(episodes_count=10, has_powers=2, is_human=1, is_famous=0)


# ============================================
# predict_one (con modelo entrenado)
# ============================================


@pytest.fixture
def trained_model() -> object:
    """Entrena un modelo para tests de prediccion."""
    df = load_data()
    x, y = prepare_dataset(df)
    return train_model(x, y)


def test_predict_rick(trained_model: object) -> None:
    """Rick (muchos episodios, famoso) -> Alive."""
    features = CharacterFeatures(episodes_count=51, has_powers=1, is_human=1, is_famous=1)
    result = predict_one(trained_model, features)
    assert result["is_alive"] is True
    assert result["label"] == "Alive"
    assert 0.0 <= float(result["probability"]) <= 1.0  # type: ignore[arg-type]


def test_predict_alien_raro(trained_model: object) -> None:
    """Alien raro (1 ep, no humano) -> Dead."""
    features = CharacterFeatures(episodes_count=1, has_powers=1, is_human=0, is_famous=0)
    result = predict_one(trained_model, features)
    assert result["label"] == "Dead"
    assert float(result["probability"]) < 0.5  # type: ignore[arg-type]


def test_predict_estructura(trained_model: object) -> None:
    """predict_one devuelve las claves esperadas."""
    features = CharacterFeatures(episodes_count=10, has_powers=1, is_human=1, is_famous=0)
    result = predict_one(trained_model, features)
    assert set(result.keys()) == {"is_alive", "probability", "label"}
