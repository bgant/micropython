'''
Source: https://docs.airnowapi.org/webservices --> Current Observations by Reporting Area
Rate Limited to 500 requests per one-hour period

Usage:
  from AirNowAPI import AQI
  aqi = AQI()
  json_data = aqi.download()
  PM = aqi.download('PM')

   0 -  50  Good (Green)
  51 - 100  Moderate (Yellow)
 101 - 150  Unhealthy for Sensitive Groups (Orange)
 151 - 200  Unhealthy (Red)
 201 - 300  Very Unhealthy (Purple)
 301 +      Hazardous (Maroon)

"air quality observations for the previous hour are generally available between 10 and 30 minutes past the hour"
'''

try:
    f = open('key_store.py','r')
    f.close()
    f = open('wifi.py','r')
    f.close()
    from key_store import KEY_STORE
    key_store = KEY_STORE()
except OSError:
    print('key_store.py and wifi.py are required to use this module')    
    exit()

# Load secrets from local key_store.db
if key_store.get('zipCode') and key_store.get('API_Key_AirNow'):
    zipCode = key_store.get('zipCode')
    API_Key_AirNow = key_store.get('API_Key_AirNow')
else:  # key_store values are empty
    zipCode = input('Enter 5-Digit Zip Code - ')
    API_Key_AirNow = input('Enter AirNow API Key - ')
    key_store.set('zipCode',zipCode)
    key_store.set('API_Key_AirNow',API_Key_AirNow)

import urequests
class AQI:
    def __init__(self):
        self.URL = f'https://www.airnowapi.org/aq/observation/zipCode/current/?&format=application/json&zipCode={zipCode}&API_KEY={API_Key_AirNow}'
        #print(self.URL)

    def download(self, query=None):
        self.response = urequests.get(self.URL).json()
        if not query: 
            return self.response
        elif query.lower() == 'pm':
            if not self.response:
                return None  # Service did not respond with data (downtime or maintenance)
            else:
                return self.response[0]['AQI']
        else:
            print(f'ERROR: {query} is not a valid query parameter')
