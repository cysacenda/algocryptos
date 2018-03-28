-- Select tables
select * from coins;
select * from prices;
select * from social_infos;
select * from social_infos_manual;
select * from social_stats;
select * from social_stats_reddit;
select * from histo_ohlcv;
select * from histo_prices;
select * from excluded_coins;
select * from kpi_reddit_subscribers;
select * from process_params;
select * from top_cryptos;
select * from process_params_histo;
select * from kpi_reddit_subscribers_histo;
select * from global_data;
select * from kpi_market_volumes;
select * from kpi_market_volumes_histo;
select * from social_stats_reddit_histo;
select * from lower_higher_prices;
select * from process_description;


-- Truncate tables = delete en plus violent :p
truncate table coins;
truncate table prices;
truncate table social_infos;
truncate table social_infos_manual;
truncate table social_stats;
truncate table social_stats_reddit;
truncate table histo_ohlcv;
truncate table histo_prices;
truncate table excluded_coins;
truncate table kpi_reddit_subscribers;
truncate table process_params;
truncate table ath_prices;

-- Dropdrop tables
drop table coins;
drop table prices;
drop table social_infos;
drop table social_infos_manual;
drop table social_stats;
drop table social_stats_reddit;
drop table histo_ohlcv;
drop table histo_prices;
drop table excluded_coins;
drop table kpi_reddit_subscribers;
drop table process_params;
drop table top_cryptos;
drop table process_params_histo;
drop table kpi_reddit_subscribers_histo;
drop table global_data;
drop table kpi_market_volumes;
drop table kpi_market_volumes_histo;
drop table social_stats_reddit_histo;
drop table lower_higher_prices;
drop table process_description;

-- Tailles de toutes les tables de la base de données
SELECT *, pg_size_pretty(total_bytes) AS total
    , pg_size_pretty(index_bytes) AS INDEX
    , pg_size_pretty(toast_bytes) AS toast
    , pg_size_pretty(table_bytes) AS TABLE
  FROM (
  SELECT *, total_bytes-index_bytes-COALESCE(toast_bytes,0) AS table_bytes FROM (
      SELECT c.oid,nspname AS table_schema, relname AS TABLE_NAME
              , c.reltuples AS row_estimate
              , pg_total_relation_size(c.oid) AS total_bytes
              , pg_indexes_size(c.oid) AS index_bytes
              , pg_total_relation_size(reltoastrelid) AS toast_bytes
          FROM pg_class c
          LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
          WHERE relkind = 'r'
  ) a
) a;

-- Checker les reddits manquants

SELECT co."Symbol", si."Reddit_name" , sim."Reddit_name" AS Reddit_name_manual FROM social_infos si
INNER JOIN coins co ON si.id_cryptocompare = co.id_cryptocompare
LEFT JOIN social_infos_manual sim ON sim.id_cryptocompare = co.id_cryptocompare
WHERE si."Reddit_name" IS NULL AND sim."Reddit_name" IS NULL;
--WHERE co."Symbol" LIKE 'SALT';