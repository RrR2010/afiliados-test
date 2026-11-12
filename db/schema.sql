-- Project SQLite database; separate from n8n's internal database.
-- Schema v0 (new DBs only). Future changes require migrations.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS products (
 id INTEGER PRIMARY KEY,
 canonical_name TEXT NOT NULL,
 brand TEXT,
 model TEXT,
 gtin TEXT,
 variant_json TEXT NOT NULL DEFAULT '{}',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS listings (
 id INTEGER PRIMARY KEY,
 product_id INTEGER REFERENCES products(id),
 marketplace TEXT NOT NULL,
 external_product_id TEXT,
 external_item_id TEXT NOT NULL,
 title TEXT NOT NULL,
 product_url TEXT,
 item_url TEXT,
 seller_id TEXT,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(marketplace, external_item_id)
);
CREATE TABLE IF NOT EXISTS price_observations (
 id INTEGER PRIMARY KEY,
 listing_id INTEGER NOT NULL REFERENCES listings(id),
 observed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 currency TEXT NOT NULL DEFAULT 'BRL',
 advertised_price_cents INTEGER NOT NULL CHECK(advertised_price_cents >= 0),
 original_price_cents INTEGER CHECK(original_price_cents >= 0),
 shipping_cents INTEGER CHECK(shipping_cents >= 0),
 conditions_json TEXT NOT NULL DEFAULT '{}',
 source TEXT NOT NULL,
 source_observation_id TEXT UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_prices_listing_time ON price_observations(listing_id, observed_at);
CREATE TABLE IF NOT EXISTS coupons (
 id INTEGER PRIMARY KEY,
 marketplace TEXT NOT NULL,
 code TEXT,
 terms_json TEXT NOT NULL DEFAULT '{}',
 valid_from TEXT,
 valid_until TEXT,
 validation_status TEXT NOT NULL DEFAULT 'unverified'
  CHECK(validation_status IN ('unverified','verified','invalid','expired')),
 checked_at TEXT
);
CREATE TABLE IF NOT EXISTS deal_candidates (
 id INTEGER PRIMARY KEY,
 listing_id INTEGER NOT NULL REFERENCES listings(id),
 observation_id INTEGER NOT NULL REFERENCES price_observations(id),
 score REAL,
 reasons_json TEXT NOT NULL DEFAULT '[]',
 review_status TEXT NOT NULL DEFAULT 'pending'
  CHECK(review_status IN ('pending','approved','rejected')),
 affiliate_url TEXT,
 affiliate_verified_at TEXT,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 reviewed_at TEXT
);
CREATE TABLE IF NOT EXISTS publications (
 id INTEGER PRIMARY KEY,
 candidate_id INTEGER NOT NULL REFERENCES deal_candidates(id),
 operator_number TEXT NOT NULL,
 message_text TEXT NOT NULL,
 meta_message_id TEXT,
 status TEXT NOT NULL DEFAULT 'draft'
  CHECK(status IN ('draft','approved','submitted','sent','delivered','read','failed')),
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 submitted_at TEXT
);
