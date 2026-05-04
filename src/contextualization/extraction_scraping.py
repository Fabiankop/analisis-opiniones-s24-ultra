"""
Automated extraction of comments about the Samsung Galaxy S24 Ultra
from X (formerly Twitter) using Tweepy.
"""

import os
import hashlib
import sqlite3
from datetime import datetime
import tweepy


# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# -----------------------------------------------------------------------------
BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN")
if not BEARER_TOKEN:
    raise ValueError(
        "Token not found. Set the X_BEARER_TOKEN environment variable."
    )

QUERY = (
    '("Galaxy S24 Ultra" OR #GalaxyS24Ultra OR #GalaxyAI) '
    'lang:es -is:retweet'
)

MAX_TWEETS = 1500
DB_PATH = "s24_comments.db"


# -----------------------------------------------------------------------------
# 2. DATABASE SETUP
# -----------------------------------------------------------------------------
def create_database(path):
    """Create the SQLite database with the required schema."""
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tweets (
            tweet_id    TEXT PRIMARY KEY,
            created_at  TEXT,
            text        TEXT,
            likes       INTEGER,
            retweets    INTEGER,
            user_hash   TEXT
        )
    """)
    conn.commit()
    return conn


# -----------------------------------------------------------------------------
# 3. USER ANONYMIZATION
# -----------------------------------------------------------------------------
def anonymize_user(user_id):
    """Convert the user ID to a SHA-256 hash for anonymization."""
    return hashlib.sha256(str(user_id).encode()).hexdigest()


# -----------------------------------------------------------------------------
# 4. TWEET EXTRACTION
# -----------------------------------------------------------------------------
def extract_tweets(client, conn):
    """Download tweets from the API and store them in the database."""
    cursor = conn.cursor()
    count = 0

    for tweet in tweepy.Paginator(
        client.search_recent_tweets,
        query=QUERY,
        tweet_fields=["created_at", "public_metrics", "author_id", "lang"],
        max_results=100
    ).flatten(limit=MAX_TWEETS):

        user_hash = anonymize_user(tweet.author_id)

        cursor.execute("""
            INSERT OR IGNORE INTO tweets
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(tweet.id),
            tweet.created_at.isoformat(),
            tweet.text,
            tweet.public_metrics["like_count"],
            tweet.public_metrics["retweet_count"],
            user_hash
        ))
        count += 1

        if count % 100 == 0:
            print(f"  Tweets collected: {count}")
            conn.commit()

    conn.commit()
    return count


# -----------------------------------------------------------------------------
# 5. MAIN PROGRAM
# -----------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("COMMENT EXTRACTION - SAMSUNG GALAXY S24 ULTRA")
    print("=" * 70)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print("[1/3] Connecting to X API...")
    client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

    print("[2/3] Preparing local database...")
    conn = create_database(DB_PATH)

    print("[3/3] Starting extraction...")
    total = extract_tweets(client, conn)

    print("\nExtraction complete.")
    print(f"  Total collected: {total} tweets")
    print(f"  Output file: {DB_PATH}")
    print(f"  End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    conn.close()


if __name__ == "__main__":
    main()
