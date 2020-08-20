'''
Creates an encrypted config file.
'''

import pickle
import AES
import codecs
import sqlite3
import getpass
import json

from pythonBitvavoApi.bitvavo import Bitvavo
from datetime import datetime

def create_db(filename):
	filename = filename + ".db"
	conn = sqlite3.connect(filename)
	conn.execute('''CREATE TABLE HISTORY
	         (ID INTEGER PRIMARY KEY AUTOINCREMENT,
	         market CHAR(16),
	         value FLOAT NOT NULL,
	         timestamp DATE DEFAULT (datetime('now','localtime')));''')
	conn.close()

print("""WARNING!!!
This script can buy and sell LTC without user interaction. Make sure you specify your limits correctly.
mr-torgue is not liable or responsible for your losses.""")

# create config object
print("Enter config filename:")
filename = input() 
config = {}
bitvavo = Bitvavo()
response = bitvavo.markets({})
for i in range(len(response)):
	print("%d: %s" % (i, response[i]["market"]))
print("Specify market:")	
index = int(input())
print("You selected the following market:\n%s" % (json.dumps(response[index], indent=4)))
config["market"] = (response[index])["market"]
response = bitvavo.tickerPrice({"market" : config["market"]})
print("The current price for this market is:\n%s" % (json.dumps(response, indent=4)))
config["db"] = filename + ".db"
print("Sell limit:")
config["sell-limit"] = input() # 75
print("Buy limit:")
config["buy-limit"] = input() # 45
print("Sell cap:")
config["sell-cap"] = input() # 200
print("Buy cap:")
config["buy-cap"] = input() # 200
print("Polling time in seconds:")
config["polling-time"] = input() # 120
print("E-mail address for notifications:")
config["mail-notification"] = input()
#print("Use PGP (Y/N)")
#config["PGP"] = True if input() == "Y" else False
config["timestamp"] = str(datetime.now())
create_db(filename)

# bitvavo kay and secret:
print("Enter bitvavo API key")
config["bitvavokey"] = getpass.getpass()
print("Enter bitvavo API secret")
config["bitvavosecret"] = getpass.getpass()

# serialize object and convert is to base 64 string
pickledconfig_b64 = codecs.encode(pickle.dumps(config), "base64").decode()

# encrypt bytes
print("Configuration password:")
key = getpass.getpass()
aescipher = AES.AESCipher(key)
encryptedconfig = aescipher.encrypt(pickledconfig_b64)

# write config to file
with open(filename + ".enc", "w") as f:
	f.write(encryptedconfig.decode())