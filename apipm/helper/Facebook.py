import json
import urllib2


def getFacebookName(idFacebook):
    if isinstance(idFacebook, str):
        ris = json.load(urllib2.urlopen('http://graph.facebook.com/' + str(idFacebook)))
        return ris['name']
    else:
        ris = []
        for u in idFacebook:
            ris.append({'id_user': u,
                        'name': json.load(urllib2.urlopen('http://graph.facebook.com/' + str(idFacebook)))['name']})
        return str(ris)
