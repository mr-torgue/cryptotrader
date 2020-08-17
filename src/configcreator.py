'''
Creates an encrypted config file.
TODO:
1. User verification step
'''

import pickle
import AES
import codecs

from datetime import datetime

# create config object
config = {}
config["market"] = "LTC-EUR"
config["db"] = "history.db"
config["sell-limit"] = 75
config["buy-limit"] = 45
config["sell-cap"] = 1
config["buy-cap"] = 1
config["polling-time"] = 120
config["timestamp"] = str(datetime.now())
# bitvavo kay and secret:
print("Enter bitvavo API key")
config["bitvavokey"] = input()
print("Enter bitvavo API secret")
config["bitvavosecret"] = input()
# serialize object and convert is to base 64 string
pickledconfig_b64 = codecs.encode(pickle.dumps(config), "base64").decode()
# encrypt bytes
print("Configuration password:")
key = input()
aescipher = AES.AESCipher(key)
encryptedconfig = aescipher.encrypt(pickledconfig_b64)
# write config to file
print("Enter filename:")
filename = input() + ".enc"
with open(filename, "w") as f:
	f.write(encryptedconfig.decode())


