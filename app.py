import streamlit as st

from database.db import get_connection, fetch_article, fetch_articles, fetch_categories
from recommendation.recommender import get_recommendations
from utils.helpers import format_date, truncate


st.set_page_config(page_title="News Recommendation System", page_icon="N", layout="wide")


@st.cache_data(ttl=300)
def load_categories():
    with get_connection() as connection:
        return fetch_categories(connection)


@st.cache_data(ttl=300)
def load_articles(category):
    with get_connection() as connection:
        return fetch_articles(connection, category)


@st.cache_data(ttl=300)
def load_article(article_id):
    with get_connection() as connection:
        return fetch_article(connection, article_id)


def select_article(article_id):
    st.session_state.selected_article_id = article_id


def render_card(article, key_prefix):
    with st.container(border=True):
        image_url = article.get("image_url")
        if isinstance(image_url, str) and image_url.strip():
            st.image(image_url, use_container_width=True)
        st.caption(f"{article.get('category', 'Uncategorized')}  ·  {format_date(article.get('publication_date'))}")
        st.subheader(article.get("headline") or "Untitled article")
        st.write(truncate(article.get("abstract") or article.get("lead_paragraph") or "No summary available.", 220))
        st.button("Read article", key=f"{key_prefix}-{article['article_id']}", on_click=select_article, args=(article["article_id"],), use_container_width=True)


def render_article(article):
    st.button("← Back to category", on_click=lambda: st.session_state.update(selected_article_id=None), type="secondary")
    st.caption(f"{article.get('category', 'Uncategorized')}  ·  {format_date(article.get('publication_date'))}")
    st.title(article.get("headline") or "Untitled article")
    if article.get("byline"):
        st.caption(article["byline"])
    if article.get("image_url"):
        st.image(article["image_url"], use_container_width=True)
    if article.get("abstract"):
        st.markdown(f"**{article['abstract']}**")
    body = article.get("lead_paragraph") or article.get("snippet")
    if body:
        st.write(body)
    if article.get("url"):
        st.link_button("Open original article", article["url"])

    st.divider()
    st.header("Recommended News")
    try:
        recommendations = get_recommendations(article["article_id"])
    except Exception as error:
        st.error(f"Recommendations are unavailable: {error}")
        recommendations = []
    if not recommendations:
        st.info("There are no similar articles available yet.")
        return
    columns = st.columns(min(3, len(recommendations)))
    for index, recommendation in enumerate(recommendations):
        with columns[index % len(columns)]:
            render_card(recommendation, f"recommendation-{index}")


def main():
    st.title("News Recommendation System")
    st.write("Explore the latest stories by category, then follow the threads that interest you.")
    try:
        categories = load_categories()
    except Exception as error:
        st.error(f"Unable to connect to MySQL: {error}")
        st.info("Copy .env.example to .env, configure MySQL, and run database/setup_db.py.")
        st.stop()
    if not categories:
        st.warning("No news categories are available. Run database/setup_db.py to import the CSV.")
        st.stop()

    if "category" not in st.session_state:
        st.session_state.category = categories[0] if categories else None
    if "selected_article_id" not in st.session_state:
        st.session_state.selected_article_id = None

    selected_article_id = st.session_state.selected_article_id
    if selected_article_id:
        article = load_article(selected_article_id)
        if article:
            render_article(article)
            return
        st.session_state.selected_article_id = None

    selected_category = st.selectbox("Browse category", categories, index=categories.index(st.session_state.category) if st.session_state.category in categories else 0)
    st.session_state.category = selected_category
    articles = load_articles(selected_category)
    st.subheader(f"{selected_category} news")
    if not articles:
        st.info("No articles were found in this category.")
        return
    columns = st.columns(3)
    for index, article in enumerate(articles):
        with columns[index % 3]:
            render_card(article, f"article-{index}")


if __name__ == "__main__":
    main()