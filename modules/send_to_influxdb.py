import urequests

try:
    f = open('key_store.py','r')
    f = open('wifi.py','r')
    f = open('client_id.py','r')
    from key_store import KEY_STORE
    key_store = KEY_STORE()
    from client_id import client_id
except OSError:
    print('key_store.py, wifi.py, and client_id.py are required to use this module')    
    exit()
    
###################################
# Load secrets from key_store.db
###################################
if key_store.get('server') and key_store.get('port') and key_store.get('database') and key_store.get('measurement') and key_store.get('jwt'):
    server = key_store.get('server') # InfluxDB Server
    port = key_store.get('port') # InfluxDB Port
    database = key_store.get('database') # InfluxDB Database
    measurement = key_store.get('measurement') # InfluxDB Measurement
    jwt = key_store.get('jwt') # Json Web Token (see notes below)
else:  # key_store values are empty
    server = input('Enter InfluxDB Server Name or IP - ')
    port = input('Enter InfluxDB Port - ')
    database = input('Enter InfluxDB Database Name - ')
    measurement = input('Enter InfluxDB Measurement - ')
    jwt = input('Enter JSON Web Token - ')
    key_store.set('server',server)
    key_store.set('port',port)
    key_store.set('database',database)
    key_store.set('measurement',measurement)
    key_store.set('jwt',jwt)


###################################
# Send Data to InfluxDB Function
###################################
def send_to_influxdb(field_name=None,field_value=None):
    if '443' in port:
        url = f'https://{server}/influx/write?db={database}'
    else:
        url = f'http://{server}:{port}/write?db={database}'
    headers = {
        'Content-type': 'application/x-www-form-urlencoded',
        'Authorization': ''
    }
    headers['Authorization'] = f'Bearer {jwt}'
    data = f'{measurement},device={client_id} {field_name}={field_value}'
    response = urequests.post(url, headers=headers, data=data)
    if '204' in str(response.status_code):  # HTTP Status 204 (No Content) indicates server fulfilled request
        print(f'InfluxDB: {database} \t Measurement: {data} \t Status: {response.status_code} Success')
    else:
        print(f'InfluxDB: {database} \t Measurement: {data} \t Status: {response.status_code} Failed')

        
# Set JSON Web Token (JWT) from key_store.db
#
# If you enabled authentication in InfluxDB you need
# to create a JSON Web Token to write to a database:
#
#    https://www.unixtimestamp.com/index.php
#        Create a future Unix Timestamp expiration   
#
#    https://jwt.io/#debugger-io
#        HEADER
#            {
#              "alg": "HS256",
#              "typ": "JWT"
#             }
#        PAYLOAD
#            {
#              "username": "<InfluxDB username with WRITE to DATABASE>",
#              "exp": <Unix Timestamp expiration>
#            }
#        VERIFY SIGNATURE
#            HMACSHA256(
#              base64UrlEncode(header) + "." +
#              base64UrlEncode(payload),
#              <shared secret phrase set in InfluxDB>
#            )
#
# Source: https://docs.influxdata.com/influxdb/v1.8/administration/authentication_and_authorization/
#