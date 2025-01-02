'''
from webdis

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
    import key_store
except OSError:
    print('key_store.py required to use this module')    
    exit()

key_store.enable()
if key_store.get('webdis_host') and key_store.get('webdis_port'):
    host = key_store.get('webdis_host')  # Webdis Host
    port = key_store.get('webdis_port')  # Webdis Port
else:  # key_store values are empty
    host = input('Enter Webdis Host Name or IP - ')
    port = input('Enter Webdis Port - ')
    key_store.set('webdis_host',host)
    key_store.set('webdis_port',port)
key_store.close()

if '443' in port:
    URL_base = f'https://{host}/'
else:
    URL_base = f'http://{host}:{port}/' 

def ping():
    URL = URL_base + f'PING'
    send(command='PING')

def set(key=None,value=None):
    URL = URL_base + f'SET/{key}/{value}'
    send(command='SET')

def get(key=None):
    URL = URL_base + f'GET/{key}'
    send(command='GET')

def timeseries(key=None,value=None):
    URL = URL_base + f'TS.ADD/{key}/*/{value}'
    send(command='TS.ADD')
        
def timeseriesget(key=None):
    URL = self.URL_base + f'TS.GET/{key}'
    send(command='TS.GET')

def send(command=None):
    global webdis_json
    global response_text
    global response_json
    try:
        r = urequests.get(URL)
        webdis_json = r.json()
        response_text = webdis_json[command]  # Webdis adds a JSON ['COMMAND'] before string response
    except:
        response_text = None
    try:
        response_json = json.loads(response_text)  # If Webdis string is JSON, convert to JSON format
    except:
        response_json = None

