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
    cur = sql.cursor()
    cur.execute(
        "DELETE FROM evento WHERE id_evento=%s and id_user=%s", (idEvento, idFacebook))
    cur.execute(
        """DELETE FROM rispose
        WHERE id_attributo
        IN (select id_attributo from attributi where id_evento=%s) and id_user=%s""",
        (idEvento, idFacebook))
    sql.commit()


def getAdminOfEvent(idEvento):
    cur = sql.cursor()
    cur.execute("SELECT admin FROM party WHERE id_evento=%s", (idEvento,))
    sql.commit()
    return cur.fetchone()[0]


def getEventName(idEvento):
    cur = sql.cursor()
    cur.execute("SELECT nome_evento FROM party WHERE id_evento=%s", (idEvento,))
    sql.commit()
    return cur.fetchone()[0]


def getAttributoName(idAttributo):
    cur = sql.cursor()
    cur.execute("SELECT domanda FROM attributi WHERE id_attributo=%s", (idAttributo,))
    sql.commit()
    return cur.fetchone()[0]
