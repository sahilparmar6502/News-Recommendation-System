# News Recommendation System

A simple content-based news recommendation app built with Python, Streamlit, MySQL, and scikit-learn.

It lets users:
- browse news articles by category
- open each article details page
- view recommended articles based on similarity
- use a TF-IDF + cosine similarity model for recommendations

## Project overview

This project has two main parts:

1. Database layer
   - Reads the dataset from `dataset/news.csv`
   - Stores it in MySQL using `database/setup_db.py`
   - The app fetches categories, article lists, and article details from the database

2. Recommendation layer
   - Uses a notebook to train a TF-IDF model on article text
   - Builds cosine similarity scores between articles
   - Saves model artifacts into the `models/` folder
   - The app loads these saved files to show related articles quickly

## Tech stack

- Python 3.10+
- Streamlit
- MySQL
- pandas
- scikit-learn

## Folder structure

```text
.
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── dataset/
│   └── news.csv
├── database/
│   ├── db.py
│   └── setup_db.py
├── recommendation/
│   └── recommender.py
├── models/
├── notebooks/
│   └── cosine_similarity_model.ipynb
├── utils/
│   └── helpers.py
└── .venv/   # optional local virtual environment
```

## Prerequisites

Before running the project, make sure you have:

- Python installed
- MySQL server running locally or on a remote machine
- A dataset file at `dataset/news.csv`

## Configuration

Create a local environment file from the example:

```bash
cp .env.example .env
```

Then update `.env` with your MySQL settings:

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=news_recommendation
```

Important notes:
- `MYSQL_USER` should have permission to create the database if it does not exist
- The app uses `MYSQL_DATABASE` as the database name
- If needed, you can create the database manually before running the setup script

## Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Import data into MySQL

Run this script to create the database and table, and import the CSV:

```bash
python database/setup_db.py
```

This script will:
- create the database if it does not exist
- create the `news_articles` table
- insert rows from `dataset/news.csv`

## Generate recommendation model

Before opening the app, train the recommendation model from the notebook:

```bash
jupyter notebook notebooks/cosine_similarity_model.ipynb
```

Run all cells in the notebook. The notebook will:
- read the CSV data
- combine text fields like headline, abstract, snippet, and keywords
- fit a TF-IDF vectorizer
- compute cosine similarity
- save model files in `models/`

The expected saved files are:
- `models/tfidf_vectorizer.pkl`
- `models/cosine_similarity.pkl`
- `models/news_mapping.pkl`

## Run the app

Start the Streamlit application:

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## How it works

- The app loads article categories and content from MySQL
- When a user opens an article, the recommender loads the saved model artifacts
- It compares the selected article with other articles using cosine similarity
- The most similar articles are shown as recommendations