"""Análisis de sentimiento de los comentarios sobre el Samsung Galaxy S24 Ultra.

Carga los comentarios desde la base SQLite generada por el módulo de
extracción y los clasifica como positivos, neutrales o negativos
empleando el modelo multilingüe ``nlptown/bert-base-multilingual-uncased-sentiment``.
Adicionalmente realiza un análisis por aspecto del producto a partir
de palabras clave en español.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from transformers import pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "s24_comments.db"
FIGURES_DIR = PROJECT_ROOT / "docs" / "figures"
TABLES_DIR = PROJECT_ROOT / "docs" / "tables"

MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"

ASPECT_KEYWORDS = {
    "Cámara": ["cámara", "camara", "foto", "zoom", "lente", "selfie"],
    "Batería": ["batería", "bateria", "carga", "duración", "duracion"],
    "Rendimiento": ["rendimiento", "fluidez", "rápido", "rapido",
                    "lag", "snapdragon", "calor", "calienta"],
    "Pantalla": ["pantalla", "display", "amoled", "brillo"],
    "Diseño": ["diseño", "diseno", "titanio", "tamaño", "tamano",
               "peso", "premium"],
    "Precio": ["precio", "caro", "costo", "vale", "valor"],
    "Galaxy AI": ["galaxy ai", "ai", "ia ", "inteligencia artificial",
                  "circle to search"],
    "S Pen": ["s pen", "spen", "lápiz"],
    "Software": ["software", "one ui", "android", "actualización",
                 "actualizacion", "bloatware"],
}


def load_comments(db_path: Path) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT tweet_id, text FROM tweets", conn)
    conn.close()
    return df


def map_label(label: str) -> str:
    """Convierte la etiqueta del modelo (1-5 estrellas) a categorías."""
    stars = int(label[0])
    if stars <= 2:
        return "negativo"
    if stars == 3:
        return "neutral"
    return "positivo"


def classify_comments(df: pd.DataFrame, classifier) -> pd.DataFrame:
    sentiments = []
    total = len(df)
    for i, text in enumerate(df["text"]):
        result = classifier(text[:512])[0]
        sentiments.append(map_label(result["label"]))
        if (i + 1) % 25 == 0 or (i + 1) == total:
            print(f"  Procesados: {i + 1}/{total}")
    df = df.copy()
    df["sentimiento"] = sentiments
    return df


def plot_sentiment_distribution(df: pd.DataFrame, output_file: Path) -> None:
    counts = df["sentimiento"].value_counts()
    counts = counts.reindex(["positivo", "neutral", "negativo"], fill_value=0)
    colors = ["#4CAF50", "#FFC107", "#F44336"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

    ax1.pie(counts, labels=counts.index, colors=colors,
            autopct="%1.1f%%", startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 2})
    ax1.set_title("Distribución de sentimiento")

    ax2.bar(counts.index, counts.values, color=colors, edgecolor="white")
    ax2.set_ylabel("Número de comentarios")
    ax2.set_title("Conteo por categoría")
    for i, v in enumerate(counts.values):
        ax2.text(i, v + max(counts.values) * 0.02, str(v),
                 ha="center", fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Gráfico guardado: {output_file}")


def analyze_by_aspect(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    text_lower = df["text"].str.lower()
    for aspect, keywords in ASPECT_KEYWORDS.items():
        pattern = "|".join(keywords)
        subset = df[text_lower.str.contains(pattern, na=False, regex=True)]
        if subset.empty:
            continue
        pct = subset["sentimiento"].value_counts(normalize=True) * 100
        rows.append({
            "Aspecto": aspect,
            "Menciones": len(subset),
            "% positivo": round(pct.get("positivo", 0), 1),
            "% neutral": round(pct.get("neutral", 0), 1),
            "% negativo": round(pct.get("negativo", 0), 1),
        })
    return pd.DataFrame(rows)


def main() -> None:
    print("=" * 70)
    print("ANÁLISIS DE SENTIMIENTO")
    print("=" * 70)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    print("\n[1/4] Cargando comentarios desde la base de datos...")
    df = load_comments(DB_PATH)
    print(f"  Total de comentarios: {len(df)}")

    print("\n[2/4] Cargando modelo de sentimiento...")
    print("  (la primera ejecución descarga ~700 MB; espera unos minutos)")
    classifier = pipeline("sentiment-analysis", model=MODEL_NAME)

    print("\n[3/4] Clasificando comentarios...")
    df = classify_comments(df, classifier)

    out_csv = TABLES_DIR / "classified_comments.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"\n  Resultados guardados: {out_csv}")

    print("\n[4/4] Generando gráficos y análisis por aspecto...")
    plot_sentiment_distribution(df, FIGURES_DIR / "sentiment_distribution.png")

    aspect_df = analyze_by_aspect(df)
    print("\n  Sentimiento por aspecto:")
    print(aspect_df.to_string(index=False))
    aspect_df.to_csv(TABLES_DIR / "sentiment_by_aspect.csv",
                     index=False, encoding="utf-8")

    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    summary = df["sentimiento"].value_counts(normalize=True) * 100
    for sentiment, pct in summary.items():
        print(f"  {sentiment.capitalize():10s}: {pct:5.1f}%")


if __name__ == "__main__":
    main()
