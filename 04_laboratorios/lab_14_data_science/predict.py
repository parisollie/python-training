"""Prediccion con el modelo entrenado.

Demuestra:
- Cargar modelo con joblib
- Validar entrada con Pydantic
- Predecir con el modelo
"""

from pathlib import Path

import joblib
import pandas as pd
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).parent
MODEL_FILE = BASE_DIR / "models" / "alive_classifier.joblib"


class CharacterFeatures(BaseModel):
    """Features de entrada para la prediccion."""

    episodes_count: int = Field(ge=0, description="Cantidad de episodios")
    has_powers: int = Field(ge=0, le=1, description="0 o 1")
    is_human: int = Field(ge=0, le=1, description="0 o 1")
    is_famous: int = Field(ge=0, le=1, description="0 o 1")


def load_model(path: Path | None = None) -> object:
    """Carga el modelo serializado.

    Args:
        path: Ruta del modelo.

    Returns:
        Modelo cargado.
    """
    return joblib.load(path or MODEL_FILE)


def predict_one(
    model: object,
    features: CharacterFeatures,
) -> dict[str, object]:
    """Predice si un personaje esta vivo.

    Args:
        model: Modelo entrenado.
        features: Features validadas.

    Returns:
        Dict con is_alive (bool), probability (float), label (str).
    """
    x = pd.DataFrame([features.model_dump()])
    prediction = model.predict(x)[0]  # type: ignore[attr-defined]
    probability = model.predict_proba(x)[0]  # type: ignore[attr-defined]

    return {
        "is_alive": bool(prediction),
        "probability": float(probability[1]),
        "label": "Alive" if prediction else "Dead",
    }


if __name__ == "__main__":
    print("📂 Cargando modelo...")
    model = load_model()
    print("✅ Modelo cargado\n")

    # Ejemplos
    ejemplos = [
        CharacterFeatures(episodes_count=51, has_powers=1, is_human=1, is_famous=1),
        CharacterFeatures(episodes_count=1, has_powers=1, is_human=0, is_famous=0),
        CharacterFeatures(episodes_count=1, has_powers=0, is_human=1, is_famous=0),
    ]
    nombres = ["Rick Sanchez", "Alien raro", "Human secundario"]

    print("Predicciones:")
    for nombre, features in zip(nombres, ejemplos, strict=True):
        result = predict_one(model, features)
        print(f"  {nombre:<20} -> {result['label']:<6} " f"(prob={result['probability']:.2%})")
