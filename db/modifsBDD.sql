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

--------------
INSERT INTO public.alert_type(
	id_alert_type, global_alert, category_type, filter_type,  trigger_period_hour, description)
	VALUES (1, false, 'price', 'TOP100', '1', '[Crypto Top 100][1h price variation > 10%] #crypto_name# (#crypto_symbol#): #val1_double#%');

