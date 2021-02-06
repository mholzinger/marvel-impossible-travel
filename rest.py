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
    (name text, id text, description text, picture_url text)''')
  c.execute('''CREATE TABLE spectrum_associates
    (name text, id text, description text, picture_url text, picture blob)''')
  # Save (commit) the changes
  conn.commit()
  conn.close()

def char_lookup_table(dossier):
  """
  Test for existing Marvel Character Data, commit if not exist
  :param dossier: dict
  """
  conn = sqlite3.connect(OUR_DB)
  c = conn.cursor()

  # Look to see if data exists
  c.execute("SELECT * FROM marvel_characters WHERE name=?", (dossier['name'],))
  if c.fetchone() is None:
    print ("Adding" + dossier['name'] + "to lookup table")

    # Format DB commit
    params = (dossier['name'], dossier['id'], dossier['description'],
      dossier['picture'])

    sql = ''' INSERT INTO marvel_characters(name,id,description,picture_url)
      VALUES(?,?,?,?) '''

   # Insert a row of data
    c.execute(sql, params)
    conn.commit()
    conn.close()

def eval_associate(dossier):
  """
  Test for existing Marvel Character Data, commit if not exist
  :param dossier: dict
  """
  conn = sqlite3.connect(OUR_DB)
  c = conn.cursor()

  # Look to see if data exists
  c.execute("SELECT * FROM spectrum_associates WHERE name=?", (dossier['name'],))
  if c.fetchone() is None:
    print ("Adding" + dossier['name'] + "to lookup table")
    # Download image
    response = requests.get(dossier['picture'])

    # Format DB commit
    params = (dossier['name'], dossier['id'], dossier['description'],
      dossier['picture'], sqlite3.Binary(response.content))

    sql = ''' INSERT INTO spectrum_associates(name,id,description,picture_url,picture)
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

def get_id_dossier(id):
  """
  :param id: str
  :return: dict
  """
  dossier = {}
  url=(marvel_endpoint + 'characters/' + id)
  result = requests.get(url, params=auth).json()
  dossier = parse_char_data(result['data']['results'][0])
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
        char_lookup_table(dossier)

        if name == item['name']:
          id = item['id']
          return id

      # pagination counters
      new_offset = (offset + count)
      auth['offset'] = str(new_offset)
  else:
    print('Name %s found with id %s'%(name, data[1]))
    id = data[1]
    return id

def add_all_appeared_names_with_char(id):
  """
  Add all accociates IDs from comic appearances to 'spectrum_accociates' table
  :param id: str
  """
  url = (marvel_endpoint + 'characters/' + id + '/comics')
  result = requests.get(url, params=auth).json()
  for collection in result['data']['results']:
    for names in collection['characters']['items']:
      id = find_character_id(names['name'])
      dossier = get_id_dossier(id)
      eval_associate(dossier)

# Load keys in dictionary and then next step
keychain = get_apikeys()
auth = marvel_auth(keychain)

if os.path.isfile(OUR_DB):
    print ("spectrum.db exists, continuing")
else:
    setup_db(OUR_DB)

# Find suspect character by name
id = find_character_id(suspect)
add_all_appeared_names_with_char(id)
