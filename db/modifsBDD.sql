DROP TABLE public.prices;

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
    Prices_ath_usd double precision,
    Ath_date timestamp with time zone,
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

COMMENT ON TABLE public.prices
    IS 'Contains one line per cryptocurrency, data comes from CoinMarketCap';

