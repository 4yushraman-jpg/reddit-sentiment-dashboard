# 📘 Interactive Brand Sentiment Web App

## 🔍 Business Problem
A Marketing Manager at a tech company (e.g., NVIDIA) needs a near real-time tool to monitor public perception of their products on Reddit.  
Currently, monitoring is **ad-hoc and reactive**. This project aims to provide an **automated, objective view of brand sentiment** so the team can quickly detect PR risks, understand customer feedback, and amplify positive discussions.

**Goal:** Build an end-to-end pipeline that:
- Scrapes Reddit for brand mentions  
- Performs sentiment analysis  
- Stores results in a database  
- Visualizes insights in an interactive Streamlit dashboard  

---

## ❓ Key Questions (KQs)
The dashboard must help answer:

1. **Volume** — How often are our brands (e.g., NVIDIA) and competitors (e.g., AMD) being mentioned?  
2. **Sentiment** — Are mentions mostly positive, negative, or neutral?  
3. **Trends** — How do sentiment and mentions evolve over time? Are there sudden spikes?  
4. **Location** — Which subreddits drive the conversations? (e.g., r/hardware vs r/gaming)  
5. **Context** — What are people actually saying? (Top posts and comments driving sentiment)  

---

## 📊 Initial Hypotheses
- **H1:** Sentiment spikes positively during product launches.  
- **H2:** Sentiment spikes negatively during technical issues (e.g., driver problems).  
- **H3:** Enthusiast subreddits (e.g., r/hardware) will have more critical sentiment than broader ones (e.g., r/gaming).  

---

## 🛠️ Technical Approach

### Phase Breakdown
- **Phase 0: Planning (this doc)**  
- **Phase 1: Proof of Concept (PoC)** → Pull a static batch of Reddit data into Jupyter Notebook, run EDA + simple sentiment (VADER).  
- **Phase 2: Prototype Dashboard** → Local Streamlit app reading from CSV, show interactive charts & tables.  
- **Phase 3: Production Pipeline** → Automate scraping + sentiment, store in PostgreSQL, incremental updates.  
- **Phase 4: Deployment** → Deploy Streamlit to the cloud, add monitoring & alerting for sentiment spikes.  

### Core Components
- **Data Extractor** → Scrape Reddit posts/comments (`praw`, Pushshift API for history).  
- **Sentiment Analyzer** → Clean text + score with VADER (fast) or transformer (optional).  
- **Storage** → Start with CSV/SQLite → move to PostgreSQL.  
- **Dashboard** → Streamlit with filters, sentiment trends, subreddit breakdown, and top posts.  
- **Automation** → Scheduler (GitHub Actions / cron) for continuous updates.  

---

## 🗂️ Data Schema (Minimum)
| Column           | Description                                |
|------------------|--------------------------------------------|
| `id`             | Unique Reddit post/comment ID              |
| `brand`          | Brand tag (NVIDIA, AMD, etc.)              |
| `text`           | Post or comment text                       |
| `subreddit`      | Subreddit name                             |
| `author`         | Reddit username (anonymized if needed)     |
| `created_utc`    | Timestamp of post/comment                  |
| `sentiment_score`| Numeric score (-1 to +1)                   |
| `sentiment_label`| Positive / Neutral / Negative              |
| `url`            | Link to the original Reddit post/comment   |

---

## ✅ Success Criteria
- PoC → Able to fetch 1,000+ posts and compute sentiment distribution.  
- Prototype → Streamlit dashboard loads CSV, answers all 5 Key Questions.  
- Production → Daily automation into DB; dashboard reflects latest data without manual steps.  
- Stakeholder → Marketing Manager can answer Key Questions and export results.  

---

## ⚠️ Risks & Mitigation
- **API Limits** → Use Pushshift for history; respect rate limits.  
- **Noisy Data (sarcasm, slang)** → Start with VADER; refine with ML models later.  
- **Privacy / TOS** → Only use public Reddit data, compliant with Reddit’s API terms.  

---

## 🚀 Next Steps (First 48h)
1. Set up environment (`requirements.txt` with praw, pandas, vaderSentiment, streamlit).  
2. Run a PoC Jupyter Notebook: fetch Reddit mentions for NVIDIA & AMD, apply sentiment, plot quick charts.  
3. Document findings & refine hypotheses before moving to dashboard.  

---

## 📂 Project Structure (planned)
interactive-brand-sentiment/
│── README.md                  # Project plan & documentation  
│── requirements.txt           # Dependencies  
│── notebooks/  
│    └── poc_exploration.ipynb # Proof of Concept analysis  
│── src/  
│    ├── reddit_scraper.py     # Fetch Reddit posts/comments  
│    ├── sentiment_analysis.py # Sentiment scoring  
│    ├── database.py           # SQLite/PostgreSQL handling  
│── app.py                     # Streamlit dashboard  
│── data/  
│    └── reddit_raw.csv        # Collected Reddit data  
