'''
Source: https://docs.airnowapi.org/webservices --> Current Observations by Reporting Area
Rate Limited to 500 requests per one-hour period

Usage:
  import key_store
  key_store.set('zipCode','<5-digits>')
  key_store.set('API_Key_AirNow','<key>')

  from AirNowAPI import AQI
  json_data = AQI()
  Ozone = AQI('Ozone')
  PM = AQI('PM')

   0 -  50  Good (Green)
  51 - 100  Moderate (Yellow)
 101 - 150  Unhealthy for Sensitive Groups (Orange)
 151 - 200  Unhealthy (Red)
 201 - 300  Very Unhealthy (Purple)
 301 +      Hazardous (Maroon)

"air quality observations for the previous hour are generally available between 10 and 30 minutes past the hour"
'''

import urequests
import key_store
zipCode = key_store.get('zipCode')
API_KEY = key_store.get('API_Key_AirNow')
URL = f'https://www.airnowapi.org/aq/observation/zipCode/current/?&format=application/json&zipCode={zipCode}&API_KEY={API_KEY}'
def AQI(query=None):
    data = urequests.get(URL).json()
    if not query: 
        return data
    elif query.lower() == 'pm':
        return data[1]['AQI']
    elif query.lower() == 'ozone':
        return data[0]['AQI']
    else:
        print(f'ERROR: {query} is not a valid query parameter')

