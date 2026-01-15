BEGIN;

-- =========================
-- MIGRATIONS META
-- =========================
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT now()
);

-- =========================
-- USERS (core identity)
-- =========================
CREATE TABLE IF NOT EXISTS app_users (
    id BIGSERIAL PRIMARY KEY,
    telegram_user_id BIGINT UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- =========================
-- USER SETTINGS
-- =========================
CREATE TABLE IF NOT EXISTS user_settings (
    user_id BIGINT PRIMARY KEY
        REFERENCES app_users(id) ON DELETE CASCADE,
    monthly_income INTEGER,
    currency VARCHAR(8) NOT NULL DEFAULT 'RUB'
);

-- =========================
-- CATEGORIES (hierarchy)
-- =========================
CREATE TABLE IF NOT EXISTS categories (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL
        REFERENCES app_users(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    parent_id BIGINT
        REFERENCES categories(id) ON DELETE SET NULL,

    type VARCHAR(16) NOT NULL CHECK (
        type IN ('expense', 'saving', 'investment')
    ),

    is_controlled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_categories_user
    ON categories(user_id);

-- =========================
-- CATEGORY BUDGET (share of income)
-- =========================
CREATE TABLE IF NOT EXISTS category_budget (
    category_id BIGINT PRIMARY KEY
        REFERENCES categories(id) ON DELETE CASCADE,

    share NUMERIC(5,4) NOT NULL CHECK (
        share >= 0 AND share <= 1
    )
);

-- =========================
-- FINANCE EVENTS (CORE FLOW)
-- =========================
CREATE TABLE IF NOT EXISTS finance_events_v2 (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL
        REFERENCES app_users(id) ON DELETE CASCADE,

    category_id BIGINT
        REFERENCES categories(id) ON DELETE SET NULL,

    kind VARCHAR(16) NOT NULL CHECK (
        kind IN ('income', 'expense', 'save', 'invest', 'withdraw')
    ),

    amount INTEGER NOT NULL,
    occurred_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_finance_events_user
    ON finance_events_v2(user_id);

CREATE INDEX IF NOT EXISTS idx_finance_events_date
    ON finance_events_v2(occurred_at);

-- =========================
-- GOALS
-- =========================
CREATE TABLE IF NOT EXISTS goals (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL
        REFERENCES app_users(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    target_amount INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- =========================
-- DAILY REPORTS (ANCHOR)
-- =========================
CREATE TABLE IF NOT EXISTS daily_reports (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL
        REFERENCES app_users(id) ON DELETE CASCADE,

    date DATE NOT NULL,

    score_total INTEGER NOT NULL DEFAULT 50,
    stars INTEGER NOT NULL DEFAULT 3,

    net_day INTEGER NOT NULL DEFAULT 0,
    expenses_day INTEGER NOT NULL DEFAULT 0,
    income_day INTEGER NOT NULL DEFAULT 0,

    has_income_basis BOOLEAN NOT NULL DEFAULT false,
    generated_at TIMESTAMP NOT NULL DEFAULT now(),

    UNIQUE (user_id, date)
);

-- =========================
-- QUOTES
-- =========================
CREATE TABLE IF NOT EXISTS quotes (
    id BIGSERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    author TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- =========================
-- USER QUOTE STATE
-- =========================
CREATE TABLE IF NOT EXISTS user_quote_state (
    user_id BIGINT PRIMARY KEY
        REFERENCES app_users(id) ON DELETE CASCADE,

    quote_id BIGINT
        REFERENCES quotes(id),

    assigned_at DATE NOT NULL
);

-- =========================
-- MIGRATION RECORD
-- =========================
INSERT INTO schema_migrations (version)
VALUES ('001_core')
ON CONFLICT (version) DO NOTHING;

COMMIT;
