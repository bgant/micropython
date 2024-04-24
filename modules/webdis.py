'''
from webdis import WEBDIS
webdis = WEBDIS()

webdis.ping()

webdis.get('foo')
webdis.response_text
webdis.response_json  <-- None

webdis.get('json-epa-aqi')
webdis.response_text
webdis.response_json  <-- JSON 
'''

import urequests
import json

try:
    f = open('key_store.py','r')
    from key_store import KEY_STORE
    key_store = KEY_STORE()
except OSError:
    print('key_store.py required to use this module')    
    exit()
    
###################################
# Load secrets from key_store.db
###################################
if key_store.get('webdis_host') and key_store.get('webdis_port'):
    webdis_host = key_store.get('webdis_host')  # Webdis Host
    webdis_port = key_store.get('webdis_port')  # Webdis Port
else:  # key_store values are empty
    webdis_host = input('Enter Webdis Host Name or IP - ')
    webdis_port = input('Enter Webdis Port - ')
    key_store.set('webdis_host',webdis_host)
    key_store.set('webdis_port',webdis_port)


class WEBDIS:

    def __init__(self):
        self.host = webdis_host
        self.port = webdis_port

    def ping(self):
        self.URL = f'http://{self.host}:{self.port}/PING'
        self.send()

    def set(self,key=None,value=None):
        self.URL = f'http://{self.host}:{self.port}/SET/{key}/{value}'
        self.send()

    def get(self,key=None):
        self.URL = f'http://{self.host}:{self.port}/GET/{key}'
        self.send()

    def timeseries(self,key=None,value=None):
        self.URL = f'http://{self.host}:{self.port}/TS.ADD/{key}/*/{value}'
        self.send()

    def send(self):
        r = urequests.get(self.URL)
        webdis_json = r.json()
        self.response_text = webdis_json['GET']  # Webdis adds a JSON ['GET'] before string response
        try:
            self.response_json = json.loads(self.response_text)  # If Webdis string is JSON, convert to JSON format
        except:
            self.response_json = None
