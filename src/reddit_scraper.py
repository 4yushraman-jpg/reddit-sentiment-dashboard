# src/reddit_scraper.py
import os
import praw
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

def get_reddit_instance():
    """Initializes and returns a PRAW Reddit instance."""
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
    )

def fetch_reddit_mentions(brands, subreddits, limit_per_subreddit=100):
    """
    Fetches posts mentioning specific brands from a list of subreddits.

    Args:
        brands (list): A list of brand names to search for.
        subreddits (list): A list of subreddit names to search in.
        limit_per_subreddit (int): Max number of posts to fetch from each subreddit.

    Returns:
        pandas.DataFrame: A DataFrame containing the fetched data.
    """
    reddit = get_reddit_instance()
    all_posts_data = []

    print(f"Searching for mentions of {', '.join(brands)} in subreddits: {', '.join(subreddits)}...")

    # Use tqdm for a progress bar
    with tqdm(total=len(subreddits) * len(brands)) as pbar:
        for sub_name in subreddits:
            subreddit = reddit.subreddit(sub_name)
            for brand in brands:
                pbar.set_description(f"Processing r/{sub_name} for '{brand}'")
                try:
                    # Search for the brand name in the subreddit
                    search_results = subreddit.search(query=brand, limit=limit_per_subreddit, sort='new')
                    for post in search_results:
                        all_posts_data.append({
                            'id': post.id,
                            'brand': brand,
                            'text': post.title + " " + post.selftext,
                            'subreddit': sub_name,
                            'author': str(post.author),
                            'created_utc': post.created_utc,
                            'sentiment_score': 0.0, # Placeholder
                            'sentiment_label': 'Neutral', # Placeholder
                            'url': f"https://reddit.com{post.permalink}"
                        })
                except Exception as e:
                    print(f"Could not fetch from r/{sub_name}. Error: {e}")
                
                pbar.update(1)

    return pd.DataFrame(all_posts_data)

if __name__ == '__main__':
    # Example usage when running the script directly
    target_brands = ['NVIDIA', 'AMD']
    target_subreddits = ['hardware', 'gaming', 'pcmasterrace', 'buildapc']
    
    df_mentions = fetch_reddit_mentions(target_brands, target_subreddits, limit_per_subreddit=50)
    
    if not df_mentions.empty:
        print(f"\nSuccessfully fetched {len(df_mentions)} posts.")
        print(df_mentions.head())
        # Example of saving to a CSV for next steps
        df_mentions.to_csv('data/raw_reddit_data.csv', index=False)
        print("Data saved to data/raw_reddit_data.csv")
    else:
        print("No posts found or an error occurred.")