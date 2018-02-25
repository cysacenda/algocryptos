CREATE TABLE public.process_params_histo
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

ALTER TABLE public.process_params_histo
    OWNER to postgres;

GRANT ALL ON TABLE public.process_params_histo TO dbuser;
GRANT ALL ON TABLE public.process_params_histo TO postgres;

COMMENT ON TABLE public.process_params_histo
    IS 'Historical data of processes with status';

------------

ALTER TABLE social_infos_manual ADD COLUMN "Twitter_link" text COLLATE pg_catalog."default";
ALTER TABLE social_infos_manual ADD COLUMN "Facebook_link" text COLLATE pg_catalog."default";


--------------

CREATE INDEX social_stats_reddit_histo_index
ON social_stats_reddit_histo ("IdCoinCryptoCompare");

--------------

ALTER TABLE social_stats_reddit RENAME TO social_stats_reddit_histo;


--------------

CREATE TABLE public.social_stats_reddit
(
    "IdCoinCryptoCompare" bigint,
    "Reddit_subscribers" bigint,
    "Reddit_active_users" bigint,
    "timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.social_stats_reddit
    OWNER to postgres;

CREATE INDEX social_stats_reddit_index
ON social_stats_reddit ("IdCoinCryptoCompare");

GRANT ALL ON TABLE public.social_stats_reddit TO dbuser;
GRANT ALL ON TABLE public.social_stats_reddit TO postgres;


COMMENT ON TABLE public.social_stats_reddit
    IS 'Contains one line per cryptocurrency per date with statistic on th subreddit of the cryptocurrency, data comes from redditmetrics.com (historical data) and reddit.com/subredditname/about.json for real time data';

--------------------

-- DROP TABLE public.global_data;

CREATE TABLE public.global_data
(
    total_market_cap_usd double precision,
    total_24h_volume_usd double precision,
    bitcoin_percentage_of_market_cap double precision,
    "timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.global_data
    OWNER to postgres;

GRANT ALL ON TABLE public.global_data TO dbuser;
GRANT ALL ON TABLE public.global_data TO postgres;

COMMENT ON TABLE public.global_data
    IS 'Contains global data from CMC like global market cap etc.';

--------------------

DELETE FROM histo_ohlcv;

--------------------


-- DROP TABLE public.kpi_market_volumes;

CREATE TABLE public.kpi_market_volumes
(
    "IdCoinCryptoCompare" bigint,
    "volume_mean_last_1h_vs_30d" double precision,
    "volume_mean_last_3h_30d" double precision,
    "volume_mean_last_6h_30d" double precision,
    "volume_mean_last_12h_30d" double precision,
    "volume_mean_last_24h_30d" double precision,
    "volume_mean_last_3d_30d" double precision,
    "volume_mean_last_7d_30d" double precision,
    "timestamp" timestamp with time zone default current_timestamp
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.kpi_market_volumes
    OWNER to postgres;

GRANT ALL ON TABLE public.kpi_market_volumes TO dbuser;
GRANT ALL ON TABLE public.kpi_market_volumes TO postgres;

COMMENT ON TABLE public.kpi_market_volumes
    IS 'Contains market kpis about volumes.';

