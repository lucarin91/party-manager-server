import psycopg2, psycopg2.extras, collections, os

sql = psycopg2.connect(
    database='pm_database',
    user='apipm',
    password='geronsi',
    host='localhost',
) if os.environ['WSGI_ENV']=='deploy.py' else None

def delUtenteFromEvent(idEvento,idFacebook):
    cur = sql.cursor()
    cur.execute("DELETE FROM evento WHERE id_evento=%s and id_user=%s", (idEvento,idFacebook))
    cur.execute("DELETE FROM rispose WHERE id_attributo IN (select id_attributo from attributi where id_evento=%s) and id_user=%s", (idEvento,idFacebook))     
    sql.commit()