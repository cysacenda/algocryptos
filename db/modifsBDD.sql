
CREATE TABLE public.ath_prices
(
    "IdCryptoCompare" bigint,
    "Name" text COLLATE pg_catalog."default",
    Prices_ath_usd double precision,
    Ath_date timestamp with time zone,
    Last_updated timestamp with time zone
    -- CONSTRAINT prices_pkey PRIMARY KEY (Symbol)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.ath_prices
    OWNER to postgres;

GRANT ALL ON TABLE public.ath_prices TO dbuser;
GRANT ALL ON TABLE public.ath_prices TO postgres;

COMMENT ON TABLE public.ath_prices
    IS 'Contains one line per cryptocurrency with ATH et ATH date';



