# Módulo 14 — Ciencia de datos

## Objetivos
- Manipular datos tabulares con Pandas y Polars
- Entrenar un modelo simple con scikit-learn
- Serializar el modelo e inferir

## Contenidos clave

### NumPy
- ndarray: array N-dimensional homogeneo
- Operaciones vectorizadas (sin loops)
- Broadcasting
- Indexado y slicing
- Cuando usar NumPy (numerico puro) vs Pandas (tablas)

### Pandas
- DataFrame y Series
- Lectura de CSV/JSON/Parquet
- Filtrado, agrupacion, agregacion
- Merge y join
- Manejo de valores nulos (NaN)
- GroupBy y pivot

### Polars
- Alternativa moderna y rapida a Pandas
- API lazy (diferida) con .lazy()/.collect()
- Multi-threading por defecto
- Sintaxis con expresiones

### scikit-learn
- Estructura: fit / predict / transform
- Train/test split
- Modelos clasicos: LinearRegression, RandomForest, LogisticRegression
- Metricas: accuracy, precision, recall, f1, MSE, R2
- Pipelines (preprocesamiento + modelo)

### Serializacion de modelos
- joblib (recomendado para sklearn)
- pickle (generico pero con riesgos)
- ONNX (interoperabilidad)
- Formatos: model.joblib, model.pkl

### Inferencia
- Cargar modelo serializado
- Predecir nuevos datos
- Validar entrada (Pydantic)
- Endpoint FastAPI para servir el modelo

## Laboratorio

Pipeline completo de ML:

1. Cargar dataset de personajes (CSV de Rick and Morty)
2. Limpiar y transformar con Pandas
3. Entrenar un clasificador (predecir si un personaje esta vivo)
4. Evaluar con metricas
5. Guardar con joblib
6. Cargar y hacer predicciones nuevas
7. Endpoint FastAPI para inferencia

## Conceptos clave

### ¿Por que PEP 20 importa aqui?
- "Explícito es mejor que implícito" -> nombrar columnas claramente
- "Simple es mejor que complejo" -> modelo simple antes que deep learning
- "Los errores nunca deben pasar silenciosamente" -> validar NaN y tipos

### Cuando usar cada herramienta

| Herramienta | Cuando usar |
|-------------|-------------|
| NumPy | Calculo numerico puro, matrices |
| Pandas | Analisis exploratorio, datos tabulares <1GB |
| Polars | Datos tabulares grandes, rendimiento |
| scikit-learn | ML clasico (no deep learning) |
| PyTorch/TensorFlow | Deep learning, GPU |

### Flujo tipico de ML

    1. Cargar datos
    2. Explorar (shape, tipos, nulos)
    3. Limpiar (nulos, outliers, tipos)
    4. Feature engineering (crear features utiles)
    5. Train/test split
    6. Entrenar modelo(s)
    7. Evaluar con metricas
    8. Serializar el mejor
    9. Servir en produccion (FastAPI)

### Ejemplo: Pandas basico

    import pandas as pd

    df = pd.read_csv("characters.csv")
    print(df.shape)              # (20, 5)
    print(df.head())             # primeras filas
    print(df["status"].value_counts())  # conteo por status

    # Filtrar
    vivos = df[df["status"] == "Alive"]

    # Agrupar
    por_especie = df.groupby("species")["id"].count()

### Ejemplo: train/test split

    from sklearn.model_selection import train_test_split

    X = df[["feature1", "feature2"]]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

### Ejemplo: entrenar RandomForest

    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")

### Ejemplo: guardar y cargar con joblib

    import joblib

    joblib.dump(model, "model.joblib")
    loaded = joblib.load("model.joblib")
    loaded.predict(X_new)

## Checklist
- [x] Crear estructura del laboratorio
- [x] Instalar numpy, pandas, scikit-learn, joblib
- [x] Cargar y limpiar datos con Pandas
- [x] Feature engineering
- [x] Entrenar modelo (clasificador)
- [x] Evaluar con metricas
- [x] Guardar con joblib
- [x] Cargar y predecir
- [x] Tests con pytest
- [x] Documentar en README del laboratorio
- [x] Commit del modulo

## Referencias
- NumPy docs: https://numpy.org/doc/
- Pandas docs: https://pandas.pydata.org/docs/
- Polars docs: https://docs.pola.rs/
- scikit-learn docs: https://scikit-learn.org/
- joblib docs: https://joblib.readthedocs.io/
- Real Python — Pandas: https://realpython.com/pandas-python-explore-dataset/
- Kaggle Learn: https://www.kaggle.com/learn
