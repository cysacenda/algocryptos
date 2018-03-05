-- DROP TABLE public.process_description;

CREATE TABLE public.process_description
(
    "Name" text COLLATE pg_catalog."default",
    "Description" text COLLATE pg_catalog."default"
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

-------------

insert into process_description ("Name", "Description") values ('DataImporter -cpd', 'Update coins list and prices');
insert into process_description ("Name", "Description") values ('DataImporter -o', 'Update OHLCV information (periods of 1 hour)');
insert into process_description ("Name", "Description") values ('DataImporter -r', 'Update Reddit statistics (number of subscribers)');
insert into process_description ("Name", "Description") values ('DataImporter -g', 'Update global infos (global market cap, 24h volumes)');
insert into process_description ("Name", "Description") values ('DataImporter -s', 'Update social stats (information relatives to twitter, Reddit linked to one cryptocurrency)');
insert into process_description ("Name", "Description") values ('DataImporter -hp', 'Update price historic');
insert into process_description ("Name", "Description") values ('DataImporter -ath', 'Update higher & lower for each cryptocurrency');
insert into process_description ("Name", "Description") values ('AlgoKPI -v', 'Calcul kpi related to volumes');
insert into process_description ("Name", "Description") values ('AlgoKPI -r', 'Calcul kpi related to reddit subscribers');

--------------

-- Table: public.lower_higher_prices

-- DROP TABLE public.lower_higher_prices;

CREATE TABLE public.lower_higher_prices
(
    "IdCryptoCompare" bigint,
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

-----------------

DROP TABLE public.ath_prices;

-----------------

DELETE FROM social_infos_manual WHERE "IdCoinCryptoCompare" = 179896;
INSERT INTO social_infos_manual VALUES (179896,'populous_platform');


-----------------

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
    "timestamp" timestamp with time zone default current_timestamp
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

