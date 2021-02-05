#!/usr/bin/env python3

import json, requests
from time import time
from hashlib import md5

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
  Construct authentication hash
  :param keychain: dict
  :return: dict
  """
  authentication = {}
  unix_timestamp = int(time())
  plaintext = str(unix_timestamp) + keychain["MARVEL_PRIVKEY"] + keychain["MARVEL_PUBKEY"]
  md5_ciphertext = md5(plaintext.encode("utf-8")).hexdigest()
  authentication['ts'] = str(unix_timestamp)
  authentication['apikey'] = keychain["MARVEL_PUBKEY"]
  authentication['hash'] = md5_ciphertext
  return authentication

marvel_endpoint = 'https://gateway.marvel.com:443/v1/public/'

# Load keys in dictionary and then next step
keychain = get_apikeys()
auth = marvel_auth(keychain)
url = (marvel_endpoint + 'characters')

response = requests.get(url, params=auth)
print(response.text)
