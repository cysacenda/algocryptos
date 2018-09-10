-- Table: public.social_google_trend_1m

-- DROP TABLE public.social_google_trend_1m;

CREATE TABLE public.social_google_trend_1m
(
    id_cryptocompare bigint,
    timestamp timestamp with time zone,
    value_standalone double precision,
    value_compared_to_standard double precision
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.social_google_trend_1m
    OWNER to postgres;

GRANT ALL ON TABLE public.social_google_trend_1m TO dbuser;
GRANT ALL ON TABLE public.social_google_trend_1m TO postgres;

COMMENT ON TABLE public.social_google_trend_1m
    IS 'Contains data from google trend per cryptocurrency 1 month historic';