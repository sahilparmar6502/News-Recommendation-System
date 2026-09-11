import os

import joblib
from sklearn.metrics.pairwise import cosine_similarity
from streamlit.runtime.caching import cache_resource


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
SIMILARITY_PATH = os.path.join(MODEL_DIR, "cosine_similarity.pkl")
MAPPING_PATH = os.path.join(MODEL_DIR, "news_mapping.pkl")


@cache_resource(show_spinner="Loading news recommendations...")
def load_model():
    paths = (VECTORIZER_PATH, SIMILARITY_PATH, MAPPING_PATH)
    missing = [path for path in paths if not os.path.exists(path)]
    if missing:
        raise FileNotFoundError(
            "Recommendation artifacts are missing. Run notebooks/cosine_similarity_model.ipynb first. "
            f"Missing: {', '.join(os.path.basename(path) for path in missing)}"
        )
    similarity_artifact = joblib.load(SIMILARITY_PATH)
    return {
        "vectorizer": joblib.load(VECTORIZER_PATH),
        "matrix": similarity_artifact["tfidf_matrix"],
        "articles": joblib.load(MAPPING_PATH),
    }


def get_recommendations(article_id, count=6):
    bundle = load_model()
    positions = {article["article_id"]: index for index, article in enumerate(bundle["articles"])}
    if article_id not in positions:
        return []
    scores = cosine_similarity(bundle["matrix"][positions[article_id]], bundle["matrix"]).ravel()
    scores[positions[article_id]] = -1
    indices = scores.argsort()[-count:][::-1]
    results = []
    for index in indices:
        article = dict(bundle["articles"][index])
        article["similarity"] = round(float(scores[index]), 3)
        results.append(article)
    return results