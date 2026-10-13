CREATE DATABASE IF NOT EXISTS fake_news_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE fake_news_db;

CREATE TABLE IF NOT EXISTS predictions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  headline VARCHAR(300) NOT NULL,
  article_text TEXT NOT NULL,
  prediction VARCHAR(100) NOT NULL,
  confidence DOUBLE NULL,
  created_at VARCHAR(40) NOT NULL
);
