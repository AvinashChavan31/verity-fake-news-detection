import os
import re
import pickle
from datetime import datetime

from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-before-deployment")

# MySQL is used when configured; SQLite keeps the app easy to run locally.
DB_MODE = os.getenv("DB_MODE", "sqlite").lower()
MODEL_PATH = os.path.join("model", "fake_news_pipeline.pkl")
_pipeline = None

def load_pipeline():
    global _pipeline
    if _pipeline is None and os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "rb") as f:
                _pipeline = pickle.load(f)
        except Exception:
            _pipeline = None
    return _pipeline

def get_db():
    if DB_MODE == "mysql":
        import pymysql
        return pymysql.connect(
            host=os.getenv("MYSQL_HOST", "127.0.0.1"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "fake_news_db"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
    import sqlite3
    conn = sqlite3.connect("fake_news.db")
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT NOT NULL,
            article_text TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL,
            created_at TEXT NOT NULL
        )
    """)
    return conn

def save_prediction(headline, article_text, prediction, confidence):
    try:
        conn = get_db()
        if DB_MODE == "mysql":
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO predictions (headline, article_text, prediction, confidence, created_at) VALUES (%s, %s, %s, %s, %s)",
                    (headline, article_text, prediction, confidence, datetime.utcnow().isoformat(timespec="seconds"))
                )
        else:
            conn.execute(
                "INSERT INTO predictions (headline, article_text, prediction, confidence, created_at) VALUES (?, ?, ?, ?, ?)",
                (headline, article_text, prediction, confidence, datetime.utcnow().isoformat(timespec="seconds"))
            )
            conn.commit()
        conn.close()
    except Exception as exc:
        app.logger.warning("Could not save prediction: %s", exc)

def recent_predictions(limit=8):
    try:
        conn = get_db()
        if DB_MODE == "mysql":
            with conn.cursor() as cur:
                cur.execute("SELECT id, headline, prediction, confidence, created_at FROM predictions ORDER BY id DESC LIMIT %s", (limit,))
                rows = cur.fetchall()
        else:
            rows = conn.execute(
                "SELECT id, headline, prediction, confidence, created_at FROM predictions ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as exc:
        app.logger.warning("Could not read history: %s", exc)
        return []

def heuristic_demo_prediction(text):
    """Transparent fallback only; not a validated misinformation detector."""
    suspicious_phrases = [
        "you won't believe", "share this now", "shocking truth", "they don't want you to know",
        "secret cure", "100% guaranteed", "breaking!!!", "forward to everyone",
        "miracle cure", "wake up people"
    ]
    lowered = text.lower()
    hits = sum(1 for phrase in suspicious_phrases if phrase in lowered)
    exclamations = min(text.count("!"), 3)
    score = min(0.85, 0.52 + hits * 0.07 + exclamations * 0.025)
    if hits or exclamations >= 2:
        return "Potentially Misleading", score, "demo"
    return "Needs Verification", 0.50, "demo"

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", history=recent_predictions())

@app.route("/predict", methods=["POST"])
def predict():
    headline = request.form.get("headline", "").strip()
    article_text = request.form.get("article_text", "").strip()
    if not headline and not article_text:
        flash("Enter a headline or article text before checking.", "error")
        return redirect(url_for("index"))
    combined = (headline + " " + article_text).strip()
    if len(combined) < 20:
        flash("Please enter at least 20 characters so there is enough text to inspect.", "error")
        return redirect(url_for("index"))

    pipeline = load_pipeline()
    method = "demo"
    if pipeline is not None:
        try:
            prediction = str(pipeline.predict([combined])[0])
            confidence = None
            if hasattr(pipeline, "predict_proba"):
                probabilities = pipeline.predict_proba([combined])[0]
                confidence = float(max(probabilities))
            method = "trained_model"
        except Exception as exc:
            app.logger.warning("Model prediction failed, using demo fallback: %s", exc)
            prediction, confidence, method = heuristic_demo_prediction(combined)
    else:
        prediction, confidence, method = heuristic_demo_prediction(combined)

    save_prediction(headline or "(No headline)", article_text or combined, prediction, confidence)
    return render_template(
        "result.html",
        headline=headline or "(No headline provided)",
        article_text=article_text or combined,
        prediction=prediction,
        confidence=confidence,
        method=method,
    )

@app.route("/health")
def health():
    return {"status": "ok", "database_mode": DB_MODE, "trained_model_available": os.path.exists(MODEL_PATH)}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
