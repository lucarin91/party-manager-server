DROP TABLE IF EXISTS utenti cascade;
DROP TABLE IF EXISTS party cascade;
DROP TABLE IF EXISTS evento cascade;
DROP TABLE IF EXISTS risposte cascade;
DROP TABLE IF EXISTS attributi cascade;
DROP TABLE IF EXISTS rispose cascade;
DROP TABLE IF EXISTS templateDom cascade;

create table utenti(
    /*id_user SERIAL primary key,*/
    id_cell varchar(500) unique NOT NULL ,
    id_user varchar(500) primary key ,
    username varchar(30),
    position varchar
	);

create table party(
	id_evento SERIAL primary key,
	admin varchar(500) references utenti(id_user),
	nome_evento varchar(30),
	data varchar(30),
	num_utenti integer NOT NULL
	);

create table evento(
	id_evento integer references party(id_evento),
	id_user varchar(500) references utenti(id_user),
	primary key(id_evento, id_user)
	);

create table templateDom(
    name varchar(30) primary key
    );
    
create table attributi(
	id_attributo SERIAL primary key,
	domanda varchar NOT NULL,
	template varchar(30) references templateDom(name),
	id_evento integer references party(id_evento) NOT NULL,
	num_risposte integer NOT NULL DEFAULT 0,
	chiusa boolean 
	);

create table risposte(
	id_risposta SERIAL primary key,
	id_attributo integer references attributi(id_attributo),
	num_risposta integer NOT NULL DEFAULT 0,
	max boolean NOT NULL DEFAULT false,
	risposta varchar NOT NULL
	);

create table rispose(
	id_risposta integer references risposte(id_risposta),
	id_attributo integer references attributi(id_attributo),
	id_user varchar(500) references utenti(id_user),
	primary key(id_attributo, id_user)
	);

INSERT INTO templateDom(name) VALUES ('data');
INSERT INTO templateDom(name) VALUES ('oraI');
INSERT INTO templateDom(name) VALUES ('oraE');
insert into templateDom(name) values('luogoI');
insert into templateDom(name) values('luogoE');
INSERT INTO templateDom(name) VALUES ('sino');



CREATE OR REPLACE FUNCTION aggMax() RETURNS TRIGGER AS
$BODY$
DECLARE
numMax INTEGER;
idNumMax INTEGER;
BEGIN
	SELECT num_risposta INTO numMax FROM risposte WHERE id_attributo = NEW.id_attributo and max = true;
	SELECT id_risposta INTO idNumMax FROM risposte WHERE id_attributo = NEW.id_attributo and max = true;
	IF numMax IS NULL OR NEW.num_risposta >= numMax THEN
		UPDATE risposte SET max=true WHERE id_risposta=NEW.id_risposta;
		UPDATE risposte SET max=false WHERE id_risposta=idNumMax;
	END IF;
	RETURN NULL;
END;
$BODY$
LANGUAGE PLPGSQL;

CREATE OR REPLACE FUNCTION aggNumRisposte() RETURNS TRIGGER AS
$BODY$
DECLARE
BEGIN
	UPDATE attributi SET num_risposte=num_risposte+1 WHERE id_attributo=NEW.id_attributo;
	UPDATE risposte SET num_risposta=num_risposta+1 WHERE id_risposta=NEW.id_risposta;
	RETURN NULL;
END;
$BODY$
LANGUAGE PLPGSQL;

CREATE OR REPLACE FUNCTION aggNumRisposta() RETURNS TRIGGER AS
$BODY$
DECLARE
BEGIN
	UPDATE risposte SET num_risposta=num_risposta-1 WHERE id_risposta=OLD.id_risposta;
	UPDATE risposte SET num_risposta=num_risposta+1 WHERE id_risposta=NEW.id_risposta;
	RETURN NEW;
END;
$BODY$
LANGUAGE PLPGSQL;


DROP TRIGGER aggMax ON risposte;
CREATE TRIGGER aggMax AFTER INSERT OR UPDATE ON risposte FOR EACH ROW WHEN (pg_trigger_depth() = 0) EXECUTE PROCEDURE aggMax();

DROP TRIGGER aggNumRisposte ON rispose;
CREATE TRIGGER aggNumRisposte AFTER INSERT ON rispose FOR EACH ROW WHEN (pg_trigger_depth() = 0) EXECUTE PROCEDURE aggNumRisposte();

DROP TRIGGER aggNumRisposta ON rispose;
CREATE TRIGGER aggNumRisposta BEFORE UPDATE ON rispose FOR EACH ROW WHEN (pg_trigger_depth() = 0) EXECUTE PROCEDURE aggNumRisposta();

/*materiale d'esempio*/
/*
insert into utenti(id_cell,id_Facebook) values('id_cell', '1738252551');
insert into utenti(id_cell,id_Facebook) values('id_cell', '1203476294');

insert into party(admin,nome_evento, data, num_utenti) values('1738252551', 'prova1', '23/03/2014', '2');

*/