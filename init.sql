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
	admin varchar(500) references utenti(id_user) ON DELETE CASCADE,
	nome_evento varchar(30),
	data varchar(30),
	num_utenti integer NOT NULL DEFAULT 0
	);

create table evento(
	id_evento integer references party(id_evento) ON DELETE CASCADE,
	id_user varchar(500) references utenti(id_user) ON DELETE CASCADE,
	primary key(id_evento, id_user)
	);

create table templateDom(
    name varchar(30) primary key
    );
    
create table attributi(
	id_attributo SERIAL primary key,
	domanda varchar NOT NULL,
	template varchar(30) references templateDom(name),
	id_evento integer references party(id_evento) ON DELETE CASCADE,
	num_risposte integer NOT NULL DEFAULT 0,
	chiusa boolean 
	);

create table risposte(
	id_risposta SERIAL primary key,
	id_attributo integer references attributi(id_attributo) ON DELETE CASCADE,
	num_risposta integer NOT NULL DEFAULT 0,
	max boolean NOT NULL DEFAULT false,
	risposta varchar NOT NULL
	);

create table rispose(
	id_risposta integer references risposte(id_risposta) ON DELETE CASCADE,
	id_attributo integer references attributi(id_attributo) ON DELETE CASCADE,
	id_user varchar(500) references utenti(id_user) ON DELETE CASCADE,
	primary key(id_attributo, id_user)
	);

INSERT INTO templateDom(name) VALUES ('data');
INSERT INTO templateDom(name) VALUES ('oraI');
INSERT INTO templateDom(name) VALUES ('oraE');
insert into templateDom(name) values('luogoI');
insert into templateDom(name) values('luogoE');
INSERT INTO templateDom(name) VALUES ('sino');


/*
CREATE OR REPLACE FUNCTION aggMax() RETURNS TRIGGER AS
$BODY$
DECLARE
numMax INTEGER;
idNumMax INTEGER;
newIdMax INTEGER;
tem VARCHAR;
risp VARCHAR;
BEGIN
	RAISE NOTICE 'entrato in aggMax';
	SELECT num_risposta INTO numMax FROM risposte WHERE id_attributo = NEW.id_attributo and max = true;
	SELECT id_risposta INTO idNumMax FROM risposte WHERE id_attributo = NEW.id_attributo and max = true;
	SELECT template INTO tem FROM attributi WHERE id_attributo = NEW.id_attributo;
	RAISE NOTICE 'numMax % - idNumMax %s',numMax,idNumMax;
	RAISE NOTICE 'new.numrisposta % - new.is_attributo %',NEW.num_risposta, NEW.id_attributo;
	IF idNumMax is NULL OR idNumMax!= NEW.id_risposta THEN
		IF numMax is NULL OR NEW.num_risposta >= numMax THEN
			UPDATE risposte SET max=true WHERE id_risposta=NEW.id_risposta;
			UPDATE risposte SET max=false WHERE id_risposta=idNumMax;
			idNumMax=NEW.id_risposta;
			RAISE NOTICE 'sono entrato max=%',NEW.id_risposta;
		END IF;
	ELSE
		SELECT id_risposta INTO newIdMax FROM risposte NATURAL JOIN attributi WHERE id_attributo=NEW.id_attributo ORDER BY num_risposta DESC LIMIT 1;
		RAISE NOTICE 'sono entrato nellelse newIdMax=%',newIdMax;
		UPDATE risposte SET max=true WHERE id_risposta=newIdMax;
		UPDATE risposte SET max=false WHERE id_risposta=NEW.id_risposta;
		idNumMax=newIdMax;
	END IF;

	IF tem = 'data' THEN
		RAISE NOTICE 'template uguale a data';
		SELECT risposta INTO risp FROM risposte WHERE id_risposta=idNumMax;
		UPDATE party SET data = risp WHERE id_evento IN (SELECT DISTINCT id_evento FROM risposte NATURAL JOIN attributi WHERE id_risposta=idNumMax); 
		RAISE NOTICE 'data aggiornata%',risp;
	END IF;
	RETURN NEW;
END;
$BODY$
LANGUAGE PLPGSQL;
*/

