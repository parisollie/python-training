# Laboratorio 14 — Ciencia de datos

Pipeline completo de Machine Learning con Pandas y scikit-learn:

1. Cargar y explorar datos con Pandas
2. Limpiar y feature engineering
3. Entrenar clasificador (RandomForest)
4. Evaluar con métricas
5. Serializar con joblib
6. Predecir con validación Pydantic

## Requisitos previos

- Python 3.12 (gestionado con Poetry)
- Poetry 2.5.1
- NumPy 2.5.4, Pandas 3.0.6, scikit-learn 1.9.1, joblib 1.6.0

## Estructura

lab_14_data_science/
├── README.md              ← este archivo
├── analysis.py            ← carga, explora y limpia datos
├── train.py               ← entrena y serializa el modelo
├── predict.py             ← carga el modelo y predice
├── data/
│   └── characters.csv     ← 100 personajes (dataset sintético)
├── models/                ← modelos entrenados (ignorados por git)
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_analysis.py   ← 9 tests
    └── test_model.py      ← 11 tests

## El problema

**Clasificación binaria**: predecir si un personaje estará **vivo** o **muerto** según sus características.

**Features:**
- `episodes_count`: cantidad de episodios
- `has_powers`: 0/1
- `is_human`: 0/1 (derivada)
- `is_famous`: 0/1 (episodes_count > 5)

**Target:** `is_alive` (0 = Dead, 1 = Alive)

**Datos:** 100 personajes, filtrados a 92 (Alive/Dead únicamente, se descartan 8 `unknown`).

## Ejecutar el pipeline completo

### Paso 1: Análisis exploratorio

    poetry run python 04_laboratorios/lab_14_data_science/analysis.py

Salida esperada:

    Cargados 100 personajes

    Resumen por status:
             count  avg_episodes  pct_with_powers
    status
    Alive       59          5.00             0.10
    Dead        33          1.27             0.36
    unknown      8          1.25             0.62

    Por especie:
    status   Alive  Dead  unknown
    species
    Alien        4    12        3
    Human       55    21        5

### Paso 2: Entrenar el modelo

    cd 04_laboratorios/lab_14_data_science
    poetry run python train.py
    cd ../..

Salida esperada:

    📂 Cargando datos...
       Total: 100 personajes
    🔧 Preparando dataset (Alive/Dead)...
       Muestras: 92 (Alive: 59, Dead: 33)
    ✂️  Train/test split (80/20)...
       Train: 73, Test: 19
    🌲 Entrenando RandomForest...
    📊 Evaluando...
       Accuracy: 78.95%

    💾 Guardando modelo...
       Guardado en: .../models/alive_classifier.joblib
    ✅ Entrenamiento completado

### Paso 3: Predecir nuevos casos

    cd 04_laboratorios/lab_14_data_science
    poetry run python predict.py
    cd ../..

Salida esperada:

    📂 Cargando modelo...
    ✅ Modelo cargado

    Predicciones:
      Rick Sanchez         -> Alive  (prob=99.20%)
      Alien raro           -> Dead   (prob=23.96%)
      Human secundario     -> Alive  (prob=68.74%)

## Cómo ejecutar los tests

    poetry run pytest 04_laboratorios/lab_14_data_science/tests/ -v

Salida esperada:

    20 passed in 1.07s

### Con cobertura

    poetry run pytest 04_laboratorios/lab_14_data_science/tests/ --cov=04_laboratorios/lab_14_data_science --cov-report=term-missing

### Archivos de tests

| Archivo | Qué cubre | Tests |
|---------|-----------|-------|
| test_analysis.py | load_data, explore, clean, summaries, add_features | 9 |
| test_model.py | prepare_dataset, train, evaluate, save/load, predict | 11 |

## Análisis de los datos

| Status | Count | Avg episodes | % con poderes |
|--------|-------|--------------|---------------|
| Alive | 59 | 5.00 | 10% |
| Dead | 33 | 1.27 | 36% |
| unknown | 8 | 1.25 | 62% |

**Patrón claro**: los personajes vivos tienden a aparecer más veces (5.00 vs 1.27). El modelo lo detecta y lo usa como feature principal.

## Modelo

### RandomForestClassifier

| Parámetro | Valor |
|-----------|-------|
| n_estimators | 100 |
| max_depth | 5 |
| random_state | 42 |

**¿Por qué RandomForest?**
- Robusto con pocas muestras (~92)
- No requiere normalización
- Expone `feature_importances_`
- Buen baseline para clasificación tabular

