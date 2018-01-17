-- Select tables
select * from coins;
select * from prices;
select * from social_infos;
select * from social_infos_manual;
select * from social_stats;
select * from social_stats_reddit;
select * from histo_volumes;
select * from excluded_coins;

-- Truncate tables
truncate table coins;
truncate table prices;
truncate table social_infos;
truncate table social_infos_manual;
truncate table social_stats;
truncate table social_stats_reddit;
truncate table histo_volumes;
truncate table excluded_coins;

-- Dropdrop tables
drop table coins;
drop table prices;
drop table social_infos;
drop table social_infos_manual;
drop table social_stats;
drop table social_stats_reddit;
drop table histo_volumes;
drop table excluded_coins;

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