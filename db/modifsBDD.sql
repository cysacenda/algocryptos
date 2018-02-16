CREATE TABLE public.process_params_histo
(
    "IdProcess" integer NOT NULL,
    "Name" text COLLATE pg_catalog."default",
    "Status" text COLLATE pg_catalog."default",
	"timestamp" timestamp with time zone
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.process_params_histo
    OWNER to postgres;

GRANT ALL ON TABLE public.process_params_histo TO dbuser;
GRANT ALL ON TABLE public.process_params_histo TO postgres;

COMMENT ON TABLE public.process_params_histo
    IS 'Historical data of processes with status';