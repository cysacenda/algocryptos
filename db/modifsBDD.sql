INSERT INTO public.excluded_coins(id_cryptocompare) VALUES (0123456);

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

------------------

drop table IF EXISTS kpi_global_data;
drop table IF EXISTS kpi_global_data_histo;


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


-----------------

insert into process_description (process_name, description) values ('DataImporter -gt', 'Update data related to Google Trend');
insert into process_description (process_name, description) values ('AlgoKPI -gt', 'Calcul kpi related to Google Trend');
insert into process_description (process_name, description) values ('AlgoKPI -g', 'Calcul kpi related to global data');