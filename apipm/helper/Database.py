import psycopg2
import psycopg2.extras
import os
from flask import current_app as app

sql = psycopg2.connect(
    database='pm_database',
    user='apipm',
    password='geronsi',
    host='localhost',
) if os.environ['WSGI_ENV'] == 'deploy.py' else None


def delUtenteFromEvent(idEvento, idFacebook):
    try:
        cursore = sql.cursor()
        cursore.execute(
            "DELETE FROM evento WHERE id_evento=%s and id_user=%s", (idEvento, idFacebook))
        cursore.execute(
            """DELETE FROM rispose
            WHERE id_attributo
            IN (select id_attributo from attributi where id_evento=%s) and id_user=%s""",
            (idEvento, idFacebook))
        sql.commit()
    except Exception, e:
        sql.rollback()
        print 'error ' + str(e)
        return 'error ' + str(e)
    finally:
        cursore.close()


def getAdminOfEvent(idEvento):
    try:
        cursore = sql.cursor()
        cursore.execute("SELECT admin FROM party WHERE id_evento=%s", (idEvento,))
        sql.commit()
        return cursore.fetchone()[0]
    except Exception, e:
        sql.rollback()
        print 'error ' + str(e)
        return 'error ' + str(e)
    finally:
        cursore.close()


def getEventName(idEvento):
    try:
        cursore = sql.cursor()
        cursore.execute("SELECT nome_evento FROM party WHERE id_evento=%s", (idEvento,))
        sql.commit()
        return cursore.fetchone()[0]
    except Exception, e:
        sql.rollback()
        print 'error ' + str(e)
        return 'error ' + str(e)
    finally:
        cursore.close()


def getAttributoName(idAttributo):
    try:
        cursore = sql.cursor()
        cursore.execute("SELECT domanda FROM attributi WHERE id_attributo=%s", (idAttributo,))
        sql.commit()
        return cursore.fetchone()[0]
    except Exception, e:
        sql.rollback()
        print 'error ' + str(e)
        return 'error ' + str(e)
    finally:
        cursore.close()


def getRipostaName(idRisposta):
    try:
        cursore = sql.cursor()
        cursore.execute("SELECT risposta FROM risposte WHERE id_risposta=%s", (idRisposta,))
        sql.commit()
        return cursore.fetchone()[0]
    except Exception, e:
        sql.rollback()
        print 'error ' + str(e)
        return 'error ' + str(e)
    finally:
        cursore.close()


def isUserOfEvent(idEvento, idUser):
    try:
        cursore = sql.cursor()
        cursore.execute(
            "SELECT id_user FROM evento WHERE id_evento=%s and id_user=%s", (idEvento, idUser))
        sql.commit()
        ris = cursore.fetchone()[0]
        print 'isUserOfEvent: ' + str(ris)
        return True if ris is not None else False
    except Exception, e:
        sql.rollback()
        print 'error ' + str(e)
        return 'error ' + str(e)
    finally:
        cursore.close()


def isUserOfAttributo(idAttributo, idUser):
    try:
        cursore = sql.cursor()
        cursore.execute(
            "SELECT id_user FROM evento NATURAL JOIN attributi WHERE id_attributo=%s and id_user=%s", (idAttributo, idUser))
        sql.commit()
        ris = cursore.fetchone()[0]
        print 'isUserOfEAttributo: ' + str(ris)
        return True if ris is not None else False
    except Exception, e:
        sql.rollback()
        print 'error ' + str(e)
        return 'error ' + str(e)
    finally:
        cursore.close()


def isUserOfRisposta(idRisposta, idUser):
    try:
        cursore = sql.cursor()
        cursore.execute(
            "SELECT id_user FROM evento NATURAL JOIN attributi NATURAL JOIN risposte WHERE id_risposta=%s and id_user=%s", (idRisposta, idUser))
        sql.commit()
        ris = cursore.fetchone()[0]
        print 'isUserOfRisposta: ' + str(ris)
        return True if ris is not None else False
    except Exception, e:
        sql.rollback()
        print 'error ' + str(e)
        return 'error ' + str(e)
    finally:
        cursore.close()


def getTemplateOfAttributo(idAttributo):
    try:
        cur = sql.cursor()
        cur.execute("""SELECT template
                       FROM attributi
                       WHERE id_attributo=%s""",
                    (idAttributo,))
        sql.commit()
        return cur.fetchone()[0]
    except Exception, e:
        sql.rollback()
        print 'error ' + str(e)
        return 'error ' + str(e)
    finally:
        cur.close()


def isAttributoChiuso(idAttributo):
    try:
        cur = sql.cursor()
        cur.execute("""SELECT chiusa
                       FROM attributi
                       WHERE id_attributo=%s""",
                    (idAttributo,))
        sql.commit()
        return cur.fetchone()[0]
    except Exception, e:
        sql.rollback()
        print 'error ' + str(e)
        return 'error ' + str(e)
    finally:
        cur.close()


def getTemplateList():
    try:
        cur = sql.cursor()
        cur.execute("SELECT array(SELECT name FROM templateDom)")
        sql.commit()
        return cur.fetchall()[0][0]
    except Exception, e:
        sql.rollback()
        print 'error ' + str(e)
        return 'error ' + str(e)
    finally:
        cur.close()


def getNumUtentiEvent(idEvento):
    try:
        cur = sql.cursor()
        cur.execute("SELECT num_utenti from party where id_evento=%s", (idEvento,))
        sql.commit()
        return cur.fetchall()[0]
    except Exception, e:
        sql.rollback()
        print 'error ' + str(e)
        return 'error ' + str(e)
    finally:
        cur.close()
        