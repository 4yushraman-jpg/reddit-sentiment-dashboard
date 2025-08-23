# src/db_utils.py
import pandas as pd
import sqlite3
import os

# Define constants for the database file and table name
DB_DIR = 'data'
DB_FILE = os.path.join(DB_DIR, 'reddit_sentiment.db')
TABLE_NAME = 'mentions'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    return conn

def save_data(df):
    """
    Saves a DataFrame to the SQLite database.
    - Appends new data if the table already exists.
    - Creates a new table if it doesn't.
    """
    if df.empty:
        print("Dataframe is empty, nothing to save.")
        return

    conn = get_db_connection()
    try:
        # Use 'append' to add new data without deleting old data
        df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
        print(f"Successfully saved {len(df)} new records to the '{TABLE_NAME}' table.")
    except Exception as e:
        print(f"An error occurred while saving data: {e}")
    finally:
        conn.close()

def load_data():
    """Loads all data from the SQLite database into a DataFrame."""
    if not os.path.exists(DB_FILE):
        return pd.DataFrame() # Return empty DataFrame if DB doesn't exist

    conn = get_db_connection()
    try:
        query = f"SELECT * FROM {TABLE_NAME}"
        df = pd.read_sql(query, conn)
        
        # Ensure 'created_utc' is treated as datetime
        df['created_utc'] = pd.to_datetime(df['created_utc'], unit='s')
        return df
    except Exception as e:
        # This handles the case where the table might not exist yet
        print(f"An error occurred while loading data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()