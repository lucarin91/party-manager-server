from gcm import GCM
from gcm.gcm import GCMNotRegisteredException
from gcm.gcm import GCMUnavailableException
gcmSender = GCM('AIzaSyDz0b7i-9n3UPTXXrySRcfK90UfKweweUc')

from flask import request
from flask import current_app as app

#HELPER#
from .Database import *
from ..helper import *


class code:

    class type:
        evento = '1'
        attributo = '2'
        risposta = '3'
        user = '4'
        test = '5'

    class method:
        new = '1'
        modify = '2'
        delete = '3'
        uscito = '4'

    class evento:
        id = 'id_evento'
        nome = 'nome_evento'
        num = 'num_utenti'
        nomeVecchio = 'nome_evento_vec'

    class attributo:
        id = 'id_attributo'
        nome = 'domanda'
        template = 'template'
        chiusa = 'chiusa'
        num = 'numd'

    class risposta:
        id = 'id_risposta'
        nome = 'nome_risposta'
        agg = 'agg'
        num = 'numr'

    class user:
        id = 'id_user'
        nome = 'nome_user'
        idAdmin = 'id_admin'
        nomeAdmin = 'nomeAdmin'
        list = 'user_list'
        idDelete = 'id_user_delete'
        nomeDelete = 'nome_user_delete'


def sendNotification(idFacebook, message):
    try:
        cur = sql.cursor()
        cur.execute("SELECT id_cell FROM utenti WHERE id_user=%s", (idFacebook,))
        sql.commit()
        idReg = str(cur.fetchone()[0])
    except Exception, e:
        sql.rollback()
        return 'error2' + str(e)
    finally:
        cur.close()

    try:
        canonical_id = gcmSender.plaintext_request(registration_id=idReg, data=message)

        if canonical_id:
            # Repace reg_id with canonical_id in your database
            try:
                cur = sql.cursor()
                cur.execute(
                    "UPDATE utenti SET id_cell = %s WHERE id_cell = %s", (canonical_id, idReg))
                sql.commit()
            except Exception, e:
                sql.rollback()
                return 'error3 ' + str(e)
            finally:
                cur.close()

        return None

    except GCMNotRegisteredException:
        # Remove this reg_id from database
        return 'error: reg_id non presente'
    except GCMUnavailableException:
        return 'error: altra roba'
    except Exception, e:
        return str(e)


def sendNotificationEvent(idEvento, user, message):
    try:
        debug = request.args.get('debug') if request.args.get('debug') is not None else 'false'
        if debug == 'true':
            regId = getIdCellofEvento(idEvento, None)
        else:
            regId = getIdCellofEvento(idEvento, user)

        app.logger.debug(str(regId))

        sendNotificationList(regId, message)
    except Exception, e:
        app.logger.error('NotificheEvent: ' + str(e))


def sendNotificationList(userList, message):
    response = gcmSender.json_request(registration_ids=userList, data=factoryMessage(message))

    # Handling errors
    if 'errors' in response:
        app.logger.error('Notification ' + str(response.get('errors')))
        # print 'error GCM: send notification'
        # for error, reg_ids in response['errors'].items():
        # Check for errors and act accordingly
        # if error is 'NotRegistered':
                # Remove reg_ids from database
                # for reg_id in reg_ids:

    if 'canonical' in response:
        app.error.info('canonical change' + str(response.get('canonical')))
        for reg_id, canonical_id in response['canonical'].items():
        # Repace reg_id with canonical_id in your database
            try:
                cur = sql.cursor()
                cur.execute(
                    "UPDATE utenti SET id_cell = %s WHERE id_cell = %s", (canonical_id, reg_id))
                sql.commit()
            except Exception, e:
                sql.rollback()
                app.logger.error('canonical change: ' + str(e))
            finally:
                cur.close()


def factoryMessage(msg):
    idEvento = msg.get(code.evento.id)
    if code.user.idAdmin not in msg:
        msg[code.user.idAdmin] = getAdminOfEvent(idEvento)

    if code.evento.num not in msg:
        msg[code.evento.num] = getNumUtentiEvent(idEvento)

    if code.evento.id in msg and code.evento.nome not in msg:
        msg[code.evento.nome] = getEventName(idEvento)

    if code.attributo.id in msg and code.attributo.nome not in msg:
        msg[code.attributo.nome] = getAttributoName(msg.get(code.attributo.id))

    if code.risposta.id in msg and code.risposta.nome not in msg:
        msg[code.risposta.nome] = getRipostaName(msg.get(code.risposta.id))

    if code.user.id in msg and code.user.nome not in msg:
        msg[code.user.nome] = Facebook.getFacebookName(msg.get(code.user.id))

    # app.logger.debug(str(msg))
    return msg
