-- Create the `news_updates` table
CREATE TABLE IF NOT EXISTS public.news_updates (
    id SERIAL PRIMARY KEY,
    headline TEXT,
    summary TEXT,
    author TEXT,
    content TEXT,
    symbols TEXT[],
    source TEXT,
    url TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ
);

-- Drop any existing primary key constraint, if any
ALTER TABLE public.news_updates
    DROP CONSTRAINT IF EXISTS news_updates_pkey;

-- Ensure the sequence for the ID column
CREATE SEQUENCE IF NOT EXISTS public.news_updates_id_seq
    AS INTEGER
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.news_updates_id_seq OWNED BY public.news_updates.id;

ALTER TABLE ONLY public.news_updates 
    ALTER COLUMN id SET DEFAULT nextval('public.news_updates_id_seq'::regclass);

-- Add a primary key constraint on (id, created_at) for time-series optimization
ALTER TABLE public.news_updates 
    ADD CONSTRAINT pk_news PRIMARY KEY (id, created_at);

-- Add an index on `created_at` for faster time-series queries
CREATE INDEX IF NOT EXISTS news_updates_created_at_idx 
    ON public.news_updates USING btree (created_at DESC);

-- Convert the table into a hypertable (TimescaleDB feature)
SELECT create_hypertable('news_updates', 'created_at', if_not_exists => TRUE);

