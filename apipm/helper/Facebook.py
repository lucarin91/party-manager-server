import json
import urllib2


def getFacebookName(idFacebook):
    if isinstance(idFacebook, str):
        print 'getFacebookName: is string ' + idFacebook
        ris = json.load(urllib2.urlopen('http://graph.facebook.com/' + idFacebook))
        return ris['name']
    else:
        print 'getFacebookName: is list'
        ris = []
        for u in idFacebook:
            ris.append({'id_user': u,
                        'name': json.load(urllib2.urlopen('http://graph.facebook.com/' + u))['name']})
        return str(ris)
