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

COMMENT ON TABLE public.coins
    IS 'Contains one line per cryptocurrency, data comes from Cryptocompare';

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

COMMENT ON TABLE public.prices
    IS 'Contains one line per cryptocurrency, data comes from CoinMarketCap';

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

COMMENT ON TABLE public.social_infos
    IS 'Contains one line per cryptocurrency with informations relatives to social networks of the cryptocurrency, data comes from CryptoCompare';

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


COMMENT ON TABLE public.social_stats
    IS 'Contains one line per cryptocurrency with informations relatives to social networks statistics about the cryptocurrency, data comes from CryptoCompare; For information related to Reddit, use social_stats_reddit table, not this one';

-- User !
--GRANT ALL ON TABLE public.coins TO dbuser;
--GRANT ALL ON TABLE public.coins TO postgres;

-- Table: public.social_stats_reddit

-- DROP TABLE public.social_stats_reddit;

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

GRANT ALL ON TABLE public.social_stats_reddit TO dbuser;
GRANT ALL ON TABLE public.social_stats_reddit TO postgres;


COMMENT ON TABLE public.social_stats_reddit
    IS 'Contains one line per cryptocurrency per date with statistic on th subreddit of the cryptocurrency, data comes from redditmetrics.com (historical data) and reddit.com/subredditname/about.json for real time data';



-- Table: public.histo_volumes

-- DROP TABLE public.histo_volumes;

CREATE TABLE public.histo_volumes
(
    "IdCoinCryptoCompare" bigint NOT NULL,
    "1h_volumes_aggregated_pairs" double precision,
    "timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.histo_volumes
    OWNER to postgres;

GRANT ALL ON TABLE public.histo_volumes TO dbuser;
GRANT ALL ON TABLE public.histo_volumes TO postgres;

COMMENT ON TABLE public.histo_volumes
    IS 'Contains one line per cryptocurrency per date per hour with informations on the volumes of the cryptocurrency, data comes from CryptoCompare and volumes are calculated on an aggregate of main trading pairs (so it s not the global volume, but we are looking for trends, so ok';


-- Table: public.excluded_coins

-- DROP TABLE public.excluded_coins;

CREATE TABLE public.excluded_coins
(
    "IdCoinCryptoCompare" bigint NOT NULL
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
    "IdCoinCryptoCompare" bigint NOT NULL,
    "Reddit_name" text COLLATE pg_catalog."default"
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
