import psycopg2
import psycopg2.extras

from flask import request
from flask import session
from flask.views import MethodView

#HELPER#
from ..helper import *
#from ..helper.Database import sql


class User(MethodView):

    def post(self):
        if request.form['idCell'] != '' and request.form['username'] != '':

            idCell = request.form['idCell'].strip()
            idFacebook = session['idFacebook']
            username = request.form['username'].strip()

            try:
                cur = sql.cursor()
                cur.execute(
                    "INSERT INTO utenti(id_cell,id_user,username) VALUES(%s,%s,%s)", (idCell, idFacebook, username))
                #cur.execute("SELECT * FROM test;")
                # pg.commit()
                sql.commit()
                #lastId = str(cur.fetchone()[0])

            except Exception, e:
                if isinstance(e, psycopg2.Error):
                    sql.rollback()
                    if e.diag.constraint_name.find('utenti_pkey') != -1:
                        try:
                            cur.execute(
                                "UPDATE utenti SET id_cell = %s WHERE id_user = %s", (idCell, idFacebook))
                            sql.commit()
                        except Exception, e:
                            sql.rollback()
                            return 'error' + str(e)
                        return 'aggiornato'
                return 'error' + str(e)
            finally:
                cur.close()
            return 'fatto'
        else:
            return 'error POST parameters'
