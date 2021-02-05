#!/usr/bin/env python3

import json, requests
from time import time
from hashlib import md5

# Static constants
marvel_endpoint = 'https://gateway.marvel.com:443/v1/public/'
character_name = "Spectrum"
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

def find_character_id(name):
  """
  Search for Marvel character from the developer API
  :param character_string: str
  :return: str
  """
  url = (marvel_endpoint + 'characters')
  result = requests.get(url, params=auth).json()
   # Write some pagination magic, this is vital
  total_results = result['data']['total']
  offset = result['data']['offset']

  while offset < total_results:
    result = requests.get(url, params=auth).json()
    offset = result['data']['offset']
    count = result['data']['count']

    for item in result['data']['results']:
      if name == item['name']:
        return item['id']

    # pagination counters
    new_offset = (offset + count)
    auth['offset'] = str(new_offset)

def get_char_data(id):
  """
  Query for char data found in the Marvel Developer API
  :param character_id: str
  :return: dict
  """
  dossier = {}

  image_size = "standard_fantastic"
  url = (marvel_endpoint + 'characters/' + str(id))
  result = requests.get(url, params=auth).json()

  dossier['name'] = result['data']['results'][0]['name']
  dossier['id'] = result['data']['results'][0]['id']
  dossier['description'] = result['data']['results'][0]['description']

  # Image path formattiing here:
  # https://developer.marvel.com/documentation/images
  image_path = result['data']['results'][0]['thumbnail']['path']
  extension = result['data']['results'][0]['thumbnail']['extension']
  dossier['jpeg'] = image_path + '/' + image_size + '.' + extension

  return dossier

# Load keys in dictionary and then next step
keychain = get_apikeys()
auth = marvel_auth(keychain)

# Find character by name
id = find_character_id(character_name)
dossier = get_char_data(id)
print (dossier)
