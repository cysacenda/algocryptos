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