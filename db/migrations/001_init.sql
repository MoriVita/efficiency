BEGIN;

CREATE TABLE IF NOT EXISTS schema_migrations (
  version TEXT PRIMARY KEY,
  applied_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS users (
  telegram_user_id BIGINT PRIMARY KEY,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS finance_events (
  id BIGSERIAL PRIMARY KEY,
  telegram_user_id BIGINT NOT NULL REFERENCES users(telegram_user_id),
  ts TIMESTAMP NOT NULL DEFAULT now(),
  amount INTEGER NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('save', 'invest', 'expense')),
  category TEXT,
  note TEXT
);

CREATE TABLE IF NOT EXISTS limits (
  id BIGSERIAL PRIMARY KEY,
  telegram_user_id BIGINT NOT NULL REFERENCES users(telegram_user_id),
  category TEXT NOT NULL,
  month INTEGER NOT NULL,
  year INTEGER NOT NULL,
  monthly_limit INTEGER NOT NULL,
  UNIQUE (telegram_user_id, category, month, year)
);

INSERT INTO schema_migrations (version)
VALUES ('001_init')
ON CONFLICT (version) DO NOTHING;

COMMIT;
