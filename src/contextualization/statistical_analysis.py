"""
Statistical analysis of the survey data about the Samsung Galaxy S24 Ultra.
Calculates mean, median, mode, and standard deviation for each aspect and
generates the related charts.
"""

import pandas as pd
import matplotlib.pyplot as plt


# -----------------------------------------------------------------------------
# 1. SURVEY DATA LOADING
# -----------------------------------------------------------------------------
def load_survey_data():
    """Load survey responses into a DataFrame."""
    data = {
        "Camera": [5,5,5,5,5,5,5,5,5,5,5,5,5,
                   4,4,4,4,4,4,4,4,4,4,4,
                   3,3,3,3, 2, 1],
        "Battery": [5,5,5,5,5,5,5,5,
                    4,4,4,4,4,4,4,4,4,4,
                    3,3,3,3,3,3,
                    2,2,2,2, 1,1],
        "Performance": [5,5,5,5,5,5,5,5,5,5,
                        4,4,4,4,4,4,4,4,4,4,4,4,
                        3,3,3,3,3, 2,2, 1],
        "Design": [5,5,5,5,5,5,5,5,5,5,5,5,5,
                   4,4,4,4,4,4,4,4,4,4,4,4,
                   3,3,3,3, 2],
        "Value for money": [5,5, 4,4,4,4,4,
                            3,3,3,3,3,3,3,3,3,
                            2,2,2,2,2,2,2,2,
                            1,1,1,1,1,1],
        "Software": [5,5,5,5,5,5,
                     4,4,4,4,4,4,4,4,4,4,4,4,4,
                     3,3,3,3,3,3,3,
                     2,2,2, 1],
    }
    return pd.DataFrame(data)


# -----------------------------------------------------------------------------
# 2. STATISTICS CALCULATION
# -----------------------------------------------------------------------------
def calculate_statistics(df):
    """Calculate core statistics for each aspect."""
    results = pd.DataFrame({
        "Mean": df.mean().round(2),
        "Median": df.median().astype(int),
        "Mode": df.mode().iloc[0].astype(int),
        "Std. dev.": df.std().round(2),
        "Variance": df.var().round(2),
        "Min": df.min(),
        "Max": df.max(),
    })
    return results


# -----------------------------------------------------------------------------
# 3. CHARTS
# -----------------------------------------------------------------------------
def plot_distribution(df, output_file="likert_distribution.png"):
    """Create a stacked bar chart of the response distribution."""
    counts = pd.DataFrame(
        {col: df[col].value_counts().reindex(range(1, 6), fill_value=0)
         for col in df.columns}
    ).T

    colors = ["#d32f2f", "#f57c00", "#fdd835", "#7cb342", "#388e3c"]
    labels = [
        "Strongly disagree",
        "Disagree",
        "Neutral",
        "Agree",
        "Strongly agree",
    ]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    counts.plot(kind="bar", stacked=True, ax=ax, color=colors,
                edgecolor="white")
    ax.set_ylabel("Number of respondents")
    ax.set_title("Likert response distribution by aspect")
    ax.legend(labels, loc="upper center",
              bbox_to_anchor=(0.5, -0.15), ncol=5, fontsize=9)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Chart saved: {output_file}")


def plot_averages(stats, output_file="averages.png"):
    """Create a bar chart with mean and median values."""
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(stats))
    width = 0.35

    ax.bar([i - width / 2 for i in x], stats["Mean"],
           width, label="Mean", color="#1f4e79")
    ax.bar([i + width / 2 for i in x], stats["Median"],
           width, label="Median", color="#2e75b6")
    ax.axhline(y=3, color="gray", linestyle="--",
               linewidth=0.8, label="Neutral point")

    ax.set_ylabel("Likert value (1-5)")
    ax.set_title("Mean and median by aspect")
    ax.set_xticks(x)
    ax.set_xticklabels(stats.index, rotation=0)
    ax.set_ylim(0, 5.5)
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Chart saved: {output_file}")


# -----------------------------------------------------------------------------
# 4. MAIN PROGRAM
# -----------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("SURVEY STATISTICAL ANALYSIS")
    print("=" * 70)

    print("\n[1/3] Loading survey data...")
    df = load_survey_data()
    print(f"  Respondents: {len(df)}")
    print(f"  Aspects:     {len(df.columns)}")

    print("\n[2/3] Calculating statistics...")
    stats = calculate_statistics(df)
    print("\n" + str(stats))

    stats.to_csv("survey_statistics.csv", encoding="utf-8")
    print("\n  Table saved: survey_statistics.csv")

    print("\n[3/3] Generating charts...")
    plot_distribution(df)
    plot_averages(stats)

    print("\n" + "=" * 70)
    print("AUTOMATED INTERPRETATION")
    print("=" * 70)
    best = stats["Mean"].idxmax()
    worst = stats["Mean"].idxmin()
    print(f"  Best-rated aspect: {best} (mean = {stats['Mean'][best]})")
    print(f"  Lowest-rated aspect: {worst} (mean = {stats['Mean'][worst]})")
    print(f"  Overall average: {stats['Mean'].mean():.2f}")


if __name__ == "__main__":
    main()
