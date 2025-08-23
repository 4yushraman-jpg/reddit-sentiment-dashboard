# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta
from src.db_utils import DB_FILE, load_data

# --- Page Configuration ---
st.set_page_config(
    page_title="Brand Sentiment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Helper Functions ---
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data_from_file():
    """Load data from the database and get the last update time."""
    try:
        if not os.path.exists(DB_FILE):
            return pd.DataFrame(), None
        
        df = load_data()
        if df.empty:
            return pd.DataFrame(), None
            
        df['date'] = df['created_utc'].dt.date
        last_updated = datetime.fromtimestamp(os.path.getmtime(DB_FILE))
        return df, last_updated
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(), None

@st.cache_data
def convert_df_to_csv(df):
    """Converts a DataFrame to a CSV string for downloading."""
    return df.to_csv(index=False).encode('utf-8')

def format_large_number(num):
    """Format large numbers with K, M suffixes for better readability."""
    if num >= 1_000_000:
        return f'{num/1_000_000:.1f}M'
    elif num >= 1_000:
        return f'{num/1_000:.1f}K'
    else:
        return str(num)

# --- Main Application ---
def main():
    st.title("Brand Sentiment Dashboard")
    st.markdown("Track and analyze brand mentions and sentiment across Reddit communities.")

    # --- Color Palettes ---
    SENTIMENT_COLORS = {'Positive': '#2ec4b6', 'Neutral': '#adb5bd', 'Negative': '#ef476f'}
    BRAND_COLORS = {'NVIDIA': '#0077B6', 'AMD': '#EF476F', 'Intel': '#FFD166'}

    # --- Load Data ---
    with st.spinner("Loading data..."):
        df, last_updated = load_data_from_file()
    
    if df.empty:
        st.error("No data found! Please run the data scraper first.")
        if st.button("Retry Loading Data"):
            st.cache_data.clear()
            st.rerun()
        st.stop()

    # --- Sidebar Filters ---
    st.sidebar.header("Filters")
    if last_updated:
        st.sidebar.caption(f"Data last updated: {last_updated.strftime('%b %d, %Y %H:%M')}")
    
    # Brand selection
    all_brands = sorted(df['brand'].unique())
    selected_brands = st.sidebar.multiselect(
        "Brands", 
        all_brands, 
        default=all_brands,
        help="Select brands to analyze"
    )
    
    # Subreddit selection
    all_subreddits = sorted(df['subreddit'].unique())
    selected_subreddits = st.sidebar.multiselect(
        "Subreddits", 
        all_subreddits, 
        default=all_subreddits,
        help="Select subreddits to include in analysis"
    )
    
    # Date range with proper handling
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    # Default to last 30 days or full range if less than 30 days
    default_start = max(min_date, max_date - timedelta(days=30))
    default_end = max_date
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(default_start, default_end),
        min_value=min_date,
        max_value=max_date
    )
    
    # Ensure we have both start and end dates
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date
        st.sidebar.warning("Please select both start and end dates")

    # Sentiment filter
    sentiment_options = ['Positive', 'Neutral', 'Negative']
    selected_sentiments = st.sidebar.multiselect(
        "Sentiment", 
        sentiment_options, 
        default=sentiment_options,
        help="Filter by sentiment type"
    )

    # --- Apply Filters ---
    filtered_df = df[
        (df['brand'].isin(selected_brands)) &
        (df['subreddit'].isin(selected_subreddits)) &
        (df['date'] >= start_date) &
        (df['date'] <= end_date) &
        (df['sentiment_label'].isin(selected_sentiments))
    ]
    
    if filtered_df.empty:
        st.warning("No data matches your filters. Try adjusting your selection.")
        st.stop()

    # --- Overview Section ---
    st.subheader("High-Level Summary")
    
    # KPIs
    kpi_cols = st.columns(4)
    
    # Total mentions
    total_mentions = len(filtered_df)
    kpi_cols[0].metric("Total Mentions", format_large_number(total_mentions))
    
    # Average sentiment
    avg_sentiment = filtered_df['sentiment_score'].mean()
    sentiment_trend = "neutral"
    kpi_cols[1].metric("Average Sentiment", f"{avg_sentiment:.2f}", delta=sentiment_trend)
    
    # Sentiment distribution
    sentiment_counts = filtered_df['sentiment_label'].value_counts()
    positive_pct = (sentiment_counts.get('Positive', 0) / total_mentions * 100) if total_mentions > 0 else 0
    kpi_cols[2].metric("Positive Mentions", f"{positive_pct:.1f}%")
    
    # Most active subreddit
    most_active_sub = filtered_df['subreddit'].mode()[0] if not filtered_df.empty else "N/A"
    kpi_cols[3].metric("Most Active Community", most_active_sub)

    st.markdown("---")

    # --- Daily Mention Volume ---
    st.subheader("Daily Mention Volume")
    
    trends_df = filtered_df.groupby(['date', 'brand']).size().reset_index(name='mentions')
    
    if not trends_df.empty:
        fig = px.line(
            trends_df, x='date', y='mentions', color='brand',
            color_discrete_map=BRAND_COLORS, 
            template='plotly_white', 
            markers=True,
            title="Daily Brand Mentions Over Time"
        )
        fig.update_layout(
            xaxis_title="Date", 
            yaxis_title="Mentions",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected date range.")

    # Two-column layout for additional charts
    col1, col2 = st.columns(2)
    
    with col1:
        # --- Sentiment Breakdown by Brand ---
        st.subheader("Sentiment Breakdown by Brand")
        brand_sentiment = filtered_df.groupby(['brand', 'sentiment_label']).size().reset_index(name='count')
        
        if not brand_sentiment.empty:
            fig3 = px.bar(
                brand_sentiment,
                x='brand',
                y='count',
                color='sentiment_label',
                color_discrete_map=SENTIMENT_COLORS,
                template='plotly_white',
                title="Sentiment Distribution by Brand"
            )
            fig3.update_layout(
                barmode='stack', 
                xaxis_title="Brand", 
                yaxis_title="Mentions",
                legend_title="Sentiment"
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No sentiment data available for selected brands.")

    with col2:
        # --- Community Hotspot Matrix ---
        st.subheader("Community Hotspot Matrix")
        subreddit_analysis = filtered_df.groupby('subreddit').agg(
            mention_count=('id', 'count'),
            avg_sentiment=('sentiment_score', 'mean')
        ).reset_index()
        
        if not subreddit_analysis.empty:
            fig2 = px.scatter(
                subreddit_analysis,
                x='mention_count',
                y='avg_sentiment',
                size='mention_count',
                color='avg_sentiment',
                color_continuous_scale=px.colors.sequential.Tealgrn,
                size_max=50,
                hover_name='subreddit',
                template='plotly_white',
                labels={
                    'mention_count': 'Volume of Mentions',
                    'avg_sentiment': 'Average Sentiment Score'
                },
                title="Community Engagement vs. Sentiment"
            )
            fig2.update_traces(
                hovertemplate="<b>%{hovertext}</b><br>Mentions: %{x}<br>Sentiment: %{y:.2f}<extra></extra>"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No community data available.")

    # --- Top Posts Section ---
    st.subheader("Top Posts")
    
    # Select metric for top posts
    sort_option = st.selectbox(
        "Sort by",
        ["Highest Sentiment", "Lowest Sentiment", "Most Recent"],
        key="post_sort"
    )
    
    if sort_option == "Highest Sentiment":
        top_posts = filtered_df.nlargest(5, 'sentiment_score')
    elif sort_option == "Lowest Sentiment":
        top_posts = filtered_df.nsmallest(5, 'sentiment_score')
    else:  # Most Recent
        top_posts = filtered_df.nlargest(5, 'created_utc')
    
    for _, post in top_posts.iterrows():
        with st.expander(f"{post['brand']} - {post['sentiment_label']} sentiment - {post['created_utc'].strftime('%Y-%m-%d')}"):
            st.write(f"**Subreddit:** r/{post['subreddit']}")
            st.write(f"**Sentiment Score:** {post['sentiment_score']:.2f}")
            st.write(f"**Text:** {post['text']}")
            st.write(f"**[Link to post]({post['url']})**")

    # --- Data Explorer ---
    st.subheader("Raw Data Explorer")
    
    # Show data summary
    st.write(f"Showing {len(filtered_df)} of {len(df)} total records")
    
    # Data table with configurable page size
    page_size = st.selectbox("Rows per page", [10, 25, 50, 100], index=0)
    st.dataframe(
        filtered_df[['brand', 'subreddit', 'created_utc', 'sentiment_score', 'sentiment_label', 'text', 'url']], 
        use_container_width=True,
        height=min(400, (page_size + 1) * 35)  # Dynamic height based on page size
    )
    
    # Download options
    csv = convert_df_to_csv(filtered_df)
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='reddit_sentiment_data.csv',
        mime='text/csv',
    )

if __name__ == "__main__":
    main()