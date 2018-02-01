-- Table: public.histo_prices

DROP TABLE public.histo_prices;

CREATE TABLE public.histo_prices
(
    "IdCryptoCompare" bigint,
    Symbol character varying(9) COLLATE pg_catalog."default" NOT NULL,
    "Name" text COLLATE pg_catalog."default",
    Price_usd double precision,
    Price_btc double precision,
    "24h_volume_usd" double precision,
    Market_cap_usd double precision,
    "timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.histo_prices
    OWNER to postgres;

GRANT ALL ON TABLE public.histo_prices TO dbuser;
GRANT ALL ON TABLE public.histo_prices TO postgres;

COMMENT ON TABLE public.histo_prices
    IS 'Contains one line per cryptocurency with informations relatives to social networks of the cryptocurrency which are not provided by CryptoCompare and are retrieved manually by us';


-- Table: public.kpi_reddit_subscribers

DROP TABLE public.kpi_reddit_subscribers;

CREATE TABLE public.kpi_reddit_subscribers
(
    "IdCryptoCompare" bigint,
    subscribers_1d_trend double precision,
    subscribers_3d_trend double precision,
    subscribers_7d_trend double precision,
    subscribers_15d_trend double precision,
    subscribers_30d_trend double precision,
    subscribers_60d_trend double precision,
    subscribers_90d_trend double precision,
    "timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.kpi_reddit_subscribers
    OWNER to postgres;

GRANT ALL ON TABLE public.kpi_reddit_subscribers TO dbuser;
GRANT ALL ON TABLE public.kpi_reddit_subscribers TO postgres;

COMMENT ON TABLE public.kpi_reddit_subscribers
    IS 'Contains one line per cryptocurency with kpis on reddit subscribers, store only last kpi calcul';


-- Table: public.kpi_reddit_subscribers

DROP TABLE public.kpi_reddit_subscribers;
CREATE TABLE public.kpi_reddit_subscribers_histo
(
    "IdCryptoCompare" bigint,
    subscribers_1d_trend double precision,
    subscribers_3d_trend double precision,
    subscribers_7d_trend double precision,
    subscribers_15d_trend double precision,
    subscribers_30d_trend double precision,
    subscribers_60d_trend double precision,
    subscribers_90d_trend double precision,
    "timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.kpi_reddit_subscribers_histo
    OWNER to postgres;

GRANT ALL ON TABLE public.kpi_reddit_subscribers_histo TO dbuser;
GRANT ALL ON TABLE public.kpi_reddit_subscribers_histo TO postgres;

COMMENT ON TABLE public.kpi_reddit_subscribers_histo
    IS 'Contains one line per cryptocurency with kpis on reddit subscribers, store all historic of KPI';


-- Table: public.process_params

DROP TABLE public.process_params;
CREATE TABLE public.process_params
(
    "IdProcess" integer NOT NULL,
    "Name" text COLLATE pg_catalog."default",
    "Status" text COLLATE pg_catalog."default",
	"timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.process_params
    OWNER to postgres;

GRANT ALL ON TABLE public.process_params TO dbuser;
GRANT ALL ON TABLE public.process_params TO postgres;

COMMENT ON TABLE public.process_params
    IS 'Allow to avoid some processes to run at the same time';


-- Table: public.histo_ohlcv

DROP TABLE public.histo_volumes;

CREATE TABLE public.histo_ohlcv
(
    "IdCoinCryptoCompare" bigint NOT NULL,
    "open" double precision,
    "high" double precision,
    "low" double precision,
    "close" double precision,
    "volume_aggregated" double precision,
    "timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.histo_ohlcv
    OWNER to postgres;

GRANT ALL ON TABLE public.histo_ohlcv TO dbuser;
GRANT ALL ON TABLE public.histo_ohlcv TO postgres;

COMMENT ON TABLE public.histo_ohlcv
    IS 'Contains one line per cryptocurrency per date per hour with informations on OHLC and the volumes of the cryptocurrency, data comes from CryptoCompare and volumes are calculated on an aggregate of main trading pairs (so it s not the global volume, but we are looking for trends, so ok';
