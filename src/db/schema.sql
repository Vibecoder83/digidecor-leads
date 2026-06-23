-- Digidecor Lead Intelligence — database schema
-- Run via: python src/db/init_db.py

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ── businesses ────────────────────────────────────────────────
-- One row per discovered business.
CREATE TABLE IF NOT EXISTS businesses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    source          TEXT    NOT NULL,       -- e.g. 'kvk', 'osm', 'manual'
    city            TEXT,
    region          TEXT    DEFAULT 'Drenthe',
    phone           TEXT,
    email           TEXT,
    website_url     TEXT,
    category        TEXT,                   -- e.g. 'restaurant', 'kapper'
    created_at      TEXT    DEFAULT (datetime('now')),
    updated_at      TEXT    DEFAULT (datetime('now'))
);

-- ── crawl_results ─────────────────────────────────────────────
-- One row per crawl attempt on a business website.
CREATE TABLE IF NOT EXISTS crawl_results (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id     INTEGER NOT NULL REFERENCES businesses(id),
    crawled_at      TEXT    DEFAULT (datetime('now')),
    status_code     INTEGER,                -- HTTP status, e.g. 200, 404
    final_url       TEXT,                   -- after redirects
    page_title      TEXT,
    meta_generator  TEXT,                   -- e.g. 'WordPress 4.2'
    copyright_year  INTEGER,                -- extracted from footer
    has_mobile      INTEGER DEFAULT 0,      -- 0/1 boolean
    has_ssl         INTEGER DEFAULT 0,
    load_time_ms    INTEGER,
    raw_html_size   INTEGER,                -- bytes
    error           TEXT                    -- null if successful
);

-- ── signals ───────────────────────────────────────────────────
-- Individual outdated-site signals extracted per crawl.
CREATE TABLE IF NOT EXISTS signals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    crawl_id        INTEGER NOT NULL REFERENCES crawl_results(id),
    signal_key      TEXT    NOT NULL,       -- e.g. 'old_copyright', 'no_ssl'
    signal_value    TEXT,                   -- raw extracted value
    weight          REAL    DEFAULT 1.0     -- for scoring
);

-- ── scores ────────────────────────────────────────────────────
-- Computed opportunity score per business, updated each run.
CREATE TABLE IF NOT EXISTS scores (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id     INTEGER NOT NULL REFERENCES businesses(id),
    scored_at       TEXT    DEFAULT (datetime('now')),
    total_score     REAL    NOT NULL,       -- higher = better lead
    score_breakdown TEXT                    -- JSON blob of signal contributions
);

-- ── Indexes ───────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_businesses_website   ON businesses(website_url);
CREATE INDEX IF NOT EXISTS idx_crawl_business       ON crawl_results(business_id);
CREATE INDEX IF NOT EXISTS idx_signals_crawl        ON signals(crawl_id);
CREATE INDEX IF NOT EXISTS idx_scores_business      ON scores(business_id);
CREATE INDEX IF NOT EXISTS idx_scores_total         ON scores(total_score DESC);
