# Verity — Fake News Detection System

A Flask web application that demonstrates a text-classification workflow for news-literacy education. It accepts a headline/article, returns a model output, and stores recent checks in a database.

> **Important limitation:** This project does not establish whether a story is true or false. The included CSV is a tiny illustrative sample created to demonstrate the training pipeline, not a valid benchmark dataset. The app's phrase-based fallback is explicitly marked as demo mode. For meaningful model evaluation, use a reputable, licensed, well-documented dataset and test for source/topic leakage, class imbalance, and out-of-distribution text.

## Features

- Flask-based web UI with responsive styling
- Headline and article-text input
- TF-IDF + Logistic Regression training pipeline
- Transparent demo fallback when no trained model is present
- Prediction history stored in SQLite by default, with optional MySQL configuration
- `/health` endpoint for deployment checks
- Training script and CSV format example

## 1. Requirements

- Python 3.10 or newer
- pip
- Optional: MySQL Server 8+ if you want MySQL instead of SQLite

## 2. Run locally

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, run `.venv\Scripts\python.exe -m pip install -r requirements.txt`, then `.venv\Scripts\python.exe app.py`.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser. `/health` returns basic app status.

## 3. Train the sample pipeline (demo only)

```bash
python train_model.py --csv data/sample_news.csv
```

This writes `model/fake_news_pipeline.pkl`. The tiny sample exists only to demonstrate the workflow; metrics from it are not meaningful. For a real submission, replace it with a suitable labelled dataset and document its source/license. The generated model is excluded from Git by `.gitignore`; regenerate it after cloning.

Expected dataset format:

```csv
text,label
"An article text...",REAL
"Another article text...",FAKE
```

The text and label column names can be changed with `--text-column` and `--label-column`. Use a stratified held-out set, check per-class precision/recall, and avoid claiming the classifier is accurate without robust evaluation.

## 4. Use MySQL (optional)

SQLite is the default to make first-run setup simple. To use MySQL:

1. Start MySQL Server.
2. Run the statements in `schema.sql` using a MySQL client.
3. Set environment variables before starting the app:

**PowerShell**
```powershell
$env:DB_MODE="mysql"
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your_password"
$env:MYSQL_DATABASE="fake_news_db"
python app.py
```

**macOS / Linux**
```bash
export DB_MODE=mysql
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD='your_password'
export MYSQL_DATABASE=fake_news_db
python app.py
```

Do not commit passwords or secret keys. Use a dedicated database user with only the permissions the application needs.

## 5. Upload to GitHub

1. Create a repository at https://github.com/new (for example `verity-fake-news-detection`).
2. Extract this ZIP and open a terminal in the extracted folder.
3. Review the files; do not upload secrets, private datasets, or personal information.
4. Run:

```bash
git init
git add .
git commit -m "Initial Verity fake news detection project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/verity-fake-news-detection.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. If Git is not installed, install it from https://git-scm.com/downloads. You can also upload files through GitHub's web interface.

Your repository URL will look like:
`https://github.com/YOUR-USERNAME/verity-fake-news-detection`

## 6. Deploy a live demo

The app can be deployed on a Python-compatible host that supports Flask and persistent storage. For a simple demo, SQLite may work only if the host provides persistent disk; otherwise prediction history may reset. MySQL requires a reachable managed MySQL database and environment variables.

Typical settings:
- Build/install command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Health check path: `/health`
- Environment: `FLASK_SECRET_KEY` set to a long random value; `DB_MODE=sqlite` for a temporary demo or `DB_MODE=mysql` with database credentials.

Important: the trained model file is not committed. If you want model predictions after deployment, use a proper dataset to train the model, then arrange to build/provide the model artifact during deployment. Do not expose private datasets or database credentials.

## Project structure

```text
fake_news_detection_system/
├── app.py
├── train_model.py
├── requirements.txt
├── schema.sql
├── .env.example
├── .gitignore
├── README.md
├── data/
│   └── sample_news.csv
├── model/
└── static/
    └── style.css
└── templates/
    ├── index.html
    └── result.html
```

## Interview explanation

“Verity is a Flask-based educational news-text screening application. It processes a headline and article text and can use a TF-IDF vectorizer with Logistic Regression for text classification. It stores analysis history in SQLite by default and supports MySQL through configuration. I also included a health endpoint and a training script. The current sample data is illustrative, so I would not claim real-world accuracy until I train and evaluate it on a larger, licensed dataset.”

## Security and responsible use

- Never commit secrets, database credentials, or private datasets.
- Treat all model outputs as uncertain suggestions, not truth labels.
- The sample/fallback is for demonstration and must not be used to make consequential decisions.
- Before production use, add authentication, CSRF protection, input/output review, rate limiting, privacy controls, and stronger database error handling.
