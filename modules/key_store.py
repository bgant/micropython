'''
MicroPython:          https://docs.micropython.org/en/latest/

Brandon Gant
Created: 2019-03-28
Updated: 2024-02-23

Usage:
   import key_store
   key_store.init()              <-- Creates key_store.db if it does not exist
   key_store.set('key','value')  <-- Sets key/value in database
   key_store.get('key')          <-- Gets value from database
   key_store.delete('key')       <-- Deletes key/value in database
   key_store.dumptext()          <-- Prints contents of key_store.db to screen
   key_store.dumpfile()          <-- Dumps contents of key_store.db to key_store.txt which ampy can retrieve
   key_store.wipe()              <-- Removes key_store.db file

This script keeps private settings out of github and also logs everything locally if needed.

Timestamps are in Embedded Epoch Time (seconds since 2000-01-01 00:00:00 UTC) as opposed to
Unix/POSIX Epoch Time (seconds since 1970-01-01 00:00:00 UTC).

   utime.localtime()
   utime.localtime(611934744)  <-- Both are in UTC timezone

'''

import btree

class KEY_STORE:
    def __init__(self):
        '''
        Create a new key_store.db database or update config settings
        '''
        self.file = 'key_store.db'
        try:
            self.f = open(self.file, 'r+b')  # Opens existing key_store.db
        except OSError:
            self.f = open(self.file, 'w+b')  # Creates key_store.db 

            '''
            self.db = btree.open(self.f,pagesize=512)
            self.db[b'ssid_name']    = input('Enter WiFi SSID - ')
            self.db[b'ssid_pass']    = input('Enter WiFi password - ')
            self.db[b'ntp_host']     = 'pool.ntp.org'
            self.db.flush()
            self.db.close()
            '''

    def set(self,key,value):
        '''
        Add new key/value pairs to key_store.db 
        '''
        self.f = open(self.file, 'r+b')
        self.db = btree.open(self.f)
        self.db[key] = value
        self.db.flush()
        self.db.close()

    def get(self,key):
        '''
        Retrieve data from key_store.db
        '''
        self.f = open(self.file, 'r+b')
        self.db = btree.open(self.f)
        try:
            return self.db[key].decode('utf-8')
        except KeyError:
            return None
        self.db.close()

    def delete(self,key):
        '''
        Delete data from key_store.db
        '''
        self.f = open(self.file, 'r+b')
        self.db = btree.open(self.f)
        del self.db[key]
        self.db.flush()
        self.db.close()

    def dumptext(self):
        '''
        Prints contents of key_store.db 
        ''' 
        self.f = open(self.file, 'r+b')
        self.db = btree.open(self.f)
        for key in self.db:
            print(key.decode('utf-8'), self.db[key].decode('utf-8'))
        self.db.close()

    def dumpfile(self):
        '''
        Dumps key_store.db contects to key_store.txt file
        '''
        self.f = open(self.file, 'r+b')
        self.db = btree.open(self.f)
        with open('key_store.txt', 'wt') as text:
            for key in self.db:
                self.pair = "{}:{}\n".format(key.decode('utf-8'), self.db[key].decode('utf-8'))
                text.write(self.pair)
        self.db.close()
        print('key_store.txt created')

    def wipe(self):
        '''
        Removes key_store.db
        ''' 
        import uos
        uos.remove(self.file)
        print(f'{self.file} removed')

