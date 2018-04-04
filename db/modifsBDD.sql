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