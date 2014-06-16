import os
from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
from flask import session
from flask import Response
from flask.views import MethodView
import json
import urllib2
from gcm import GCM
from gcm.gcm import GCMNotRegisteredException
from gcm.gcm import GCMUnavailableException
import facebook
import psycopg2
import collections
import psycopg2.extras

from functools import wraps


APPTOKEN = '401068586702319|5f78073b1129c9ff17880a96b6bf9ac9'
APPID =  '401068586702319'
gcmSender = GCM('AIzaSyDz0b7i-9n3UPTXXrySRcfK90UfKweweUc')

'''
sql = psycopg2.connect(
    database='d5ht3v16g2i6te',
    user='vbsxnsuyearmdz',
    password='ulHwqakmS4SXJ0GRzheH96ZwRu',
    host='ec2-23-23-244-144.compute-1.amazonaws.com',
    port=5432
)
'''

application = Flask(__name__)
application.config.from_envvar('WSGI_ENV')
application.secret_key = 'asdasdasd'
sql = application.config['SQL']
where = application.config['WHERE']

def requiresLogin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'idFacebook' not in session:
            return 'session error'
        return f(*args, **kwargs)
    return decorated

@application.route('/')
@requiresLogin
def index():
    return 'ciao '+ where


class User(MethodView):
    def get(self, idEvento):

	try:
 		cur = sql.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
		cur.execute("SELECT id_user, username from utenti natural join evento where id_evento=%s", (idEvento,))
		sql.commit()
		utenti = cur.fetchall()
		for u in utenti:
			u['name'] = getFacebookName(u['id_user'])
		
		    
		return jsonify(results = utenti)
	except Exception, e:
		return 'error ' + str(e)
	finally:
		cur.close()
        

    def post(self):
        if request.form['idCell']!='' and request.form['username']!='':
        
            idCell = request.form['idCell'].strip()
            idFacebook = session['idFacebook']
            username = request.form['username'].strip()
            
            try:
                cur = sql.cursor()
                cur.execute("INSERT INTO utenti(id_cell,id_user,username) VALUES(%s,%s,%s)",(idCell,idFacebook,username))
                #cur.execute("SELECT * FROM test;")
                #pg.commit()
                sql.commit()
                #lastId = str(cur.fetchone()[0])
                
            except Exception, e:
                if isinstance(e,psycopg2.Error):
                    sql.rollback()
                    if e.diag.constraint_name.find('utenti_pkey') !=-1:
                        try:
                            ris = cur.execute("UPDATE utenti SET id_cell = %s WHERE id_user = %s",(idCell,idFacebook))
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

    
class Event(MethodView):

    def get(self):
        facebookId = session['idFacebook']
        try:
            cur = sql.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            #cur = sql.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
            #cur = sql.cursor()
            cur.execute("""SELECT evento.id_evento, party.nome_evento, party.admin, party.data, party.num_utenti
                        FROM evento 
                        JOIN party ON evento.id_evento=party.id_evento 
                        JOIN utenti ON utenti.id_user=evento.id_user 
                        WHERE utenti.id_user=%s""",
                        (facebookId,))
            sql.commit()
            eventi = cur.fetchall()
            
        except Exception, e:
            sql.rollback()
            return 'error '+str(e)
        finally:
            cur.close()
        return jsonify(results = eventi)

    def post(self):
        if request.form['name']!='' and request.form['userList']!='':
            try:
                nome_evento = request.form['name'].strip()
                print nome_evento
                userList = json.loads(request.form['userList'].strip())
                admin = session['idFacebook'].strip()
            except:
                return 'error json parser'

            if not admin in userList:
                userList.append(admin)

            print 'USERLIST: '+str(userList)

            numUtenti = len(userList)
            try:
                cur = sql.cursor()
                cur.execute("INSERT INTO party(admin,nome_evento,num_utenti) VALUES(%s,%s,%s) RETURNING id_evento",(admin,nome_evento,numUtenti))
                
                eventId = str(cur.fetchone()[0])
                for p in userList:
                    print str(p)
                    cur.execute("INSERT INTO evento(id_evento, id_user) VALUES (%s,%s)", (eventId,p))

                    
                    #int id, String name, String details, String date, String admin, int numUtenti
                sql.commit()

                adminName = getFacebookName(admin)
                msg = {'type':'newEvent','id_evento': eventId, 'nome_evento': nome_evento, 'admin': admin, 'adminName': adminName, 'num_utenti': str(numUtenti)}
                sendNotificationEvent(eventId,admin,msg)
                    
                    #ris = sendNotification(str(p),msg)
                    #if ris is not None:
                    #    print 'GCM error: '+str(ris)
            except Exception, e:
                sql.rollback()
                return 'error1 '+str(e)
            finally:
                cur.close()     
            
            return eventId
        else:
            return 'error POST parameters'   


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

