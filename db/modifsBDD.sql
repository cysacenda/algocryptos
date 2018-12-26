DROP TABLE public.orders;

CREATE TABLE public.orders
(
    orderId bigint NOT NULL,
    symbol text,
    clientOrderId text,
    transactTime bigint,
    price double precision,
    origQty double precision,
    executedQty double precision,
    cummulativeQuoteQty double precision,
    status text,
    timeInForce text,
    typeorder text,
    side text,
    fills text,
    timestamp timestamp with time zone default current_timestamp
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.orders
    OWNER to postgres;

GRANT ALL ON TABLE public.orders TO dbuser;
GRANT ALL ON TABLE public.orders TO postgres;

COMMENT ON TABLE public.orders
    IS 'Contains one line per order placed by AlgoCryptos';