CREATE OR REPLACE FUNCTION aggMax() RETURNS TRIGGER AS
$BODY$
DECLARE
idNumMax INTEGER;
tem VARCHAR;
risp VARCHAR;
BEGIN
	RAISE NOTICE 'entrato in aggMax';
	UPDATE risposte SET max=false WHERE id_attributo= NEW.id_attributo and max=true;
	
	SELECT id_risposta INTO idNumMax FROM risposte WHERE id_attributo=NEW.id_attributo ORDER BY num_risposta DESC LIMIT 1;
	UPDATE risposte SET max=true WHERE id_risposta = idNumMax;
	SELECT template INTO tem FROM risposte NATURAL JOIN attributi WHERE id_risposta = idNumMax;

	IF tem = 'data' THEN
		RAISE NOTICE 'template uguale a data';
		SELECT risposta INTO risp FROM risposte WHERE id_risposta=idNumMax;
		UPDATE party SET data = risp WHERE id_evento IN (SELECT DISTINCT id_evento FROM risposte NATURAL JOIN attributi WHERE id_risposta=idNumMax); 
		RAISE NOTICE 'data aggiornata%',risp;
	END IF;
	RETURN NEW;
END;
$BODY$
LANGUAGE PLPGSQL;

CREATE OR REPLACE FUNCTION aggNumRisposte() RETURNS TRIGGER AS
$BODY$
DECLARE
BEGIN
	UPDATE attributi SET num_risposte=num_risposte+1 WHERE id_attributo=NEW.id_attributo;
	UPDATE risposte SET num_risposta=num_risposta+1 WHERE id_risposta=NEW.id_risposta;
	RETURN NEW;
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

CREATE OR REPLACE FUNCTION aggNumRispostaDEL() RETURNS TRIGGER AS
$BODY$
DECLARE
BEGIN
	RAISE NOTICE 'entrato in aggNumRispostaDEl';
	RAISE NOTICE 'id_risposta %',OLD.id_risposta;
	UPDATE risposte SET num_risposta=num_risposta-1 WHERE id_risposta=OLD.id_risposta;
	UPDATE attributi SET num_risposte=num_risposte-1 WHERE id_attributo=OLD.id_attributo;
	RETURN NEW;
END;
$BODY$
LANGUAGE PLPGSQL;

CREATE OR REPLACE FUNCTION aggNumUtenti() RETURNS TRIGGER AS
$BODY$
DECLARE
BEGIN
	UPDATE party SET num_utenti=num_utenti+1 WHERE id_evento=NEW.id_evento;
	RETURN NULL;
END;
$BODY$
LANGUAGE PLPGSQL;

CREATE OR REPLACE FUNCTION aggNumUtentiDEL() RETURNS TRIGGER AS
$BODY$
DECLARE
BEGIN
	UPDATE party SET num_utenti=num_utenti-1 WHERE id_evento=OLD.id_evento;
	RETURN NULL;
END;
$BODY$
LANGUAGE PLPGSQL;

DROP TRIGGER aggMax ON risposte;
CREATE TRIGGER aggMax AFTER INSERT OR UPDATE OR DELETE ON risposte FOR EACH ROW WHEN (pg_trigger_depth() <= 1) EXECUTE PROCEDURE aggMax();

DROP TRIGGER aggNumRisposte ON rispose;
CREATE TRIGGER aggNumRisposte AFTER INSERT ON rispose FOR EACH ROW WHEN (pg_trigger_depth() = 0) EXECUTE PROCEDURE aggNumRisposte();

DROP TRIGGER aggNumRisposta ON rispose;
CREATE TRIGGER aggNumRisposta BEFORE UPDATE ON rispose FOR EACH ROW WHEN (pg_trigger_depth() = 0) EXECUTE PROCEDURE aggNumRisposta();

DROP TRIGGER aggNumRispostaDEL ON rispose;
CREATE TRIGGER aggNumRispostaDEL AFTER DELETE ON rispose FOR EACH ROW WHEN (pg_trigger_depth() = 0) EXECUTE PROCEDURE aggNumRispostaDEL();

DROP TRIGGER aggNumUtenti ON evento;
CREATE TRIGGER aggNumUtenti AFTER INSERT ON evento FOR EACH ROW WHEN (pg_trigger_depth() = 0) EXECUTE PROCEDURE aggNumUtenti();

DROP TRIGGER aggNumUtentiDEL ON evento;
CREATE TRIGGER aggNumUtentiDEL AFTER DELETE ON evento FOR EACH ROW WHEN (pg_trigger_depth() = 0) EXECUTE PROCEDURE aggNumUtentiDEL();
