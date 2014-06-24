import psycopg2
import psycopg2.extras
import os

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