### Accuracy

**~79%** en test (19 muestras). Considerando que:
- Solo hay 4 features
- Dataset muy pequeño (92)
- Clasificación binaria

Es un resultado razonable para un modelo de práctica.

## Serialización con joblib

    import joblib

    # Guardar
    joblib.dump(model, "model.joblib")

    # Cargar
    model = joblib.load("model.joblib")

**¿Por qué joblib y no pickle?**
- Optimizado para arrays NumPy (que es lo que usa sklearn internamente)
- Más eficiente con objetos grandes
- API más simple

**Riesgo de seguridad:** `pickle`/`joblib` ejecutan código al deserializar. Nunca cargar modelos de fuentes no confiables.

## Validación de entrada con Pydantic

    from predict import CharacterFeatures, predict_one

    features = CharacterFeatures(
        episodes_count=51,
        has_powers=1,
        is_human=1,
        is_famous=1,
    )
    result = predict_one(model, features)
    # {"is_alive": True, "probability": 0.99, "label": "Alive"}

`CharacterFeatures` valida:
- `episodes_count >= 0`
- `has_powers`, `is_human`, `is_famous` en {0, 1}

## Notas de implementación

### Pandas: `df.copy()` para no mutar

    def clean(df):
        cleaned = df.copy()  # no modifica el original
        ...

Buenas prácticas: las funciones no deben mutar la entrada.

### Pivot tables

    df.pivot_table(
        index="species",
        columns="status",
        values="id",
        aggfunc="count",
        fill_value=0,
    )

Convierte datos largos en tablas cruzadas (útil para reportes).

### Feature engineering

    df["is_human"] = (df["species"] == "Human").astype(int)
    df["is_famous"] = (df["episodes_count"] > 5).astype(int)
    df["is_alive"] = (df["status"] == "Alive").astype(int)

Las features derivadas suelen mejorar el modelo y aportar interpretabilidad.

### mypy + stubs de terceros

`pandas-stubs` provee tipos para Pandas. Para `joblib` y `sklearn` (sin stubs oficiales), usamos override:

    [[tool.mypy.overrides]]
    module = ["joblib.*", "sklearn.*"]
    ignore_missing_imports = true

## Comandos rápidos (resumen)

    # Análisis
    poetry run python 04_laboratorios/lab_14_data_science/analysis.py

    # Entrenamiento
    cd 04_laboratorios/lab_14_data_science
    poetry run python train.py
    cd ../..

    # Predicción
    cd 04_laboratorios/lab_14_data_science
    poetry run python predict.py
    cd ../..

    # Tests
    poetry run pytest 04_laboratorios/lab_14_data_science/tests/ -v

    # Calidad
    poetry run ruff check 04_laboratorios/lab_14_data_science/
    poetry run mypy 04_laboratorios/lab_14_data_science/

## Estado

- [x] Estructura del laboratorio
- [x] NumPy, Pandas, scikit-learn, joblib instalados
- [x] Dataset sintético (100 personajes)
- [x] Análisis exploratorio con Pandas
- [x] Feature engineering
- [x] Entrenamiento (RandomForest)
- [x] Evaluación (accuracy ~79%)
- [x] Serialización con joblib
- [x] Predicción con validación Pydantic
- [x] 20 tests
- [x] ruff + mypy OK
- [x] Documentación completa

## Pendiente (más adelante)

- Endpoint FastAPI para servir el modelo
- Más features (origin, has_powers * episodes_count)
- Comparar con otros modelos (LogisticRegression, GradientBoosting)
- Cross-validation más robusta
- Guardar métricas en MLflow

## Clonar este laboratorio

    git clone https://github.com/parisollie/python-training.git
    cd python-training
    poetry install

    # Tests (no necesitan el modelo entrenado)
    poetry run pytest 04_laboratorios/lab_14_data_science/tests/ -v

    # Pipeline completo
    poetry run python 04_laboratorios/lab_14_data_science/analysis.py
    cd 04_laboratorios/lab_14_data_science
    poetry run python train.py
    poetry run python predict.py
    cd ../..

## Referencias

- NumPy docs: https://numpy.org/doc/
- Pandas docs: https://pandas.pydata.org/docs/
- scikit-learn docs: https://scikit-learn.org/
- joblib docs: https://joblib.readthedocs.io/
- pandas-stubs: https://pypi.org/project/pandas-stubs/
- Real Python — Pandas: https://realpython.com/pandas-python-explore-dataset/
- Kaggle Learn: https://www.kaggle.com/learn
