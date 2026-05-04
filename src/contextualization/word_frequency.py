"""
Word frequency analysis on extracted comments about the Samsung Galaxy S24
Ultra. Identifies the most mentioned terms.
"""

import re
import sqlite3
from collections import Counter

import pandas as pd
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords


# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# -----------------------------------------------------------------------------
DB_PATH = "s24_comments.db"
TOP_N = 12

try:
    stopwords.words("spanish")
except LookupError:
    nltk.download("stopwords", quiet=True)


# -----------------------------------------------------------------------------
# 2. STOPWORD LIST
# -----------------------------------------------------------------------------
def get_stopwords():
    """
    Build the list of words to ignore:
    - Standard NLTK Spanish stopwords
    - Product-specific words that dominate the analysis
    """
    sw = set(stopwords.words("spanish"))
    sw.update([
        "samsung", "galaxy", "s24", "ultra", "smartphone", "celular",
        "telefono", "tel\u00e9fono", "movil", "m\u00f3vil", "https", "http", "www",
        "rt", "the", "and", "for", "que", "los", "las", "una", "uno",
        "ser", "estar", "tener", "hacer",
    ])
    return sw


# -----------------------------------------------------------------------------
# 3. TEXT CLEANING AND TOKENIZATION
# -----------------------------------------------------------------------------
def clean_text(text):
    """Clean a comment and convert it into a list of words."""
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", "", text)
    text = re.sub(r"[@#]\w+", "", text)
    text = re.sub(r"[^a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1\u00fc\s]", " ", text)
    words = text.split()
    words = [w for w in words if len(w) >= 3]
    return words


def process_comments(texts, sw):
    """Process all comments and return the flattened list of words."""
    all_words = []
    for text in texts:
        words = clean_text(text)
        words = [w for w in words if w not in sw]
        all_words.extend(words)
    return all_words


# -----------------------------------------------------------------------------
# 4. FREQUENCY COUNT
# -----------------------------------------------------------------------------
def count_frequencies(words, top_n=12):
    """Count word frequencies and return the most common terms."""
    counter = Counter(words)
    top = counter.most_common(top_n)
    total = sum(counter.values())

    df = pd.DataFrame(top, columns=["Word", "Frequency"])
    df["Rank"] = df.index + 1
    df["% of total"] = (df["Frequency"] / total * 100).round(2)
    df = df[["Rank", "Word", "Frequency", "% of total"]]
    return df, total


# -----------------------------------------------------------------------------
# 5. CHART
# -----------------------------------------------------------------------------
def plot_frequencies(df, output_file="word_frequency.png"):
    """Create a horizontal bar chart of the most frequent words."""
    fig, ax = plt.subplots(figsize=(10, 5.5))

    words = df["Word"][::-1]
    freqs = df["Frequency"][::-1]

    colors = ["#1f4e79"] * len(words)
    for i in range(min(3, len(words))):
        colors[-(i + 1)] = "#2e75b6"

    ax.barh(words, freqs, color=colors, edgecolor="white")
    ax.set_xlabel("Frequency")
    ax.set_title(f"Top {len(df)} words in the comments")

    for i, freq in enumerate(freqs):
        ax.text(freq + 5, i, str(freq), va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Chart saved: {output_file}")


# -----------------------------------------------------------------------------
# 6. MAIN PROGRAM
# -----------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("WORD FREQUENCY ANALYSIS")
    print("=" * 70)

    print("\n[1/4] Loading comments...")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT text FROM tweets", conn)
    conn.close()
    print(f"  Total comments: {len(df)}")

    print("\n[2/4] Processing text (cleaning and stopword removal)...")
    sw = get_stopwords()
    words = process_comments(df["text"], sw)
    print(f"  Total words processed: {len(words):,}")
    print(f"  Unique vocabulary:     {len(set(words)):,}")

    print(f"\n[3/4] Calculating top {TOP_N} words...")
    result, _total = count_frequencies(words, TOP_N)
    print("\n" + result.to_string(index=False))

    result.to_csv("word_frequency.csv", index=False, encoding="utf-8")
    print("\n  Table saved: word_frequency.csv")

    print("\n[4/4] Generating chart...")
    plot_frequencies(result)

    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print(f"  Most mentioned word: '{result.iloc[0]['Word']}' "
          f"({result.iloc[0]['Frequency']} times)")
    print("  This indicates the topic users discuss the most.")


if __name__ == "__main__":
    main()
