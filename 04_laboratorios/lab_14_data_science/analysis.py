"""Analisis de datos con Pandas.

Demuestra:
- Carga de CSV con pd.read_csv
- Exploracion (shape, dtypes, describe)
- Limpieza (nulos, tipos)
- Filtrado y agrupacion
- Feature engineering
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
CSV_FILE = DATA_DIR / "characters.csv"


def load_data(path: Path | None = None) -> pd.DataFrame:
    """Carga el CSV de personajes.

    Args:
        path: Ruta opcional al CSV. Por defecto usa el del laboratorio.

    Returns:
        DataFrame con los datos cargados.
    """
    return pd.read_csv(path or CSV_FILE)


def explore(df: pd.DataFrame) -> dict[str, object]:
    """Resumen exploratorio del DataFrame.

    Args:
        df: DataFrame.

    Returns:
        Dict con shape, columnas, tipos, nulos y describe.
    """
    return {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "nulls": df.isnull().sum().to_dict(),
        "describe": df.describe().to_dict(),
    }


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia el DataFrame.

    - Elimina filas con status "unknown" (para el clasificador binario).
    - Normaliza la columna origin.
    - Convierte tipos si hace falta.

    Args:
        df: DataFrame crudo.

    Returns:
        DataFrame limpio (copia).
    """
    cleaned = df.copy()

    # Convertir origin "unknown" a categoria explicita
    cleaned["origin"] = cleaned["origin"].fillna("unknown")

    # Aseguramos tipos
    cleaned["episodes_count"] = cleaned["episodes_count"].astype(int)
    cleaned["has_powers"] = cleaned["has_powers"].astype(int)

    return cleaned


def summary_by_status(df: pd.DataFrame) -> pd.DataFrame:
    """Resumen agregado por status.

    Args:
        df: DataFrame.

    Returns:
        DataFrame con conteos y promedios por status.
    """
    return (
        df.groupby("status")
        .agg(
            count=("id", "count"),
            avg_episodes=("episodes_count", "mean"),
            pct_with_powers=("has_powers", "mean"),
        )
        .round(2)
    )


def summary_by_species(df: pd.DataFrame) -> pd.DataFrame:
    """Conteo de personajes por especie y status.

    Args:
        df: DataFrame.

    Returns:
        DataFrame pivot con conteos.
    """
    return df.pivot_table(
        index="species",
        columns="status",
        values="id",
        aggfunc="count",
        fill_value=0,
    )


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering: agrega columnas derivadas.

    Args:
        df: DataFrame.

    Returns:
        DataFrame con nuevas features.
    """
    df = df.copy()
    df["is_human"] = (df["species"] == "Human").astype(int)
    df["is_famous"] = (df["episodes_count"] > 5).astype(int)
    df["is_alive"] = (df["status"] == "Alive").astype(int)
    return df


if __name__ == "__main__":
    df = load_data()
    print(f"Cargados {len(df)} personajes\n")

    summary = summary_by_status(df)
    print("Resumen por status:")
    print(summary)
    print()

    by_species = summary_by_species(df)
    print("Por especie:")
    print(by_species)
    print()

    df_with_features = add_features(df)
    print("Features agregadas:")
    print(df_with_features[["name", "is_human", "is_famous", "is_alive"]].head(10))
