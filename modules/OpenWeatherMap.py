'''
Module Usage:
    from OpenWeatherMap import WEATHER
    api = WEATHER()
    response = api.download()
    response = api.download('temp')
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
if key_store.get('latitude') and key_store.get('longitude') and key_store.get('API_Key_OpenWeatherMap'):
    latitude = key_store.get('latitude')
    longitude = key_store.get('longitude')
    API_Key_OpenWeatherMap = key_store.get('API_Key_OpenWeatherMap')
else:  # key_store values are empty
    latitude = input('Enter Latitude - ')
    longitude = input('Enter Longitude - ')
    API_Key_OpenWeatherMap = input('Enter OpenWeatherMap API Key - ')
    key_store.set('latitude',latitude)
    key_store.set('longitude',longitude)
    key_store.set('API_Key_OpenWeatherMap',API_Key_OpenWeatherMap)

import urequests
class WEATHER:
    def __init__(self):
        self.URL = 'https://api.openweathermap.org/data/2.5/weather?lat=' + \
            key_store.get('latitude') + '&lon=' + key_store.get('longitude') + \
            '&units=imperial&appid=' + key_store.get('API_Key_OpenWeatherMap')

    def download(self, query=None):
        try:
            self.response = urequests.get(self.URL).json()
            if not query:
                return self.response  # Return all json data
            else:
                if not self.response:  # No data from service (avoid IndexError exception)
                    return None 
                else:
                    return self.response['main'][query]  # Return just 'temp' or 'feels_like'
        except:
            print('ERROR: Unable to download OpenWeatherMap.org Data')
            return None

'''
download_hours = [h % 24 for h in range(13,28)]  # Between 8CST/13UTC and 23CST/4UTC
if utime.localtime()[3] in download_hours:   # Run during certain hours to conserve API Calls
'''
