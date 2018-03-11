-- Table: public.social_google_trend

-- DROP TABLE public.social_google_trend;

CREATE TABLE public.social_google_trend
(
    "IdCryptoCompare" bigint,
    "timestamp" timestamp with time zone,
    "value_standalone" double precision,
    "value_compared_to_standard" double precision
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.social_google_trend
    OWNER to postgres;

GRANT ALL ON TABLE public.social_google_trend TO dbuser;
GRANT ALL ON TABLE public.social_google_trend TO postgres;

COMMENT ON TABLE public.social_google_trend
    IS 'Contains data from google trend per cryptocurrency';


-- Add unique constraint in social infos manual

ALTER TABLE social_infos_manual ADD CONSTRAINT id_unique UNIQUE ("IdCoinCryptoCompare");