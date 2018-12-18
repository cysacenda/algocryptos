-- Table: public.coins

-- DROP TABLE public.coins;

CREATE TABLE public.coins
(
    id_cryptocompare bigint,
    crypto_name text COLLATE pg_catalog."default",
    symbol varchar(20) COLLATE pg_catalog."default",
    coin_name text COLLATE pg_catalog."default",
    total_coin_supply text COLLATE pg_catalog."default",
    sort_order integer,
    proof_type text COLLATE pg_catalog."default",
    algorithm text COLLATE pg_catalog."default",
    image_url text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.coins
    OWNER to postgres;

GRANT ALL ON TABLE public.coins TO dbuser;
GRANT ALL ON TABLE public.coins TO postgres;

COMMENT ON TABLE public.coins
    IS 'Contains one line per cryptocurrency, data comes from Cryptocompare';

-- Table: public.prices

-- DROP TABLE public.prices;

CREATE TABLE public.prices
(
    id_cryptocompare bigint,
    symbol varchar(20) COLLATE pg_catalog."default" NOT NULL,
    crypto_name text COLLATE pg_catalog."default",
    crypto_rank integer,
    price_usd double precision,
    price_btc double precision,
    volume_usd_24h double precision,
    market_cap_usd double precision,
    percent_change_1h double precision,
    percent_change_24h double precision,
    percent_change_7d double precision,
    available_supply double precision,
    last_updated timestamp with time zone
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

-- Table: public.social_infos

-- DROP TABLE public.social_infos;

CREATE TABLE public.social_infos
(
    id_cryptocompare bigint,
    twitter_account_creation timestamp with time zone,
    twitter_name text COLLATE pg_catalog."default",
    twitter_link text COLLATE pg_catalog."default",
    reddit_name text COLLATE pg_catalog."default",
    reddit_link text COLLATE pg_catalog."default",
    reddit_community_creation timestamp with time zone,
    facebook_name text COLLATE pg_catalog."default",
    facebook_link text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.social_infos
    OWNER to postgres;

GRANT ALL ON TABLE public.social_infos TO dbuser;
GRANT ALL ON TABLE public.social_infos TO postgres;

COMMENT ON TABLE public.social_infos
    IS 'Contains one line per cryptocurrency with informations relatives to social networks of the cryptocurrency, data comes from CryptoCompare';

-- Table: public.social_stats

-- DROP TABLE public.social_stats;

CREATE TABLE public.social_stats
(
    id_cryptocompare bigint,
    twitter_followers bigint,
    reddit_posts_per_day double precision,
    reddit_comments_per_day double precision,
    reddit_active_users bigint,
    reddit_subscribers bigint,
    facebook_likes bigint,
    facebook_talking_about bigint,
    timestamp timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.social_stats
    OWNER to postgres;

GRANT ALL ON TABLE public.social_stats TO dbuser;
GRANT ALL ON TABLE public.social_stats TO postgres;


COMMENT ON TABLE public.social_stats
    IS 'Contains one line per cryptocurrency with informations relatives to social networks statistics about the cryptocurrency, data comes from CryptoCompare; For information related to Reddit, use social_stats_reddit table, not this one';


-- Table: public.social_stats_reddit

-- DROP TABLE public.social_stats_reddit;

CREATE TABLE public.social_stats_reddit
(
    id_cryptocompare bigint,
    reddit_subscribers bigint,
    reddit_active_users bigint,
    timestamp timestamp with time zone
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

-- Table: public.histo_ohlcv

-- DROP TABLE public.histo_ohlcv;

CREATE TABLE public.histo_ohlcv
(
    id_cryptocompare bigint NOT NULL,
    open_price double precision,
    high_price double precision,
    low_price double precision,
    close_price double precision,
    volume_aggregated double precision,
    timestamp timestamp with time zone
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
    IS 'Contains one line per cryptocurrency per date per hour with informations on OHLC and the volumes of the cryptocurrency, data comes from CryptoCompare and volumes are calculated on an aggregate of main algo pairs (so it s not the global volume, but we are looking for trends, so ok';


-- Table: public.excluded_coins

-- DROP TABLE public.excluded_coins;

CREATE TABLE public.excluded_coins
(
    id_cryptocompare bigint NOT NULL
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.excluded_coins
    OWNER to postgres;

GRANT ALL ON TABLE public.excluded_coins TO dbuser;
GRANT ALL ON TABLE public.excluded_coins TO postgres;

COMMENT ON TABLE public.excluded_coins
    IS 'This table contains the list of cryptocurrencies we want to exclude from the tool - inactive, useless, etc.';


-- Table: public.social_infos_manual

-- DROP TABLE public.social_infos_manual;

CREATE TABLE public.social_infos_manual
(
    id_cryptocompare bigint NOT NULL,
    reddit_name text COLLATE pg_catalog."default",
    twitter_link text COLLATE pg_catalog."default",
    facebook_link text COLLATE pg_catalog."default",
    CONSTRAINT id_unique UNIQUE (id_cryptocompare)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.social_infos_manual
    OWNER to postgres;

GRANT ALL ON TABLE public.social_infos_manual TO dbuser;

GRANT ALL ON TABLE public.social_infos_manual TO postgres;

COMMENT ON TABLE public.social_infos_manual
    IS 'Contains one line per cryptocurrency with informations relatives to social networks of the cryptocurrency which are not provided by CryptoCompare and are retrieved manually by us';


-- Table: public.histo_prices

-- DROP TABLE public.histo_prices;

CREATE TABLE public.histo_prices
(
    id_cryptocompare bigint,
    symbol varchar(20) COLLATE pg_catalog."default" NOT NULL,
    crypto_name text COLLATE pg_catalog."default",
    price_usd double precision,
    price_btc double precision,
    volume_usd_24h double precision,
    market_cap_usd double precision,
    timestamp timestamp with time zone
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

-- DROP TABLE public.kpi_reddit_subscribers;

CREATE TABLE public.kpi_reddit_subscribers
(
    id_cryptocompare bigint,
    subscribers_1d_trend double precision,
    subscribers_3d_trend double precision,
    subscribers_7d_trend double precision,
    subscribers_15d_trend double precision,
    subscribers_30d_trend double precision,
    subscribers_60d_trend double precision,
    subscribers_90d_trend double precision,
    timestamp timestamp with time zone default current_timestamp
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

-- DROP TABLE public.kpi_reddit_subscribers;

ALTER TABLE public.kpi_reddit_subscribers_histo RENAME COLUMN "IdCryptoCompare" TO id_cryptocompare;
ALTER TABLE public.kpi_reddit_subscribers_histo RENAME COLUMN "timestamp" TO timestamp;

CREATE TABLE public.kpi_reddit_subscribers_histo
(
    id_cryptocompare bigint,
    subscribers_1d_trend double precision,
    subscribers_3d_trend double precision,
    subscribers_7d_trend double precision,
    subscribers_15d_trend double precision,
    subscribers_30d_trend double precision,
    subscribers_60d_trend double precision,
    subscribers_90d_trend double precision,
    timestamp timestamp with time zone
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

-- DROP TABLE public.process_params;
CREATE TABLE public.process_params
(
    process_id integer NOT NULL,
    process_name text COLLATE pg_catalog."default",
    status text COLLATE pg_catalog."default",
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

-- Table: public.top_cryptos

-- DROP TABLE public.top_cryptos;

CREATE TABLE public.top_cryptos
(
    id_cryptocompare bigint
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.top_cryptos
    OWNER to postgres;

GRANT ALL ON TABLE public.top_cryptos TO dbuser;
GRANT ALL ON TABLE public.top_cryptos TO postgres;

COMMENT ON TABLE public.top_cryptos
    IS 'Contains one line per cryptocurrency which are top currencies (usefull for algo pairs count)';


-- Table: public.process_params_histo

-- DROP TABLE public.process_params_histo;
CREATE TABLE public.process_params_histo
(
    process_id integer NOT NULL,
    process_name text COLLATE pg_catalog."default",
    status text COLLATE pg_catalog."default",
	timestamp timestamp with time zone
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

-- Table: public.social_stats_reddit_histo

-- DROP TABLE public.social_stats_reddit_histo;

CREATE TABLE public.social_stats_reddit_histo
(
    id_cryptocompare bigint,
    reddit_subscribers bigint,
    reddit_active_users bigint,
    timestamp timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.social_stats_reddit_histo
    OWNER to postgres;

CREATE INDEX social_stats_reddit_histo_index
ON social_stats_reddit_histo ("IdCoinCryptoCompare");

GRANT ALL ON TABLE public.social_stats_reddit_histo TO dbuser;
GRANT ALL ON TABLE public.social_stats_reddit_histo TO postgres;

COMMENT ON TABLE public.social_stats_reddit_histo
    IS 'Contains one line per cryptocurrency per date with statistic on th subreddit of the cryptocurrency, data comes from redditmetrics.com (historical data) and reddit.com/subredditname/about.json for real time data';


-- Table: public.global_data

-- DROP TABLE public.global_data;

CREATE TABLE public.global_data
(
    total_market_cap_usd double precision,
    total_24h_volume_usd double precision,
    bitcoin_percentage_of_market_cap double precision,
    timestamp timestamp with time zone
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



-- Table: public.kpi_market_volumes;

-- DROP TABLE public.kpi_market_volumes;

CREATE TABLE public.kpi_market_volumes
(
    id_cryptocompare bigint,
    volume_mean_last_1h_vs_30d double precision,
    volume_mean_last_3h_30d double precision,
    volume_mean_last_6h_30d double precision,
    volume_mean_last_12h_30d double precision,
    volume_mean_last_24h_30d double precision,
    volume_mean_last_3d_30d double precision,
    volume_mean_last_7d_30d double precision,
    timestamp timestamp with time zone default current_timestamp
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



-- Table: public.kpi_market_volumes_histo;

-- DROP TABLE public.kpi_market_volumes_histo;

CREATE TABLE public.kpi_market_volumes_histo
(
    id_cryptocompare bigint,
    volume_mean_last_1h_vs_30d double precision,
    volume_mean_last_3h_30d double precision,
    volume_mean_last_6h_30d double precision,
    volume_mean_last_12h_30d double precision,
    volume_mean_last_24h_30d double precision,
    volume_mean_last_3d_30d double precision,
    volume_mean_last_7d_30d double precision,
    timestamp timestamp with time zone default current_timestamp
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.kpi_market_volumes_histo
    OWNER to postgres;

GRANT ALL ON TABLE public.kpi_market_volumes_histo TO dbuser;
GRANT ALL ON TABLE public.kpi_market_volumes_histo TO postgres;

COMMENT ON TABLE public.kpi_market_volumes_histo
    IS 'Contains historical data of market kpis about volumes.';

-- Table : public.process_description;

-- DROP TABLE public.process_description;

CREATE TABLE public.process_description
(
    process_name text COLLATE pg_catalog."default",
    description text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.process_description
    OWNER to postgres;

GRANT ALL ON TABLE public.process_description TO dbuser;
GRANT ALL ON TABLE public.process_description TO postgres;

COMMENT ON TABLE public.process_description
    IS 'Contains description of processes.';



-- Table: public.lower_higher_prices

-- DROP TABLE public.lower_higher_prices;

CREATE TABLE public.lower_higher_prices
(
    id_cryptocompare bigint,
    price_low_15d double precision,
    date_low_15d timestamp with time zone,
    price_low_1m double precision,
    date_low_1m timestamp with time zone,
    price_low_3m double precision,
    date_low_3m timestamp with time zone,
    price_low_6m double precision,
    date_low_6m timestamp with time zone,
    price_low_1y double precision,
    date_low_1y timestamp with time zone,
    price_low_5y double precision,
    date_low_5y timestamp with time zone,
    price_high_15d double precision,
    date_high_15d timestamp with time zone,
    price_high_1m double precision,
    date_high_1m timestamp with time zone,
    price_high_3m double precision,
    date_high_3m timestamp with time zone,
    price_high_6m double precision,
    date_high_6m timestamp with time zone,
    price_high_1y double precision,
    date_high_1y timestamp with time zone,
    price_high_5y double precision,
    date_high_5y timestamp with time zone,
    timestamp timestamp with time zone default current_timestamp
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.lower_higher_prices
    OWNER to postgres;

GRANT ALL ON TABLE public.lower_higher_prices TO dbuser;
GRANT ALL ON TABLE public.lower_higher_prices TO postgres;

COMMENT ON TABLE public.lower_higher_prices
    IS 'Contains one line per cryptocurrency with lowers and highers on different periods';

-- Table: public.social_google_trend

-- DROP TABLE public.social_google_trend;

CREATE TABLE public.social_google_trend
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

ALTER TABLE public.social_google_trend
    OWNER to postgres;

GRANT ALL ON TABLE public.social_google_trend TO dbuser;
GRANT ALL ON TABLE public.social_google_trend TO postgres;

COMMENT ON TABLE public.social_google_trend
    IS 'Contains data from google trend per cryptocurrency 5 years historic';


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

-- Table: public.kpi_global_data

-- DROP TABLE public.kpi_global_data;

CREATE TABLE public.kpi_global_data
(
    global_market_cap_24h_pctchange double precision,
    timestamp timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.kpi_global_data
    OWNER to postgres;

GRANT ALL ON TABLE public.kpi_global_data TO dbuser;
GRANT ALL ON TABLE public.kpi_global_data TO postgres;

COMMENT ON TABLE public.kpi_global_data
    IS 'Contains calculated kpi on global data.';



-- Table: public.kpi_global_data_histo

-- DROP TABLE public.kpi_global_data_histo;

CREATE TABLE public.kpi_global_data_histo
(
    global_market_cap_24h_pctchange double precision,
    timestamp timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.kpi_global_data_histo
    OWNER to postgres;

GRANT ALL ON TABLE public.kpi_global_data_histo TO dbuser;
GRANT ALL ON TABLE public.kpi_global_data_histo TO postgres;

COMMENT ON TABLE public.kpi_global_data_histo
    IS 'Contains calculated kpi on global data (historical table).';




-- Table: public.kpi_global_data_volumes

-- DROP TABLE public.kpi_global_data_volumes;

CREATE TABLE public.kpi_global_data_volumes
(
    volume_mean_last_1h_vs_30d double precision,
    volume_mean_last_3h_30d double precision,
    volume_mean_last_6h_30d double precision,
    volume_mean_last_12h_30d double precision,
    volume_mean_last_24h_30d double precision,
    volume_mean_last_3d_30d double precision,
    volume_mean_last_7d_30d double precision,
    timestamp timestamp with time zone default current_timestamp
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.kpi_global_data_volumes
    OWNER to postgres;

GRANT ALL ON TABLE public.kpi_global_data_volumes TO dbuser;
GRANT ALL ON TABLE public.kpi_global_data_volumes TO postgres;

COMMENT ON TABLE public.kpi_global_data_volumes
    IS 'Contains calculated kpi on global data volumes.';



-- Table: public.kpi_global_data_volumes_histo

-- DROP TABLE public.kpi_global_data_volumes_histo;

CREATE TABLE public.kpi_global_data_volumes_histo
(
    volume_mean_last_1h_vs_30d double precision,
    volume_mean_last_3h_30d double precision,
    volume_mean_last_6h_30d double precision,
    volume_mean_last_12h_30d double precision,
    volume_mean_last_24h_30d double precision,
    volume_mean_last_3d_30d double precision,
    volume_mean_last_7d_30d double precision,
    timestamp timestamp with time zone default current_timestamp
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.kpi_global_data_volumes_histo
    OWNER to postgres;

GRANT ALL ON TABLE public.kpi_global_data_volumes_histo TO dbuser;
GRANT ALL ON TABLE public.kpi_global_data_volumes_histo TO postgres;

COMMENT ON TABLE public.kpi_global_data_volumes_histo
    IS 'Contains calculated kpi on global data volumes (historical table).';



-- Table: public.kpi_googletrend

-- DROP TABLE public.kpi_googletrend;
CREATE TABLE public.kpi_googletrend
(
    id_cryptocompare bigint,
    search_1d_trend double precision,
    search_3d_trend double precision,
    search_7d_trend double precision,
    search_15d_trend double precision,
    search_1m_trend double precision,
    timestamp timestamp with time zone default current_timestamp
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.kpi_googletrend
    OWNER to postgres;

GRANT ALL ON TABLE public.kpi_googletrend TO dbuser;
GRANT ALL ON TABLE public.kpi_googletrend TO postgres;


-- Table: public.kpi_googletrend_histo

-- DROP TABLE public.kpi_googletrend_histo;
CREATE TABLE public.kpi_googletrend_histo
(
    id_cryptocompare bigint,
    search_1d_trend double precision,
    search_3d_trend double precision,
    search_7d_trend double precision,
    search_15d_trend double precision,
    search_1m_trend double precision,
    timestamp timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.kpi_googletrend_histo
    OWNER to postgres;

GRANT ALL ON TABLE public.kpi_googletrend_histo TO dbuser;
GRANT ALL ON TABLE public.kpi_googletrend_histo TO postgres;




-- Table: public.alerts

-- DROP TABLE public.alerts;
CREATE TABLE public.alerts
(
    id_cryptocompare bigint,
    id_alert_type integer,
    val1_double double precision,
    val2_double double precision,
    timestamp timestamp with time zone default current_timestamp
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.alerts
    OWNER to postgres;

GRANT ALL ON TABLE public.alerts TO dbuser;
GRANT ALL ON TABLE public.alerts TO postgres;


-- Table: public.alert_type

-- DROP TABLE public.alert_type;
CREATE TABLE public.alert_type
(
    id_alert_type integer,
    global_alert boolean, --for one crypto FALSE or all cryptos TRUE
    category_type varchar(20), --price, volume, etc.
    filter_type varchar(20), --TOP100, ALL, etc.
    trigger_period_hour integer, -- 1H, 12H, 24H
    description text
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.alert_type
    OWNER to postgres;

GRANT ALL ON TABLE public.alert_type TO dbuser;
GRANT ALL ON TABLE public.alert_type TO postgres;


-- Table: public.histo_ohlcv_old

-- DROP TABLE public.histo_ohlcv_old;

CREATE TABLE public.histo_ohlcv_old
(
    id_cryptocompare bigint NOT NULL,
    open_price double precision,
    high_price double precision,
    low_price double precision,
    close_price double precision,
    volume_crypto double precision,
    volume_usd double precision,
    timestamp timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.histo_ohlcv_old
    OWNER to postgres;

GRANT ALL ON TABLE public.histo_ohlcv_old TO dbuser;
GRANT ALL ON TABLE public.histo_ohlcv_old TO postgres;

COMMENT ON TABLE public.histo_ohlcv_old
    IS 'Contains one line per cryptocurrency per day with informations on OHLC and the volumes of the cryptocurrency, data comes from CryptoCompare and volumes are USD only. The goal is to have data for technical analysis before Dec 2017';
