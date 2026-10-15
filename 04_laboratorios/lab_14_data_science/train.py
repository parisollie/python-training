"""Entrenamiento de un clasificador con scikit-learn.

Pipeline:
1. Cargar datos con Pandas
2. Filtrar solo Alive/Dead (clasificacion binaria)
3. Feature engineering
4. Train/test split
5. Entrenar RandomForest
6. Evaluar con metricas
7. Guardar con joblib
"""

from pathlib import Path

import joblib
import pandas as pd
from analysis import add_features, load_data
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
MODEL_FILE = MODELS_DIR / "alive_classifier.joblib"


def prepare_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Prepara X (features) e y (target) para clasificacion binaria.

    Solo usa filas con status Alive/Dead.

    Args:
        df: DataFrame crudo.

    Returns:
        Tupla (X, y).
    """
    # Filtrar solo Alive/Dead
    binary_df = df[df["status"].isin(["Alive", "Dead"])].copy()

    # Agregar features
    binary_df = add_features(binary_df)

    # Features para el modelo
    feature_cols = ["episodes_count", "has_powers", "is_human", "is_famous"]
    x = binary_df[feature_cols]
    y = binary_df["is_alive"]

    return x, y


def train_model(x: pd.DataFrame, y: pd.Series) -> RandomForestClassifier:
    """Entrena un RandomForestClassifier.

    Args:
        x: Features.
        y: Target.

    Returns:
        Modelo entrenado.
    """
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
    )
    model.fit(x, y)
    return model


def evaluate(
    model: RandomForestClassifier,
    x_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict[str, object]:
    """Evalua el modelo y devuelve metricas.

    Args:
        model: Modelo entrenado.
        x_test: Features de test.
        y_test: Target de test.

    Returns:
        Dict con accuracy, report, confusion.
    """
    y_pred = model.predict(x_test)
    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "report": classification_report(y_test, y_pred, output_dict=True),
        "confusion": confusion_matrix(y_test, y_pred).tolist(),
    }


def save_model(model: RandomForestClassifier, path: Path | None = None) -> Path:
    """Serializa el modelo con joblib.

    Args:
        model: Modelo a guardar.
        path: Ruta de salida.

    Returns:
        Ruta donde se guardo.
    """
    output = path or MODEL_FILE
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output)
    return output


def load_model(path: Path | None = None) -> RandomForestClassifier:
    """Carga un modelo serializado.

    Args:
        path: Ruta del modelo.

    Returns:
        Modelo cargado.
    """
    return joblib.load(path or MODEL_FILE)


def main() -> None:
    """Pipeline completo de entrenamiento."""
    print("📂 Cargando datos...")
    df = load_data()
    print(f"   Total: {len(df)} personajes")

    print("🔧 Preparando dataset (Alive/Dead)...")
    x, y = prepare_dataset(df)
    print(f"   Muestras: {len(x)} (Alive: {y.sum()}, Dead: {len(y) - y.sum()})")

    print("✂️  Train/test split (80/20)...")
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Train: {len(x_train)}, Test: {len(x_test)}")

    print("🌲 Entrenando RandomForest...")
    model = train_model(x_train, y_train)

    print("📊 Evaluando...")
    metrics = evaluate(model, x_test, y_test)
    print(f"   Accuracy: {metrics['accuracy']:.2%}")
    print()

    print("💾 Guardando modelo...")
    path = save_model(model)
    print(f"   Guardado en: {path}")

    print("✅ Entrenamiento completado")


if __name__ == "__main__":
    main()
