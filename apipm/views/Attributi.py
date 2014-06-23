import psycopg2, psycopg2.extras, collections

from flask import request
from flask import jsonify
from flask import session
from flask.views import MethodView

#HELPER#
from ..helper import *
from ..helper.Database import sql

class Attributi(MethodView):
# id_attributo | domanda | template | id_evento | chiusa 
#--------------+---------+----------+-----------+--------

# id_risposta | id_attributo | id_user 
#-------------+--------------+---------
    def get(self,idEvento):
       #TO-DO: controllare che l'evento sia il mio
        try:
            cur = sql.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            '''
            cur.execute("""select distinct id_attributo, domanda, template, id_risposta, risposta, numR, numD, chiusa from
                            attributi 
                            natural join 
                            (select t1.id_attributo, t1.id_risposta, t2.numR from 
                            (
                            select id_risposta, id_attributo, count(*) as cnt 
                            from rispose 
                            group by id_risposta, id_attributo
                            ) t1 
                            join 
                            (
                            select id_attributo, max(cnt) over (partition by id_attributo) as numR 
                            from rispose 
                            natural join 
                            (
                            select id_risposta, id_attributo, count(*) as cnt
                            from rispose 
                            group by id_risposta, id_attributo
                            ) t4 
                            ) t2 
                            on t2.id_attributo=t1.id_attributo and t1.cnt=t2.numR 
                            ) tab natural join
                            (
                            select id_attributo, count(*) as numD 
                            from rispose 
                            group by id_attributo
                            ) tA natural join risposte
                            where attributi.id_evento=%s""",(idEvento,))
            '''
            cur.execute("""select distinct attributi.id_attributo, domanda, template, id_risposta, risposta, num_risposta as numR, num_risposte as numD, chiusa 
                            from risposte natural join rispose right join attributi on rispose.id_attributo = attributi.id_attributo 
                            where id_evento=%s and (max=true or id_risposta is NULL)""",(idEvento,))
            sql.commit()
            attributi = cur.fetchall()
            
            '''
            cur.execute("""select id_attributo, domanda, template, chiusa, id_risposta, risposta, id_user 
                        from attributi natural join rispose natural join risposte
                        where id_evento=%s order by id_attributo, id_risposta""", (idEvento,))
            sql.commit()
            attributi = cur.fetchall()
            
            ris = []
            if (len(attributi) != 0):
                ris.append({'id_attributo': attributi[0]['id_attributo'], 'domanda': attributi[0]['domanda'], 'template': attributi[0]['template'], 'chiusa': attributi[0]['chiusa'], 'rispList': []})
            
                for p in attributi:
                    if p['id_attributo'] != ris[len(ris)-1]['id_attributo']:
                        ris.append({'id_attributo': p['id_attributo'], 'domanda': p['domanda'], 'template': p['template'], 'chiusa': p['chiusa'], 'rispList': []})
                    
                    userName = json.load(urllib2.urlopen('http://graph.facebook.com/'+ str(p['id_user'])))
                    ris[len(ris)-1]['rispList'].append({'id_risposta': p['id_risposta'], 'risposta': p['risposta'], 'user': userName['name']})
            '''
        except Exception, e:
            sql.rollback()
            return 'error '+str(e)
        finally:
            cur.close()

        return jsonify(results = attributi)

    def post(self,idEvento):
        #return jsonify(request.form)
        if request.form['domanda']!='' and request.form['chiusa']!='':
            
            #TO_DO: controlare che l'evento sia il mio
            domanda = request.form['domanda']
            template = request.form['template'] if 'template' in request.form else None
            risposta = request.form['risposta'] if 'risposta' in request.form and request.form['risposta']!='' else None
            chiusa = request.form['chiusa']
            user = session['idFacebook']
            
            print "DEBUG parametri: "+domanda+" "+str(template)+" "+str(risposta)+" "+chiusa+" "+user
            #return domanda+template+risposta+chiusa+user
            try:
                cur = sql.cursor()
                cur.execute("SELECT array(SELECT name FROM templateDom)")
                sql.commit()
                templateList = cur.fetchall()[0][0]
                #templateDom = cur.fetchall()
                #return jsonify(templateDom)
                #templateList=[p[0] for p in templateDom]    
                print "DEBUG "+str(templateList)
                if template is not None and template not in templateList:
                    return 'error template parameter'
                
                #return 'template '+template+' chiusa '+chiusa
                
                
                if template is not None:
                    cur.execute("INSERT INTO attributi(domanda,template,id_evento,chiusa) VALUES(%s,%s,%s,%s) RETURNING id_attributo",(domanda,template,idEvento,chiusa))
                else:
                    cur.execute("INSERT INTO attributi(domanda,id_evento,chiusa) VALUES(%s,%s,%s) RETURNING id_attributo",(domanda,idEvento,chiusa))
                temp = cur.fetchone()
                print "DEBUG SQL: "+ str(temp)
                idAttributo = str(temp[0])
                
                if risposta is not None:
                    '''
                    if template == 'data' and chiusa == str(1):
                        #return 'sonoentrato'
                        cur.execute("UPDATE party SET data = %s WHERE id_evento=%s",(risposta,idEvento))
                        #sql.commit()
                    '''
                    cur.execute("INSERT INTO risposte(risposta,id_attributo) VALUES(%s,%s) RETURNING id_risposta",(risposta,idAttributo))
                    test = cur.fetchone()
                    print "SQL DEBUG: "+str(test)
                    idRisposta = str(test[0])
                    sql.commit()
                    cur.execute("INSERT INTO rispose(id_risposta,id_attributo,id_user) VALUES(%s,%s,%s)",(idRisposta,idAttributo,user))
                    #aggiorno NUM_RISPOSTE
                    #cur.execute("UPDATE attributi SET num_risposte=1 WHERE id_attributo=%s",(idAttributo,))
                    
                
                sql.commit()
                
                userName = getFacebookName(user)
                
                msg = {'type': 'newAttr', 'user': user, 'userName': userName, 'id_attributo': idAttributo, 'domanda': domanda, 'risposta': risposta, 'template': template, 'chiusa': chiusa, 'numd': '1', 'numr': '1'}
                sendNotificationEvent(idEvento,user,msg)
            
            except Exception, e:
                sql.rollback()
                return 'error '+str(e)
            finally:
                cur.close()
            
            return idAttributo
        else:
            return 'error POST parameters'