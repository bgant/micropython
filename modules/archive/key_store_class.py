'''
MicroPython:          https://docs.micropython.org/en/latest/

Brandon Gant
Created: 2019-03-28
Updated: 2025-01-02

Usage:
   import key_store
   key_store.set('key','value')  <-- Sets key/value in database
   key_store.get('key')          <-- Gets value from database
   key_store.delete('key')       <-- Deletes key/value in database
   key_store.show()              <-- Prints contents of key_store.db to screen
   key_store.export()            <-- Dumps contents of key_store.db to key_store.txt which ampy can retrieve
   key_store.clear()             <-- Removes key_store.db file
   key_store.close()             <-- Close key_store.db file when no longer needed
   key_store.enable()            <-- Open key_store.db again

This script keeps private settings out of github and also logs everything locally if needed.
'''

import btree

class KEY_STORE:
    '''Stores secret or custom variables for use by scripts'''
    def __init__(self):
        '''Create a new key_store.db database or update config settings'''
        self.file = 'key_store.db'

    def enable(self):
        '''Open up the database for read/write access'''
        try:
            self.f = open(self.file, 'r+b')  # Opens existing key_store.db
        except OSError:
            self.f = open(self.file, 'w+b')  # Creates key_store.db on storage
        self.db = btree.open(self.f)

    def close(self):
        '''
        Closing the database at the end of processing is mandatory because
        some of the unwritten data may remain in the cache. Closing the file 
        stream is also mandatory to ensure that data flushed from the buffer
        goes into the underlying storage.
        ''' 
        self.db.flush()
        self.db.close()
        self.f.close()

    def set(self,key,value):
        '''Add new key/value pairs to key_store.db '''
        self.db[key] = value
        self.db.flush()

    def get(self,key):
        '''Retrieve data from key_store.db'''
        try:
            return self.db[key].decode('utf-8')
        except KeyError:
            return None

    def delete(self,key):
        '''Delete data from key_store.db'''
        del self.db[key]
        self.db.flush()

    def show(self):
        '''Prints contents of key_store.db ''' 
        for key in self.db:
            print(key.decode('utf-8'), self.db[key].decode('utf-8'))

    def export(self):
        '''Dumps key_store.db contects to key_store.txt file'''
        with open('key_store.txt', 'wt') as text:
            for key in self.db:
                pair = "{}:{}\n".format(key.decode('utf-8'), self.db[key].decode('utf-8'))
                text.write(pair)
        print('key_store.txt created')

    def clear(self):
        '''Removes key_store.db''' 
        import uos
        uos.remove(self.file)
        print(f'{self.file} removed')


