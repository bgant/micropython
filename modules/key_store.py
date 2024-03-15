'''
MicroPython:          https://docs.micropython.org/en/latest/

Brandon Gant
Created: 2019-03-28
Updated: 2024-03-15

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
'''

import btree

class KEY_STORE:
    '''Stores secret or custom variables for use by scripts'''
    
    def __init__(self):
        '''Create a new key_store.db database or update config settings'''
        self.file = 'key_store.db'
        try:
            f = open(self.file, 'r+b')  # Opens existing key_store.db
        except OSError:
            f = open(self.file, 'w+b')  # Creates key_store.db 

    def set(self,key,value):
        '''Add new key/value pairs to key_store.db '''
        f = open(self.file, 'r+b')
        db = btree.open(f)
        db[key] = value
        db.flush()
        db.close()

    def get(self,key):
        '''Retrieve data from key_store.db'''
        f = open(self.file, 'r+b')
        db = btree.open(f)
        try:
            return db[key].decode('utf-8')
        except KeyError:
            return None
        db.close()

    def delete(self,key):
        '''Delete data from key_store.db'''
        f = open(self.file, 'r+b')
        db = btree.open(f)
        del db[key]
        db.flush()
        db.close()

    def dumptext(self):
        '''Prints contents of key_store.db ''' 
        f = open(self.file, 'r+b')
        db = btree.open(f)
        for key in db:
            print(key.decode('utf-8'), db[key].decode('utf-8'))
        db.close()

    def dumpfile(self):
        '''Dumps key_store.db contects to key_store.txt file'''
        f = open(self.file, 'r+b')
        db = btree.open(f)
        with open('key_store.txt', 'wt') as text:
            for key in db:
                pair = "{}:{}\n".format(key.decode('utf-8'), db[key].decode('utf-8'))
                text.write(pair)
        db.close()
        print('key_store.txt created')

    def wipe(self):
        '''Removes key_store.db''' 
        import uos
        uos.remove(self.file)
        print(f'{self.file} removed')
