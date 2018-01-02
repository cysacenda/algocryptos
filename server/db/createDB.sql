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
    "IdCryptoCompare" integer,
    "Name" text COLLATE pg_catalog."default",
    "Symbol" character(3) COLLATE pg_catalog."default",
    "CoinName" text COLLATE pg_catalog."default",
    "TotalCoinSupply" bigint,
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