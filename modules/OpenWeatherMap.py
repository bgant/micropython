'''
Module Usage:
    import key_store
    key_store.set('latitude','<value>')
    key_store.set('longitude','<value>')
    key_store.set('API_Key_OpenWeatherMap','<appid>')

    from OpenWeatherMap import API
    api = API()
    response = api.download()
    response = api.download('temp')
'''

import urequests
import key_store

class API:
    def __init__(self):
        try:
            self.JSON_URL = 'https://api.openweathermap.org/data/2.5/weather?lat=' + \
                            key_store.get('latitude') + '&lon=' + key_store.get('longitude') + \
                            '&units=imperial&appid=' + key_store.get('API_Key_OpenWeatherMap')
        except:
            print('ERROR: Need to add latitude, longitude, API_Key_OpenWeatherMap to key_store')
            return None

    def download(self, query=None):
        try:
            self.response = urequests.get(self.JSON_URL).json()
            if not query:
                return self.response  # Return all json data
            else:
                return self.response['main'][query]  # Return just 'temp' or 'feels_like'
        except:
            print('ERROR: Unable to download OpenWeatherMap.org Data')
            return None

'''
download_hours = [h % 24 for h in range(13,28)]  # Between 8CST/13UTC and 23CST/4UTC
if utime.localtime()[3] in download_hours:   # Run during certain hours to conserve API Calls
'''
