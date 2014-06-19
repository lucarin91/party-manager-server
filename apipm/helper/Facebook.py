import json
import urllib2
import psycopg2, psycopg2.extras

def getFacebookName (idFacebook):
    ris = json.load(urllib2.urlopen('http://graph.facebook.com/'+ str(idFacebook)))
    return ris['name']