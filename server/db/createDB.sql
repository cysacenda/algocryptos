-- Database: algocryptos

-- DROP DATABASE algocryptos;

CREATE DATABASE algocryptos
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

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

-- Table: public.prices

-- DROP TABLE public.prices;

CREATE TABLE public.prices
(
    Symbol character varying(9) COLLATE pg_catalog."default" NOT NULL,
    Rank integer,
    Price_usd double precision,
    Price_btc double precision,
    "24h_volume_usd" double precision,
    Market_cap_usd double precision,
    Percent_change_1h double precision,
    Percent_change_24h double precision,
    Percent_change_7d double precision,
    Last_updated date
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