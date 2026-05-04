"""Análisis estadístico de la encuesta sobre el Samsung Galaxy S24 Ultra.

Lee las respuestas reales desde ``datos_encuesta.csv`` (escala Likert 1-5
para seis aspectos del producto) y calcula media, mediana, moda,
desviación típica y varianza por aspecto. Genera dos figuras:
distribución apilada por categoría Likert y comparación de
media/mediana.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "datos_encuesta.csv"
FIGURES_DIR = PROJECT_ROOT / "docs" / "figures"
TABLES_DIR = PROJECT_ROOT / "docs" / "tables"

ASPECT_COLUMNS = {
    "camara": "Cámara",
    "bateria": "Batería",
    "rendimiento": "Rendimiento",
    "diseno": "Diseño",
    "calidad_precio": "Calidad / precio",
    "software": "Software",
}


def load_survey_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve (subset Likert con columnas en español, dataframe completo)."""
    df = pd.read_csv(CSV_PATH)
    likert = df[list(ASPECT_COLUMNS.keys())].rename(columns=ASPECT_COLUMNS)
    return likert, df


def calculate_statistics(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "Media": df.mean().round(2),
        "Mediana": df.median().astype(int),
        "Moda": df.mode().iloc[0].astype(int),
        "Desv. típica": df.std().round(2),
        "Varianza": df.var().round(2),
        "Mín": df.min(),
        "Máx": df.max(),
    })


def plot_distribution(df: pd.DataFrame, output_file: Path) -> None:
    counts = pd.DataFrame(
        {col: df[col].value_counts().reindex(range(1, 6), fill_value=0)
         for col in df.columns}
    ).T

    colors = ["#d32f2f", "#f57c00", "#fdd835", "#7cb342", "#388e3c"]
    labels = [
        "Muy en desacuerdo (1)",
        "En desacuerdo (2)",
        "Neutral (3)",
        "De acuerdo (4)",
        "Muy de acuerdo (5)",
    ]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    counts.plot(kind="bar", stacked=True, ax=ax, color=colors,
                edgecolor="white")
    ax.set_ylabel("Número de respondientes")
    ax.set_title("Distribución de respuestas Likert por aspecto")
    ax.legend(labels, loc="upper center",
              bbox_to_anchor=(0.5, -0.15), ncol=5, fontsize=9)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Gráfico guardado: {output_file}")


def plot_averages(stats: pd.DataFrame, output_file: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(stats))
    width = 0.35

    ax.bar([i - width / 2 for i in x], stats["Media"],
           width, label="Media", color="#1f4e79")
    ax.bar([i + width / 2 for i in x], stats["Mediana"],
           width, label="Mediana", color="#2e75b6")
    ax.axhline(y=3, color="gray", linestyle="--",
               linewidth=0.8, label="Punto neutral")

    ax.set_ylabel("Valor Likert (1-5)")
    ax.set_title("Media y mediana por aspecto")
    ax.set_xticks(x)
    ax.set_xticklabels(stats.index, rotation=15, ha="right")
    ax.set_ylim(0, 5.5)
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Gráfico guardado: {output_file}")


def main() -> None:
    print("=" * 70)
    print("ANÁLISIS ESTADÍSTICO DE LA ENCUESTA")
    print("=" * 70)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    print("\n[1/3] Cargando datos de la encuesta...")
    likert, full = load_survey_data()
    print(f"  Respondientes: {len(likert)}")
    print(f"  Aspectos:      {len(likert.columns)}")
    print(f"  Demografía:    edad media = {full['edad'].mean():.1f} años, "
          f"género: {full['genero'].value_counts().to_dict()}")

    print("\n[2/3] Calculando estadísticas...")
    stats = calculate_statistics(likert)
    print("\n" + str(stats))

    out_csv = TABLES_DIR / "survey_statistics.csv"
    stats.to_csv(out_csv, encoding="utf-8")
    print(f"\n  Tabla guardada: {out_csv}")

    print("\n[3/3] Generando gráficos...")
    plot_distribution(likert, FIGURES_DIR / "likert_distribution.png")
    plot_averages(stats, FIGURES_DIR / "averages.png")

    print("\n" + "=" * 70)
    print("INTERPRETACIÓN AUTOMÁTICA")
    print("=" * 70)
    best = stats["Media"].idxmax()
    worst = stats["Media"].idxmin()
    print(f"  Aspecto mejor calificado: {best} (media = {stats['Media'][best]})")
    print(f"  Aspecto peor calificado:  {worst} (media = {stats['Media'][worst]})")
    print(f"  Promedio general:         {stats['Media'].mean():.2f}")


if __name__ == "__main__":
    main()
