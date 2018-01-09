-- Database: algocryptos

-- DROP schema public CASCADE
-- DROP DATABASE algocryptos;

CREATE DATABASE algocryptos
    WITH
    OWNER = dbuser
    ENCODING = 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

CREATE SCHEMA public AUTHORIZATION dbuser

-- Table: public.coins

-- DROP TABLE public.coins;

CREATE TABLE public.coins
(
    "IdCryptoCompare" bigint,
    "Name" text COLLATE pg_catalog."default",
    "Symbol" character varying(9) COLLATE pg_catalog."default",
    "CoinName" text COLLATE pg_catalog."default",
    "TotalCoinSupply" text COLLATE pg_catalog."default",
    "SortOrder" integer,
    "ProofType" text COLLATE pg_catalog."default",
    "Algorithm" text COLLATE pg_catalog."default",
    "ImageUrl" text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.coins
    OWNER to postgres;

GRANT ALL ON TABLE public.coins TO dbuser;
GRANT ALL ON TABLE public.coins TO postgres;

-- Table: public.prices

-- DROP TABLE public.prices;

CREATE TABLE public.prices
(
    "IdCryptoCompare" bigint,
    Symbol character varying(9) COLLATE pg_catalog."default" NOT NULL,
    "Name" text COLLATE pg_catalog."default",
    Rank integer,
    Price_usd double precision,
    Price_btc double precision,
    "24h_volume_usd" double precision,
    Market_cap_usd double precision,
    Percent_change_1h double precision,
    Percent_change_24h double precision,
    Percent_change_7d double precision,
    Last_updated timestamp with time zone
    -- CONSTRAINT prices_pkey PRIMARY KEY (Symbol)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.prices
    OWNER to postgres;

GRANT ALL ON TABLE public.prices TO dbuser;
GRANT ALL ON TABLE public.prices TO postgres;

-- Table: public.social_infos

-- DROP TABLE public.social_infos;

CREATE TABLE public.social_infos
(
    "IdCoinCryptoCompare" bigint,
    "Twitter_account_creation" timestamp with time zone,
    "Twitter_name" text COLLATE pg_catalog."default",
    "Twitter_link" text COLLATE pg_catalog."default",
    "Reddit_name" text COLLATE pg_catalog."default",
    "Reddit_link" text COLLATE pg_catalog."default",
    "Reddit_community_creation" timestamp with time zone,
    "Facebook_name" text COLLATE pg_catalog."default",
    "Facebook_link" text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.social_infos
    OWNER to postgres;

GRANT ALL ON TABLE public.social_infos TO dbuser;
GRANT ALL ON TABLE public.social_infos TO postgres;

-- Table: public.social_stats

-- DROP TABLE public.social_stats;

CREATE TABLE public.social_stats
(
    "IdCoinCryptoCompare" bigint,
    "Twitter_followers" bigint,
    "Reddit_posts_per_day" double precision,
    "Reddit_comments_per_day" double precision,
    "Reddit_active_users" bigint,
    "Reddit_subscribers" bigint,
    "Facebook_likes" bigint,
    "Facebook_talking_about" bigint,
    "timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.social_stats
    OWNER to postgres;

GRANT ALL ON TABLE public.social_stats TO dbuser;
GRANT ALL ON TABLE public.social_stats TO postgres;

-- User !
--GRANT ALL ON TABLE public.coins TO dbuser;
--GRANT ALL ON TABLE public.coins TO postgres;