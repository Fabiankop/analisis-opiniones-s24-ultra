"""
Sentiment analysis of comments extracted from X.
Classifies each comment as positive, neutral, or negative using a
pretrained Hugging Face Transformers model.
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from transformers import pipeline


# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# -----------------------------------------------------------------------------
DB_PATH = "s24_comments.db"
MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"


# -----------------------------------------------------------------------------
# 2. COMMENT LOADING
# -----------------------------------------------------------------------------
def load_comments(db_path):
    """Load comments from the SQLite database."""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT tweet_id, text FROM tweets", conn)
    conn.close()
    return df


# -----------------------------------------------------------------------------
# 3. SENTIMENT CLASSIFICATION
# -----------------------------------------------------------------------------
def map_label(label):
    """Map the model label (1 to 5 stars) to sentiment categories."""
    stars = int(label[0])
    if stars <= 2:
        return "negative"
    if stars == 3:
        return "neutral"
    return "positive"


def classify_comments(df, classifier):
    """Apply the model to each comment and store the result."""
    sentiments = []
    total = len(df)

    for i, text in enumerate(df["text"]):
        result = classifier(text[:512])[0]
        sentiment = map_label(result["label"])
        sentiments.append(sentiment)

        if (i + 1) % 100 == 0:
            print(f"  Processed: {i + 1}/{total}")

    df["sentiment"] = sentiments
    return df


# -----------------------------------------------------------------------------
# 4. CHARTS
# -----------------------------------------------------------------------------
def plot_sentiment_distribution(df, output_file="sentiment_distribution.png"):
    """Pie and bar charts showing sentiment distribution."""
    counts = df["sentiment"].value_counts()
    counts = counts.reindex(["positive", "neutral", "negative"])
    colors = ["#4CAF50", "#FFC107", "#F44336"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

    ax1.pie(counts, labels=counts.index, colors=colors,
            autopct="%1.1f%%", startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 2})
    ax1.set_title("Sentiment distribution")

    ax2.bar(counts.index, counts.values, color=colors, edgecolor="white")
    ax2.set_ylabel("Number of comments")
    ax2.set_title("Count by category")
    for i, v in enumerate(counts.values):
        ax2.text(i, v + 10, str(v), ha="center", fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Chart saved: {output_file}")


# -----------------------------------------------------------------------------
# 5. ANALYSIS BY ASPECT
# -----------------------------------------------------------------------------
def analyze_by_aspect(df):
    """Analyze sentiment by product aspect based on keyword matches."""
    aspects = ["camera", "battery", "screen", "price", "ai", "s pen"]

    rows = []
    for aspect in aspects:
        subset = df[df["text"].str.lower().str.contains(aspect, na=False)]
        if len(subset) == 0:
            continue
        percentages = subset["sentiment"].value_counts(normalize=True) * 100
        rows.append({
            "Aspect": aspect.title(),
            "Total": len(subset),
            "Positive": round(percentages.get("positive", 0), 1),
            "Neutral": round(percentages.get("neutral", 0), 1),
            "Negative": round(percentages.get("negative", 0), 1),
        })

    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# 6. MAIN PROGRAM
# -----------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("SENTIMENT ANALYSIS")
    print("=" * 70)

    print("\n[1/4] Loading comments from the database...")
    df = load_comments(DB_PATH)
    print(f"  Total comments: {len(df)}")

    print("\n[2/4] Loading sentiment model...")
    print("  (first run downloads ~700 MB; please wait)")
    classifier = pipeline("sentiment-analysis", model=MODEL_NAME)

    print("\n[3/4] Classifying comments...")
    df = classify_comments(df, classifier)

    df.to_csv("classified_comments.csv", index=False, encoding="utf-8")
    print("\n  Results saved: classified_comments.csv")

    print("\n[4/4] Generating charts and aspect analysis...")
    plot_sentiment_distribution(df)

    aspect_df = analyze_by_aspect(df)
    print("\n  Sentiment by aspect:")
    print(aspect_df.to_string(index=False))
    aspect_df.to_csv("sentiment_by_aspect.csv",
                     index=False, encoding="utf-8")

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    summary = df["sentiment"].value_counts(normalize=True) * 100
    for sentiment, pct in summary.items():
        print(f"  {sentiment.capitalize():10s}: {pct:5.1f}%")


if __name__ == "__main__":
    main()
