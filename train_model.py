"""Train a TF-IDF + Logistic Regression text classifier from a labelled CSV.

Expected CSV columns:
  text,label
Labels should be consistent, e.g. REAL and FAKE.
Use a reputable, appropriately licensed dataset. The included sample is for
pipeline demonstration only and is far too small for real-world conclusions.
"""
import argparse
import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/sample_news.csv")
    parser.add_argument("--text-column", default="text")
    parser.add_argument("--label-column", default="label")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    df = df[[args.text_column, args.label_column]].dropna()
    df[args.text_column] = df[args.text_column].astype(str).str.strip()
    df = df[df[args.text_column].str.len() >= 20]
    if df[args.label_column].nunique() < 2:
        raise SystemExit("Dataset must contain at least two distinct labels.")
    if len(df) < 10:
        raise SystemExit("Please use at least 10 labelled rows; a much larger dataset is recommended.")

    X_train, X_test, y_train, y_test = train_test_split(
        df[args.text_column], df[args.label_column],
        test_size=0.25, random_state=42, stratify=df[args.label_column]
    )
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english", max_features=30000, ngram_range=(1, 2))),
        ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced"))
    ])
    pipeline.fit(X_train, y_train)
    print("Evaluation on held-out sample (not proof of real-world performance):")
    print(classification_report(y_test, pipeline.predict(X_test), zero_division=0))
    os.makedirs("model", exist_ok=True)
    with open(os.path.join("model", "fake_news_pipeline.pkl"), "wb") as f:
        pickle.dump(pipeline, f)
    print("Saved model/model fake_news_pipeline.pkl")

if __name__ == "__main__":
    main()
