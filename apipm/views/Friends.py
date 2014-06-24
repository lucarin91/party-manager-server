import psycopg2
import psycopg2.extras
import json

from flask import request
from flask import jsonify
from flask import session
from flask.views import MethodView

#HELPER#
from ..helper import *
#from ..helper.Database import sql


class Friends(MethodView):

    def get(self, idEvento):
        try:
            cur = sql.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                "SELECT id_user, username from utenti natural join evento where id_evento=%s", (idEvento,))
            sql.commit()
            utenti = cur.fetchall()
            for u in utenti:
                u['name'] = getFacebookName(u['id_user'])

            return jsonify(results=utenti)
        except Exception, e:
            sql.rollback()
            return 'error ' + str(e)
        finally:
            cur.close()

    def post(self, idEvento):
        if request.form['userList'] != '':
            try:
                user = session['idFacebook']
                userList = json.loads(request.form['userList'].strip())
            except Exception, e:
                return 'json parser error'

            try:
                cur = sql.cursor()
                for u in userList:
                    cur.execute(
                        "INSERT INTO evento(id_evento, id_user) VALUES(%s,%s)", (idEvento, u))
                sql.commit()

                sendNotificationEvent(idEvento,
                                      user,
                                      {'type': CODE['addFriends'],
                                       'id_evento': idEvento,
                                       'nome_evento': Database.getEventName(idEvento),
                                       'user_list': Facebook.getFacebookName(userList)})
                return 'fatto'

            except Exception, e:
                sql.rollback()
                print 'error ' + str(e)
                return 'error ' + str(e)
            finally:
                cur.close()
        else:
            return 'POST parameter error'

    def delete(self, idEvento, idFacebook):
        try:
            user = session['idFacebook']
            admin = Database.getAdminOfEvent(idEvento)
            if admin == user:
                Database.delUtenteFromEvent(idEvento, idFacebook)

                sendNotificationEvent(idEvento,
                                      user,
                                      {'type': CODE['delFriends'],
                                       'id_evento': str(idEvento),
                                       'nome_evento': Database.getEventName(idEvento),
                                       'admin_name': getFacebookName(admin),
                                       'id_user': idFacebook,
                                       'user_name': getFacebookName(idFacebook)})

                return 'fatto'
            else:
                return 'error no amministratore'

        except Exception, e:
            print 'error ' + str(e)
            return 'error ' + str(e)
