import json
import urllib2

def getFacebookName (idFacebook):
    ris = json.load(urllib2.urlopen('http://graph.facebook.com/'+ str(idFacebook)))
    return ris['name']