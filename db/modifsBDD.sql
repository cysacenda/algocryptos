CREATE TABLE public.top_cryptos
(
    "IdCryptoCompare" bigint
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.top_cryptos
    OWNER to postgres;

GRANT ALL ON TABLE public.top_cryptos TO dbuser;
GRANT ALL ON TABLE public.top_cryptos TO postgres;

COMMENT ON TABLE public.top_cryptos
    IS 'Contains one line per cryptocurrency which are top currencies (usefull for trading pairs count)';

insert into top_cryptos("IdCryptoCompare") values (1182);
insert into top_cryptos("IdCryptoCompare") values (3808);
insert into top_cryptos("IdCryptoCompare") values (5038);
insert into top_cryptos("IdCryptoCompare") values (24854);
insert into top_cryptos("IdCryptoCompare") values (4614);
insert into top_cryptos("IdCryptoCompare") values (5285);
insert into top_cryptos("IdCryptoCompare") values (19745);
insert into top_cryptos("IdCryptoCompare") values (20333);
insert into top_cryptos("IdCryptoCompare") values (27368);
insert into top_cryptos("IdCryptoCompare") values (112392);
insert into top_cryptos("IdCryptoCompare") values (127356);
insert into top_cryptos("IdCryptoCompare") values (171986);
insert into top_cryptos("IdCryptoCompare") values (187440);
insert into top_cryptos("IdCryptoCompare") values (202330);
insert into top_cryptos("IdCryptoCompare") values (236131);
insert into top_cryptos("IdCryptoCompare") values (299774);
insert into top_cryptos("IdCryptoCompare") values (310829);
insert into top_cryptos("IdCryptoCompare") values (321992);
insert into top_cryptos("IdCryptoCompare") values (324068);
insert into top_cryptos("IdCryptoCompare") values (5031);
insert into top_cryptos("IdCryptoCompare") values (7605);
insert into top_cryptos("IdCryptoCompare") values (5324);
insert into top_cryptos("IdCryptoCompare") values (172091);
insert into top_cryptos("IdCryptoCompare") values (347235);
insert into top_cryptos("IdCryptoCompare") values (3807);
insert into top_cryptos("IdCryptoCompare") values (166503);