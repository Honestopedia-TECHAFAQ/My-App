import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Real-Time News Aggregator By Afaq Ahmad", layout="wide")

st.markdown("""
    <style>
    body {
        font-family: 'Helvetica Neue', sans-serif;
        background-color: #f4f4f9;
        color: #333;
    }
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    .header {
        text-align: center;
        margin-bottom: 30px;
    }
    .news-container {
        margin: 20px 0;
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        display: flex;
        align-items: flex-start;
        transition: transform 0.2s;
    }
    .news-container:hover {
        transform: translateY(-5px);
    }
    .news-image {
        width: 150px;
        height: 100px;
        object-fit: cover;
        border-radius: 5px;
        margin-right: 20px;
    }
    .category-title {
        font-size: 28px;
        color: #004080;
        margin-top: 40px;
        border-bottom: 2px solid #004080;
        padding-bottom: 10px;
    }
    .article-title {
        font-size: 20px;
        font-weight: bold;
        color: #0066cc;
    }
    .article-summary {
        font-size: 16px;
        margin-top: 10px;
    }
    .footer {
        text-align: center;
        margin-top: 40px;
        font-size: 14px;
        color: #777;
    }
    </style>
""", unsafe_allow_html=True)
rss_urls = [
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://feeds.foxnews.com/foxnews/latest",
    "https://www.sec.gov/rss/news/press.xml",
    "https://www.federalreserve.gov/feeds/press_all.xml"
]
categories = {
    "Politics": [],
    "World": [],
    "Finance": [],
    "Technology": [],
    "Health": [],
    "Sports": [],
    "Entertainment": [],
    "Others": []
}
@st.cache_data(ttl=600)
def fetch_feed(url):
    """Fetch RSS feed data from the URL and return a dictionary."""
    feed = feedparser.parse(url)
    return {"entries": [entry for entry in feed.entries]}

@st.cache_data(ttl=600)
def fetch_article_content(link):
    """Fetch the full article content from the link."""
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = soup.find_all('p')
    full_content = " ".join([p.get_text() for p in paragraphs])
    return full_content

def summarize_content(content):
    """Summarize the content to 100 words or less."""
    words = content.split()
    if len(words) > 100:
        return " ".join(words[:100]) + "..."
    else:
        return content

def categorize_article(title, summary, image_url):
    """Categorize articles into predefined categories."""
    title_lower = title.lower()
    if any(word in title_lower for word in ["politics", "government", "election", "president", "senate"]):
        categories["Politics"].append({"title": title, "summary": summary, "image": image_url})
    elif any(word in title_lower for word in ["world", "international", "global"]):
        categories["World"].append({"title": title, "summary": summary, "image": image_url})
    elif any(word in title_lower for word in ["finance", "money", "stock", "market", "economy"]):
        categories["Finance"].append({"title": title, "summary": summary, "image": image_url})
    elif any(word in title_lower for word in ["technology", "tech", "innovation", "software", "hardware"]):
        categories["Technology"].append({"title": title, "summary": summary, "image": image_url})
    elif any(word in title_lower for word in ["health", "medicine", "wellness", "disease"]):
        categories["Health"].append({"title": title, "summary": summary, "image": image_url})
    elif any(word in title_lower for word in ["sports", "game", "tournament", "football", "soccer", "basketball"]):
        categories["Sports"].append({"title": title, "summary": summary, "image": image_url})
    elif any(word in title_lower for word in ["entertainment", "movie", "music", "celebrity", "show"]):
        categories["Entertainment"].append({"title": title, "summary": summary, "image": image_url})
    else:
        categories["Others"].append({"title": title, "summary": summary, "image": image_url})
st_autorefresh(interval=300000, key="data_refresh")
with st.container():
    st.markdown("<h1 class='header'>Real-Time News Aggregator</h1>", unsafe_allow_html=True)
    for url in rss_urls:
        feed = fetch_feed(url)
        for entry in feed["entries"]:
            title = entry.title
            link = entry.link
            image_url = entry.get("media_content", [{}])[0].get("url", "")

            try:
                full_content = fetch_article_content(link)
                summary = summarize_content(full_content)
                categorize_article(title, summary, image_url)

            except Exception as e:
                st.warning(f"Failed to fetch or summarize article: {title}. Error: {e}")
    for category, articles in categories.items():
        if articles:
            st.markdown(f"<div class='category-title'>{category}</div>", unsafe_allow_html=True)
            for article in articles:
                st.markdown(
                    f"""
                    <div class='news-container'>
                        <img src='{article['image']}' class='news-image' alt='news image'>
                        <div>
                            <div class='article-title'>{article['title']}</div>
                            <div class='article-summary'>{article['summary']}</div>
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                st.write("---")
    st.markdown("<div class='footer'> | © 2024</div>", unsafe_allow_html=True)
