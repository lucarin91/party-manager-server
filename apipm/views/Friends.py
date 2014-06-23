import psycopg2, psycopg2.extras, collections
import json

from flask import Flask
from flask import request
from flask import jsonify
from flask import session
from flask.views import MethodView

#HELPER#
from ..helper import *
from ..helper.Database import sql

class Friends(MethodView):
    
    def get(self,idEvento):
        try:
            cur = sql.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT id_user, username from utenti natural join evento where id_evento=%s", (idEvento,))
            sql.commit()
            utenti = cur.fetchall()
            for u in utenti:
                u['name'] = getFacebookName(u['id_user'])
            
            return jsonify(results = utenti)
        except Exception, e:
            sql.rollback()
            return 'error ' + str(e)
        finally:
            cur.close()

    def post(self,idEvento):
        if request.form['userList']!='':
            try:
                userList = json.loads(request.form['userList'].strip())
            except Exception, e:
                return 'json parser error'

            try:
                cur = sql.cursor()
                for user in userList:
                    cur.execute("INSERT INTO evento(id_evento, id_user) VALUES(%s,%s)", (idEvento,user))
                sql.commit()
                return 'fatto'

            except Exception, e:
                sql.rollback()
                print 'error ' + str(e)
                return 'error ' + str(e)
            finally:
                cur.close()
        else:
            return 'POST parameter error'

    def delete(self,idEvento,idFacebook):
        try:
            user = session['idFacebook']
            cur = sql.cursor()
            cur.execute("SELECT admin FROM party WHERE id_evento=%s",(idEvento,))
            admin = cur.fetchone()[0]
            if (admin==user):
                cur.execute("DELETE FROM evento WHERE id_evento=%s and id_user=%s", (idEvento,idFacebook))
                cur = sql.cursor()
                cur.execute("""DELETE FROM rispose 
                                WHERE id_attributo 
                                IN (select id_attributo from attributi where id_evento=%s) and id_user=%s""", (idEvento,idFacebook))     
                sql.commit()
                return 'fatto'
            else:
                return 'error no amministratore'
        except Exception, e:
            sql.rollback()
            print 'error ' + str(e)
            return 'error ' + str(e)
        finally:
            cur.close()