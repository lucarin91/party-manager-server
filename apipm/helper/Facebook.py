import json
import urllib2
from urllib2 import HTTPError
from flask import current_app as app


def getFacebookName(idFacebook):
    try:
        if isinstance(idFacebook, unicode) or isinstance(idFacebook, str):
            print 'getFacebookName: is string ' + idFacebook
            ris = json.load(urllib2.urlopen('http://graph.facebook.com/' + idFacebook))
            print 'risposta facebok: ' + str(ris)
            return ris['name']
        elif isinstance(idFacebook, list):
            print 'getFacebookName: is list'
            ris = []
            for u in idFacebook:
                ris.append({'id_user': u,
                            'name': json.load(urllib2.urlopen('http://graph.facebook.com/' + u))['name']})
            return str(ris)
        else:
            print 'parametro errato'
            return None
    except HTTPError, e:
        print 'Could not download page ' + str(e)
    except Exception, e:
        print 'Error getFacebookName: ' + str(e)
