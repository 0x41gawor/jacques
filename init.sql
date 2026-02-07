CREATE TABLE IF NOT EXISTS words (
    word TEXT PRIMARY KEY
);


CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    google_id   TEXT NOT NULL UNIQUE,
    name        TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);


CREATE TABLE decks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    is_default  BOOLEAN NOT NULL DEFAULT false,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Constraint: tylko jeden default deck per user
CREATE UNIQUE INDEX uniq_default_deck_per_user
ON decks(owner_id)
WHERE is_default = true;

-- Wymuszenie nazwy default dla default deck
-- Tu NIE robimy tego constraintem (bo SQL CHECK nie ogarnie warunku zależnego od innej kolumny w sensowny sposób), tylko TRIGGEREM
CREATE OR REPLACE FUNCTION enforce_default_deck_name()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_default THEN
        NEW.name := 'default';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_default_deck_name
BEFORE INSERT OR UPDATE ON decks
FOR EACH ROW
EXECUTE FUNCTION enforce_default_deck_name();



CREATE TABLE flashcards (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deck_id     UUID NOT NULL REFERENCES decks(id) ON DELETE CASCADE,
    front_json  JSONB NOT NULL,
    reverse_json JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE flashcard_state (
    flashcard_id   UUID PRIMARY KEY REFERENCES flashcards(id) ON DELETE CASCADE,
    interval       INTEGER NOT NULL,
    ease_factor    NUMERIC(4,2) NOT NULL,
    next_review_at TIMESTAMPTZ NOT NULL,
    last_result    TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- indeks pod spaced repetition
CREATE INDEX idx_flashcard_state_next_review
ON flashcard_state(next_review_at);

CREATE TABLE refresh_tokens (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash   TEXT NOT NULL,
    expires_at   TIMESTAMPTZ NOT NULL,
    revoked_at   TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_refresh_tokens_user
ON refresh_tokens(user_id);

CREATE INDEX idx_refresh_tokens_active
ON refresh_tokens(user_id)
WHERE revoked_at IS NULL;


-- Co backend MUSI robić (minimalny kontrakt)
-- Po rejestracji usera
--      INSERT INTO decks (owner_id, is_default) VALUES (:user_id, true);
-- Przy clone fiszki
--      INSERT do flashcards i opcjonalnie INSERT do flashcard_state
-- Logout 
    -- UPDATE refresh_tokens SET revoked_at = now() WHERE id = :token_id;
