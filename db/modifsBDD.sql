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
insert into process_description ("Name", "Description") values ('DataImporter -ath', 'Update all time high for each cryptocurrency');
insert into process_description ("Name", "Description") values ('AlgoKPI -v', 'Calcul kpi related to volumes');
insert into process_description ("Name", "Description") values ('AlgoKPI -r', 'Calcul kpi related to reddit subscribers');