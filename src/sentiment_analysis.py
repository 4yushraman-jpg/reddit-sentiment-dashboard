import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def get_sentiment_label(score):
    """
    Categorizes a sentiment score into Positive, Neutral, or Negative.
    """
    if score >= 0.05:
        return 'Positive'
    elif score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

def add_sentiment_scores(df):
    """
    Analyzes the sentiment of text in a DataFrame and adds sentiment scores and labels.

    Args:
        df (pandas.DataFrame): DataFrame with a 'text' column.

    Returns:
        pandas.DataFrame: The original DataFrame with added 'sentiment_score' and 'sentiment_label' columns.
    """
    if 'text' not in df.columns:
        raise ValueError("DataFrame must contain a 'text' column.")
        
    analyzer = SentimentIntensityAnalyzer()
    
    # Calculate sentiment score (compound score)
    df['sentiment_score'] = df['text'].apply(lambda text: analyzer.polarity_scores(text)['compound'])
    
    # Assign sentiment label based on the score
    df['sentiment_label'] = df['sentiment_score'].apply(get_sentiment_label)
    
    return df

if __name__ == '__main__':
    # Example usage
    data = {'text': [
        "NVIDIA's new GPU is absolutely amazing!",
        "I'm having a lot of driver issues with my AMD card.",
        "The price of the new graphics card is okay.",
        "I hate the new software update, it's terrible.",
        "The performance is exactly as advertised."
    ]}
    df_test = pd.DataFrame(data)
    
    df_analyzed = add_sentiment_scores(df_test)
    print(df_analyzed)