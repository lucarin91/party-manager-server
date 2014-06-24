import json
import urllib2
from urllib2 import HTTPError


def getFacebookName(idFacebook):
    try:
        if isinstance(idFacebook, str):
            print 'getFacebookName: is string ' + idFacebook
            ris = json.load(urllib2.urlopen('http://graph.facebook.com/' + idFacebook))
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
            
    except HTTPError:
        print 'Could not download page'
