# notebooks/poc_exploration.py (now acts as our main pipeline script)
import sys
import os
import pandas as pd

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.reddit_scraper import fetch_reddit_mentions
from src.sentiment_analysis import add_sentiment_scores
from src.db_utils import save_data, load_data

# --- Configuration ---
BRANDS = ['NVIDIA', 'AMD']
SUBREDDITS = ['hardware', 'gaming', 'pcmasterrace', 'buildapc', 'intel']
POST_LIMIT = 200 # Fetch up to 200 of the LATEST posts per brand/subreddit

def run_update_pipeline():
    """
    Runs the full data update pipeline:
    1. Load existing data from the database.
    2. Fetch the latest posts from Reddit.
    3. Filter out posts that are already in the database.
    4. Perform sentiment analysis on the new posts only.
    5. Save the new posts to the database.
    """
    print("--- Starting Data Update Pipeline ---")
    
    # 1. Load existing data to get IDs we've already processed
    print("[Step 1/5] Loading existing data from database...")
    existing_df = load_data()
    existing_ids = set(existing_df['id']) if not existing_df.empty else set()
    print(f"Found {len(existing_ids)} existing records in the database.")

    # 2. Fetch latest mentions from Reddit
    print("\n[Step 2/5] Fetching latest Reddit mentions...")
    latest_df = fetch_reddit_mentions(BRANDS, SUBREDDITS, limit_per_subreddit=POST_LIMIT)
    if latest_df.empty:
        print("No new data fetched from Reddit. Exiting.")
        return

    # 3. Filter out posts we already have
    print("\n[Step 3/5] Filtering for new, unseen posts...")
    new_posts_df = latest_df[~latest_df['id'].isin(existing_ids)]
    
    if new_posts_df.empty:
        print("No new posts found since last update. Pipeline finished.")
        return
        
    print(f"Found {len(new_posts_df)} new posts to process.")

    # 4. Perform sentiment analysis on new posts
    print("\n[Step 4/5] Performing sentiment analysis on new data...")
    analyzed_df = add_sentiment_scores(new_posts_df.copy()) # Use .copy() to avoid SettingWithCopyWarning
    print("Sentiment analysis complete.")

    # 5. Save the new, analyzed data to the database
    print("\n[Step 5/5] Saving new data to the database...")
    save_data(analyzed_df)
    
    print("\n--- Pipeline finished successfully! ---")

if __name__ == '__main__':
    run_update_pipeline()