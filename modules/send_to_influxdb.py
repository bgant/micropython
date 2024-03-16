
import urequests
from client_id import client_id
from key_store import KEY_STORE
key_store = KEY_STORE()

###################################
# Send Data to InfluxDB Function
###################################
server      = key_store.get('server')
port        = key_store.get('port')
database    = key_store.get('database')
measurement = key_store.get('measurement')
jwt         = key_store.get('jwt')
def send_to_influxdb(water=None,cpu=None):
    if '443' in port:
        url = f'https://{server}/influx/write?db={database}'
    else:
        url = f'http://{server}:{port}/write?db={database}'
    headers = {
        'Content-type': 'application/x-www-form-urlencoded',
        'Authorization': ''
    }
    headers['Authorization'] = f'Bearer {jwt}'
    data = f'{measurement},device={client_id} waterF={water},cpuF={cpu}'
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