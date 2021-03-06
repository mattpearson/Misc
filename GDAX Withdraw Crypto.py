## Example of how to withdraw crypto from GDAX exchange without using 3rd party API. 

import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase

# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = signature.digest().encode('base64').rstrip('\n')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request

api_url = 'https://api.gdax.com/'

Auth(key, b64secret, passphrase)  ### TODO: Fill in your key, b64 secret, and passphrase here.

# Get accounts
r = requests.get(api_url + 'accounts', auth=auth)
print r.json()

withdrawParams = {
      'amount': '0.1', 
      'currency':'ETH',
      'crypto_address':'0x000000000000000000000000000'    ### TODO: Replace with your ETH address
    }
r = requests.post(api_url + 'withdrawals/crypto', json=withdrawParams, auth=auth)
print r.json()



