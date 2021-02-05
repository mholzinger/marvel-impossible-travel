#!/usr/bin/env python3

import json, requests, sqlite3, os
from time import time
from hashlib import md5
import os.path

# Static constants
marvel_endpoint = 'https://gateway.marvel.com:443/v1/public/'
suspect = "Spectrum"
OUR_DB = "spectrum.db"
#response = requests.get(url, params=auth).json()
#print(response)

def get_apikeys():
  """
  Load Marvel account api keys from text file
  :return: dict
  """
  keychain = {}
  with open(".apikeys") as f:
    for line in f:
      apikey, secret = line.partition("=")[::2]
      keychain[apikey] = secret.strip('\n')
  return keychain

def marvel_auth(keychain):
  """
  Build marvel auth dictionary
  :param keychain: dict
  :return: dict
  """
  authentication = {}

  unix_timestamp = int(time())
  plaintext = str(unix_timestamp) + \
    keychain["MARVEL_PRIVKEY"] + keychain["MARVEL_PUBKEY"]
  md5_ciphertext = md5(plaintext.encode("utf-8")).hexdigest()
  authentication['ts'] = str(unix_timestamp)
  authentication['apikey'] = keychain["MARVEL_PUBKEY"]
  authentication['hash'] = md5_ciphertext
  authentication['limit'] = 100

  return authentication

def setup_db(dbname):
  """
  Setup our Spectrum Database
  :param dbname: str
  """
  conn = sqlite3.connect(dbname)
  c = conn.cursor()
    # Create table
  c.execute('''CREATE TABLE marvel_characters
    (name text, id text, description text, picture_url text, picture blob)''')
  # Save (commit) the changes
  conn.commit()
  conn.close()

def eval_char_data(dossier):
  """
  Test for existing Marvel Character Data, commit if not exist
  :param dossier: dict
  """
  conn = sqlite3.connect(OUR_DB)
  c = conn.cursor()

  # Look to see if data exists
  c.execute("SELECT * FROM marvel_characters WHERE name=?", (dossier['name'],))
  if c.fetchone() is None:
    print ("adding", dossier['name'])
    # Download image
    response = requests.get(dossier['picture'])

    # Format DB commit
    params = (dossier['name'], dossier['id'], dossier['description'],
      dossier['picture'], sqlite3.Binary(response.content))

    sql = ''' INSERT INTO marvel_characters(name,id,description,picture_url,picture)
      VALUES(?,?,?,?,?) '''

   # Insert a row of data
    c.execute(sql, params)
    conn.commit()
    conn.close()

def parse_char_data(data):
  """
  Pase and add character data to db if not exist
  :param character_id: str
  :return: dict
  """
  dossier = {}
  image_size = "standard_fantastic"

  dossier['name'] = data['name']
  dossier['id'] = data['id']
  dossier['description'] = data['description']

  # Image path formatting here:
  # https://developer.marvel.com/documentation/images
  image_path = data['thumbnail']['path']
  extension = data['thumbnail']['extension']
  dossier['picture'] = image_path + '/' + image_size + '.' + extension

  return dossier

def find_character_id(name):
  """
  Search for Marvel character from the developer API
  :param character_string: str
  :return: str
  """

  # Check local DB file first
  conn = sqlite3.connect(OUR_DB)
  c = conn.cursor()

  # Look to see if data exists
  c.execute("SELECT * FROM marvel_characters WHERE name=?", (name,))
  data=c.fetchone()

  if data is None:
    # First, let's see if we have this character id stored already
    url = (marvel_endpoint + 'characters')
    result = requests.get(url, params=auth).json()

    # Vital pagination magic
    total_results = result['data']['total']
    offset = result['data']['offset']

    while offset < total_results:
      result = requests.get(url, params=auth).json()
      offset = result['data']['offset']
      count = result['data']['count']

      for item in result['data']['results']:
        dossier = parse_char_data(item)
        eval_char_data(dossier)

        if name == item['name']:
          return item['id']

      # pagination counters
      new_offset = (offset + count)
      auth['offset'] = str(new_offset)
  else:
    print('Name %s found with id %s'%(name, data[1]))
    id = data[1]
    return id


# Load keys in dictionary and then next step
keychain = get_apikeys()
auth = marvel_auth(keychain)

import os.path

if os.path.isfile(OUR_DB):
    print ("spctrum.db exists, continuing")
else:
    setup_db(OUR_DB)

# Find suspect character by name
id = find_character_id(suspect)
