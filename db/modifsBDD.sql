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
