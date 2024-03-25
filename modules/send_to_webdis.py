import urequests

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
        self.response = urequests.get(self.URL)
        print(f'Webdis Response: {self.response.text}')

