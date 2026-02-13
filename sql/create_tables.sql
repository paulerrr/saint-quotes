CREATE TABLE saint_quotes (
  id INTEGER PRIMARY KEY,
  topic TEXT NOT NULL,
  quote TEXT NOT NULL,
  author TEXT NOT NULL,
  source_title TEXT NOT NULL,
  page INTEGER,
  source_file TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_saint_quotes_author ON saint_quotes(author);
CREATE INDEX idx_saint_quotes_topic ON saint_quotes(topic);
