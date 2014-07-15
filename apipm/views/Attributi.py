import psycopg2
import psycopg2.extras

from flask import request
from flask import jsonify
from flask import session
from flask.views import MethodView
from flask import current_app as app

#HELPER#
from ..helper import *
#from ..helper.Database import sql


class Attributi(MethodView):

    def get(self, idEvento):
       # TO-DO: controllare che l'evento sia il mio
        try:
            cur = sql.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""SELECT DISTINCT attributi.id_attributo,
                                            domanda,
                                            template,
                                            id_risposta,
                                            risposta,
                                            num_risposta AS numR,
                                            num_risposte AS numD,
                                            chiusa
                            FROM risposte NATURAL JOIN rispose
                                RIGHT JOIN attributi ON rispose.id_attributo = attributi.id_attributo
                            WHERE id_evento=%s and (max=true or id_risposta is NULL)""",
                        (idEvento,))
            sql.commit()
            attributi = cur.fetchall()
        except Exception, e:
            sql.rollback()
            return 'error ' + str(e)
        finally:
            cur.close()

        return jsonify(results=attributi)

    def post(self, idEvento):
        # return jsonify(request.form)
        if request.form['domanda'] != '' and request.form['chiusa'] != '':

            # TO_DO: controlare che l'evento sia il mio
            try:
                domanda = request.form['domanda']
                template = request.form.get('template')
                risposta = request.form.get('risposta') if request.form.get('risposta') != '' else None
                chiusa = bool(int(request.form['chiusa']))
                user = session['idFacebook']
                admin = Database.getAdminOfEvent(idEvento)
            except Exception, e:
                app.logger.error(str(e))
                return 'parameter exception'
            # print 'user e di tipo: ' + str(type(user))

            # print "DEBUG parametri: " + domanda + " " + str(template) + " " + str(risposta) + " " + chiusa + " " + user
            # return domanda+template+risposta+chiusa+user
            try:
                cur = sql.cursor()
                app.logger.debug('valore chiusa: ' + str(chiusa))

                if chiusa and user != admin:
                    return 'solo ladmin dellevento puo scrivere una domanda chiusa'

                if template is not None:
                    templateList = Database.getTemplateList()
                    if template not in templateList:
                        return 'error template parameter'

                # return 'template '+template+' chiusa '+chiusa

                    cur.execute("""INSERT INTO attributi(domanda,template,id_evento,chiusa)
                                    VALUES(%s,%s,%s,%s) RETURNING id_attributo""",
                                (domanda, template, idEvento, chiusa))
                else:
                    cur.execute(
                        "INSERT INTO attributi(domanda,id_evento,chiusa) VALUES(%s,%s,%s) RETURNING id_attributo", (domanda, idEvento, chiusa))

                temp = cur.fetchone()
                # print "DEBUG SQL: " + str(temp)
                idAttributo = str(temp[0])

                idRisposta = None
                if risposta is not None:
                    '''
                    if template == 'data' and chiusa == str(1):
                        #return 'sonoentrato'
                        cur.execute("UPDATE party SET data = %s WHERE id_evento=%s",(risposta,idEvento))
                        #sql.commit()
                    '''
                    cur.execute(
                        "INSERT INTO risposte(risposta,id_attributo) VALUES(%s,%s) RETURNING id_risposta", (risposta, idAttributo))
                    test = cur.fetchone()
                    # print "SQL DEBUG: " + str(test)
                    idRisposta = str(test[0])
                    sql.commit()
                    cur.execute(
                        "INSERT INTO rispose(id_risposta,id_attributo,id_user) VALUES(%s,%s,%s)", (idRisposta, idAttributo, user))
                    # aggiorno NUM_RISPOSTE
                    #cur.execute("UPDATE attributi SET num_risposte=1 WHERE id_attributo=%s",(idAttributo,))

                sql.commit()

                sendNotificationEvent(idEvento, user, {'type': code.type.attributo,
                                                       'method': code.method.new,
                                                       code.user.id: user,
                                                       code.evento.id: str(idEvento),
                                                       code.attributo.id: idAttributo,
                                                       code.attributo.nome: domanda,
                                                       code.risposta.nome: risposta,
                                                       code.risposta.id: str(idRisposta),
                                                       code.attributo.template: template,
                                                       code.attributo.chiusa: chiusa,
                                                       code.attributo.num: '1',
                                                       code.risposta.num: '1'
                                                       })

            except Exception, e:
                sql.rollback()
                return 'error ' + str(e)
            finally:
                cur.close()

            return idAttributo
        else:
            return 'error POST parameters'

    def delete(self, idEvento, idAttributo):
        user = session['idFacebook']
        print 'route: elimina ATTRIBUTI'

        try:
            admin = Database.getAdminOfEvent(idEvento)

            if user == admin:
                cur = sql.cursor()
                cur.execute("DELETE FROM attributi WHERE id_attributo=%s", (idAttributo,))
                sql.commit()
                sendNotificationEvent(idEvento,
                                      user,
                                      {'type': code.type.attributo,
                                       'method': code.method.delete,
                                       code.evento.id: str(idEvento),
                                       code.user.id: user,
                                       code.user.idAdmin: admin,
                                       code.attributo.id: str(idAttributo)})
                return 'fatto'
            else:
                return 'error: solo l admin puo eliminare una domanda'

        except Exception, e:
            sql.rollback()
            return 'error ' + str(e)
        finally:
            cur.close()