class Risposte(MethodView):
    def get(self,idEvento,idAttributo):
        #controllare che l evento e il mio
        
        user = session['idFacebook']
        
        try:
            cur = sql.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""select risposte.id_risposta, risposta, id_user, template 
                        from risposte natural join attributi left join rispose on risposte.id_risposta=rispose.id_risposta
                        where attributi.id_attributo=%s order by id_risposta""",(idAttributo,))
            
            sql.commit()
            risposte = cur.fetchall()
            
            ris = []
            if (len(risposte) != 0):
                ris.append({'id_risposta': risposte[0]['id_risposta'], 'risposta': risposte[0]['risposta'], 'template': risposte[0]['template'], 'userList': []})
            
                for p in risposte:
                    if p['id_risposta'] != ris[len(ris)-1]['id_risposta']:
                        ris.append({'id_risposta': p['id_risposta'], 'risposta': p['risposta'], 'template': p['template'], 'userList': []})
                    if p['id_user'] is not None:
                        name = getFacebookName(p['id_user'])
                        ris[len(ris)-1]['userList'].append({'id_user': p['id_user'], 'name': name})
                        
        except Exception, e:
            sql.rollback()
            return 'error ' + str(e)
        finally:
            cur.close()
        
        return jsonify(results = ris)

    def post(self,idEvento,idAttributo):
        if request.form['risposta']!='':
            
            #idAttributo = request.form['idAttributo']
            risposta = request.form['risposta']
            user = session['idFacebook']
            
            try:
                cur = sql.cursor()
                #cur.execute("SELECT num_risposta FROM risposte WHERE id_attributo=%s and max=true",(idAttributo,))
                #numRispostaMax = cur.fetchone()[0]
                
                cur.execute("INSERT INTO risposte(risposta,id_attributo) VALUES(%s,%s) RETURNING id_risposta",(risposta,idAttributo))
                idRisposta = str(cur.fetchone()[0])    
                #cur.execute("UPDATE attributi SET num_risposte = num_risposte + 1 WHERE id_attributo = %s",(idAttributo,))
                sql.commit()

                #if numRispostaMax <= 1:
                #    cambiaMaxRisposta()
                


                cur.execute("INSERT INTO rispose(id_risposta,id_attributo,id_user) VALUES(%s,%s,%s)",(idRisposta,idAttributo,user))

                cur.execute("select domanda from attributi where id_attributo=%s",(idAttributo,))
                domanda = cur.fetchone()[0]
                sql.commit()
                userName = getFacebookName(user)
                msg = {'type':'newRis', 'agg': '0', 'user': user, 'userName': userName, 'id_attributo': idAttributo, 'id_risposta': idRisposta, 'domanda': domanda, 'risposta': risposta}
                sendNotificationEvent(idEvento,user,msg)
                
            except Exception, e:
                if isinstance(e,psycopg2.Error):
                    sql.rollback()
                    #return str(e.diag.constraint_name)
                    print 'error SQL: ' + str(e)
                    if e.diag.constraint_name is not None and e.diag.constraint_name.find('rispose_pkey') !=-1:
                        try:
                            cur.execute("UPDATE rispose SET id_risposta = %s WHERE id_user = %s and id_attributo = %s", (idRisposta,user,idAttributo))
                            sql.commit()
                            
                            cur.execute("select domanda from attributi where id_attributo=%s",(idAttributo,))
                            domanda = cur.fetchone()[0]
                            sql.commit()
                            userName = getFacebookName(user)
                            msg = {'type':'newRis', 'agg': '1', 'user': user, 'userName': userName, 'id_attributo': idAttributo, 'id_risposta': idRisposta, 'domanda': domanda, 'risposta': risposta}
                            sendNotificationEvent(idEvento,user,msg)
                        except Exception, e:
                            sql.rollback()
                            return 'error' + str(e)
                        return idRisposta
                return 'error' + str(e)
            finally:
                cur.close()
            
            return idRisposta
        else:
            return 'error POST paramaters'

    def put(self,idEvento,idAttributo):
        
        idRisposta = request.form['idRisposta']
        user = session['idFacebook']
        
        try:
            cur = sql.cursor()
            #cur.execute("UPDATE attributi SET num_risposte = num_risposte + 1 WHERE id_attributo = %s",(idAttributo,))
            #cur.execute("UPDATE risposte SET num_risposta = num_risposta + 1 WHERE id_risposta = %s",(idRisposta,))
            #sql.commit()

            cur.execute("INSERT INTO rispose(id_risposta,id_attributo,id_user) VALUES(%s,%s,%s)",(idRisposta,idAttributo,user))
            
            cur.execute("select domanda from attributi where id_attributo=%s",(idAttributo,))
            sql.commit()
            domanda = cur.fetchone()[0]
            cur.execute("select risposta, count(*) from rispose natural join risposte where id_risposta=%s group by risposta",(idRisposta,))
            sql.commit()
            risposta = cur.fetchone()[0]
            userName = getFacebookName(user)
            
            msg = {'type':'risp', 'agg':'0', 'user': user, 'userName': userName, 'id_attributo': idAttributo, 'id_risposta': idRisposta, 'domanda': domanda, 'risposta': str(risposta[0]), 'numr': str(risposta[1])}
            sendNotificationEvent(idEvento,user,msg)

        except Exception, e:
            if isinstance(e,psycopg2.Error):
                sql.rollback()
                #return str(e.diag.constraint_name)
                if e.diag.constraint_name.find('rispose_pkey') !=-1:
                    try:
                        ris = cur.execute("UPDATE rispose SET id_risposta = %s WHERE id_user = %s and id_attributo = %s",(idRisposta,user,idAttributo))
                        sql.commit()
                        
                        cur.execute("select domanda from attributi where id_attributo=%s",(idAttributo,))
                        sql.commit()
                        domanda = cur.fetchone()[0]
                        cur.execute("select risposta, count(*) from rispose natural join risposte where id_risposta=%s group by risposta",(idRisposta,))
                        sql.commit()
                        risposta = cur.fetchone()[0]
                        userName = getFacebookName(user)
                        
                        msg = {'type':'Risp', 'agg':'1', 'user': user, 'userName': userName, 'id_attributo': idAttributo, 'id_risposta': idRisposta, 'domanda': domanda, 'risposta': str(risposta[0]), 'numr': str(risposta[1])}
                        sendNotificationEvent(idEvento,user,msg)
                    except Exception, e:
                        sql.rollback()
                        return 'error' + str(e)
                    return 'aggiornato'
            return 'error' + str(e)
        finally:
            cur.close()

        return idRisposta

        '''
        try:
            cur = sql.cursor()
            cur.execute("INSERT INTO rispose(id_risposta,id_user) VALUES(%s,%s)",(idRisposta,user))
            sql.commit()

            cur.excute("SELECT id_attributo FROM risposte WHERE id_risposta=%s",(idRisposta,))
            sql.commit()
            idAttributo = cur.fetchone()[0]

            cur.execute("""SELECT num_utenti FROM party WHERE id_evento=
                            (SELECT id_evento FROM attributi WHERE id_attributo=%s""",(idAttributo,))
            sql.commit()
            numUtenti = cur.fetchone()[0]

            cur.execute("SELECT count(*) FROM rispose WHERE id_risposta=%s",(idRisposta,))
            sql.commit()
            countRis = cur.fetchone()[0]
            
            if numUtenti == countRis:
                cur.execute("SELECT risposta FROM risposte WHERE id_risposta=%s",(idRisposta,))
                cur.execute("""UPDATE attributi SET risposta = 
                                (SELECT risposta FROM risposte WHERE id_risposta=%s)
                                WHERE id_attributo = %s""",(idRisposta,idAttributo))

        except Exception, e:
            sql.rollback()
            return 'error '+str(e)
        finally:
            cur.close()

        return 'fatto'
        '''

eventoView = requiresLogin(Event.as_view('event'))
attributoView = requiresLogin(Attributi.as_view('attr'))
risposteView = requiresLogin(Risposte.as_view('ris'))
userView = requiresLogin(User.as_view('user'))
'''
eventoView = Event.as_view('event')
attributoView = Attributi.as_view('attr')
risposteView = Risposte.as_view('ris')
userView = User.as_view('user')
'''
application.add_url_rule('/event', view_func=eventoView, methods=['GET','POST'])
application.add_url_rule('/event/<int:idEvento>', view_func=attributoView, methods=['GET','POST'])
#application.add_url_rule('/attr', view_func=attributoView, methods=['GET','POST'])
application.add_url_rule('/event/<int:idEvento>/<int:idAttributo>', view_func=risposteView, methods=['GET','POST','PUT'])
application.add_url_rule('/user', view_func=userView, methods=['POST',])
application.add_url_rule('/user/<int:idEvento>', view_func=userView, methods=['GET',])

@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and request.form['idFacebook'] != '' and request.form['token'] != '':
        token = request.form['token'].strip()
        idFacebook = request.form['idFacebook'].strip()
        
        try:
            data = json.load(urllib2.urlopen('https://graph.facebook.com/debug_token?input_token='+token+'&access_token='+APPTOKEN))['data']
            
            if (data['is_valid'] == True and  data['app_id'] == APPID and data['user_id'] == idFacebook):
                session['idFacebook'] = data['user_id']
                return 'fatto'
            else:
                return 'login fallito'
        except Exception, e:
            return 'login error'
    else:
        return render_template('login.html')

@application.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('idFacebook', None)
    return 'fatto'


'''
DEBUG FUNCTION
'''

@application.route('/send', methods=['GET','POST'])
def send():
    if request.method == 'POST' and request.form['idFacebook']!='':
        idFacebook = request.form['idFacebook']
        sendNotification(idFacebook,{'type':'test'})
        return 'fatto'
    else:
        return render_template('send.html')
           

@application.route("/lista", methods=['GET','POST'])
def lista():
    if request.method == 'POST':
        table = request.form['table']
        try:
            cur = sql.cursor()
            if table == 'utenti':
                cur.execute("SELECT * FROM utenti")
            elif table == 'evento':
                cur.execute("SELECT * FROM evento")
            elif table == 'party':
                cur.execute("SELECT * FROM party")
            elif table == 'attributi':
                cur.execute("SELECT * FROM attributi")
            elif table == 'risposte':
                cur.execute("SELECT * FROM risposte")
            elif table == 'rispose':
                cur.execute("SELECT * FROM rispose")
            else:
                return 'parametro non riconosciuto'
            
            ris = cur.fetchall()
        except Exception, e:
            sql.rollback()
            return 'error '+str(e)
        finally:
            cur.close()

        return str(ris)
    else:
        return render_template('list.html')


'''
UTILITY
'''

def sendNotification(idFacebook, message):
    try:
        cur = sql.cursor()
        cur.execute("SELECT id_cell FROM utenti WHERE id_user=%s",(idFacebook,))
        sql.commit()
        idReg = str(cur.fetchone()[0])
    except Exception, e:
        sql.rollback()
        return 'error2'+str(e)
    finally:
        cur.close()

    try:
        canonical_id = gcmSender.plaintext_request(registration_id=idReg, data=message)
        
        if canonical_id:
            # Repace reg_id with canonical_id in your database
            try:
                cur = sql.cursor()
                cur.execute("UPDATE utenti SET id_cell = %s WHERE id_cell = %s",(canonical_id,idReg))
                sql.commit()
            except Exception, e:
                sql.rollback()
                return 'error3 '+str(e)
            finally:
                cur.close()
        
        return None

    except GCMNotRegisteredException:
        # Remove this reg_id from database
        return 'error: reg_id non presente'
    except GCMUnavailableException:
        return 'error: altra roba'
    except Exception,e:
        return str(e)

def sendNotificationEvent(idEvento, user, message):
    try:
        cur = sql.cursor()
        cur.execute("select array(select id_cell from evento natural join utenti where id_evento=%s and id_user<>%s)",(idEvento,user))
        sql.commit()
        regIds = cur.fetchall()[0][0]
        print 'regIds: ' + str(regIds)
        response = gcmSender.json_request(registration_ids=regIds, data=message)

        # Handling errors
        if 'errors' in response:
            print 'error GCM: send notification'
            #for error, reg_ids in response['errors'].items():
                # Check for errors and act accordingly
                #if error is 'NotRegistered':
                    # Remove reg_ids from database
                    #for reg_id in reg_ids:
                        
        if 'canonical' in response:
            print 'canonical change'
            for reg_id, canonical_id in response['canonical'].items():
                # Repace reg_id with canonical_id in your database
                cur.execute("UPDATE utenti SET id_cell = %s WHERE id_cell = %s",(canonical_id, reg_id))
                sql.commit()
    
    except Exception, e:
        sql.rollback()
        print 'error GCM: '+str(e)
    finally:
        cur.close()

def getFacebookName (idFacebook):
    ris = json.load(urllib2.urlopen('http://graph.facebook.com/'+ str(idFacebook)))
    return ris['name']
