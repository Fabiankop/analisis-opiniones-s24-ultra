"""Análisis de frecuencia de palabras en los comentarios sobre el
Samsung Galaxy S24 Ultra.

Lee los comentarios de la base SQLite, normaliza el texto, descarta
stopwords y términos genéricos del producto, y reporta los términos
más mencionados con un gráfico de barras horizontales.
"""

from __future__ import annotations

import re
import sqlite3
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import nltk
import pandas as pd
from nltk.corpus import stopwords

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "s24_comments.db"
FIGURES_DIR = PROJECT_ROOT / "docs" / "figures"
TABLES_DIR = PROJECT_ROOT / "docs" / "tables"

TOP_N = 12

try:
    stopwords.words("spanish")
except LookupError:
    nltk.download("stopwords", quiet=True)


def get_stopwords() -> set[str]:
    sw = set(stopwords.words("spanish"))
    sw.update([
        "samsung", "galaxy", "s24", "ultra", "smartphone", "celular",
        "teléfono", "telefono", "móvil", "movil", "https", "http", "www",
        "rt", "que", "los", "las", "una", "uno",
        "ser", "estar", "tener", "hacer", "más", "mas",
    ])
    return sw


def clean_text(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", "", text)
    text = re.sub(r"[@#]\w+", "", text)
    text = re.sub(r"[^a-záéíóúñü\s]", " ", text)
    words = text.split()
    return [w for w in words if len(w) >= 3]


def process_comments(texts, sw: set[str]) -> list[str]:
    all_words: list[str] = []
    for text in texts:
        words = clean_text(text)
        all_words.extend(w for w in words if w not in sw)
    return all_words


def count_frequencies(words: list[str], top_n: int = 12) -> tuple[pd.DataFrame, int]:
    counter = Counter(words)
    top = counter.most_common(top_n)
    total = sum(counter.values())

    df = pd.DataFrame(top, columns=["Palabra", "Frecuencia"])
    df["Posición"] = df.index + 1
    df["% del total"] = (df["Frecuencia"] / total * 100).round(2)
    df = df[["Posición", "Palabra", "Frecuencia", "% del total"]]
    return df, total


def plot_frequencies(df: pd.DataFrame, output_file: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))

    words = df["Palabra"][::-1]
    freqs = df["Frecuencia"][::-1]

    colors = ["#1f4e79"] * len(words)
    for i in range(min(3, len(words))):
        colors[-(i + 1)] = "#2e75b6"

    ax.barh(words, freqs, color=colors, edgecolor="white")
    ax.set_xlabel("Frecuencia")
    ax.set_title(f"Top {len(df)} palabras en los comentarios")

    for i, freq in enumerate(freqs):
        ax.text(freq + max(freqs) * 0.01, i, str(freq),
                va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Gráfico guardado: {output_file}")


def main() -> None:
    print("=" * 70)
    print("ANÁLISIS DE FRECUENCIA DE PALABRAS")
    print("=" * 70)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    print("\n[1/4] Cargando comentarios...")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT text FROM tweets", conn)
    conn.close()
    print(f"  Total de comentarios: {len(df)}")

    print("\n[2/4] Procesando texto (limpieza y stopwords)...")
    sw = get_stopwords()
    words = process_comments(df["text"], sw)
    print(f"  Palabras procesadas: {len(words):,}")
    print(f"  Vocabulario único:   {len(set(words)):,}")

    print(f"\n[3/4] Calculando top {TOP_N} palabras...")
    result, _total = count_frequencies(words, TOP_N)
    print("\n" + result.to_string(index=False))

    out_csv = TABLES_DIR / "word_frequency.csv"
    result.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"\n  Tabla guardada: {out_csv}")

    print("\n[4/4] Generando gráfico...")
    plot_frequencies(result, FIGURES_DIR / "word_frequency.png")

    print("\n" + "=" * 70)
    print("INTERPRETACIÓN")
    print("=" * 70)
    print(f"  Palabra más mencionada: '{result.iloc[0]['Palabra']}' "
          f"({result.iloc[0]['Frecuencia']} veces)")
    print("  Esto refleja el tópico más recurrente en la conversación.")


if __name__ == "__main__":
    main()
