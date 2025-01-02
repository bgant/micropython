'''
MicroPython:          https://docs.micropython.org/en/latest/

Brandon Gant
Created: 2019-03-28
Updated: 2025-01-01

Usage:
   import key_store
   key_store.set('key','value')  <-- Sets key/value in database
   key_store.get('key')          <-- Gets value from database
   key_store.delete('key')       <-- Deletes key/value in database
   key_store.show()              <-- Prints contents of key_store.db to screen
   key_store.export()            <-- Dumps contents of key_store.db to key_store.txt
   key_store.close()             <-- Mandatory to close everything when no longer needed
   key_store.open()              <-- Reopen access to key_store.db
   key_store.clear()             <-- Removes key_store.db

This script keeps private settings out of github and also logs everything locally if needed.

RULES:
  1) key_store.py should be a module with functions (not Class)
  2) Access to key_store.py should be done after import (not as part of Class)
  3) Closing key_store.py seems to cause more problems than leaving it open,
     but feel free to close it if you know your script is done using it.
'''

import btree

file = 'key_store.db'

def enable():
    '''Open up the database for read/write access'''
    global f
    try:
        f = open(file, 'r+b')  # Opens existing key_store.db
    except OSError:
        f = open(file, 'w+b')  # Creates key_store.db on storage
    global db
    db = btree.open(f)

def close():
    '''
    Closing the database at the end of processing is mandatory because
    some of the unwritten data may remain in the cache. Closing the file 
    stream is also mandatory to ensure that data flushed from the buffer
    goes into the underlying storage.
    '''
    global db
    db.close()
    global f
    f.close()

def set(key,value):
    '''Add new key/value pairs to key_store.db '''
    global db
    db[key] = value
    db.flush()

def get(key):
    '''Retrieve data from key_store.db'''
    try:
        global db
        return db[key].decode('utf-8')
    except KeyError:
        return None

def delete(key):
    '''Delete data from key_store.db'''
    global db
    try:
       del db[key]
       db.flush()
       print(f'{key} deleted')
    except KeyError:
       print(f'{key} does not exist')

def show():
    '''Prints contents of key_store.db ''' 
    global db
    for key in db:
        print(key.decode('utf-8'), db[key].decode('utf-8'))

def export():
    '''Dumps key_store.db contents to key_store.txt file'''
    global db
    with open('key_store.txt', 'wt') as text:
        for key in db:
            pair = "{}:{}\n".format(key.decode('utf-8'), db[key].decode('utf-8'))
            text.write(pair)
    print('key_store.txt created')

def clear():
    '''Removes key_store.db'''
    close()
    import uos
    uos.remove(file)
    print('%s removed' % file)


# Enable key_store.py on import and leave open
enable()

