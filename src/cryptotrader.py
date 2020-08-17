import AES
import pickle
import codecs
import sqlite3
import sched, time
import traceback
import json

from pythonBitvavoApi.bitvavo import Bitvavo

class CryptoTrader:

    def __init__(self):
        self.get_config()
        try:
            self.verify_config()
            self.bitvavo = Bitvavo({"apikey" : self.config["bitvavokey"], "apisecret" : self.config["bitvavosecret"]})
            self.conn = sqlite3.connect(self.config["db"])
            self.s = sched.scheduler(time.time, time.sleep)
            self.s.enter(1, 1, self.loop)
            self.s.run()
        except Exception as e:
            print(str(e))

    def get_config(self):
        # load configuration
        print("Enter configuration file:")
        enc_config_file = input()
        try:
            with open(enc_config_file, "r") as f:
                encryptedconfig = f.read()
                try:
                    print("Enter configuration password:")
                    password = input()
                    aescipher = AES.AESCipher(password)
                    pickledconfig_b64 = aescipher.decrypt(encryptedconfig)
                    config = pickle.loads(codecs.decode(pickledconfig_b64.encode(), "base64"))
                    self.config = config
                except:
                    print("Reading configuration failed. Make sure the file is properly encrypted and you are using the correct password.")
        except:
            print("Could not find configuration file")

    def verify_config(self):
        required_fields = ["market", "sell-limit", "buy-limit", "sell-cap", "buy-cap", "polling-time", "timestamp", "bitvavokey", "bitvavosecret", "db"]
        for field in required_fields:
            if field not in self.config:
                raise Exception("Missing required field: %s" % (field))     

    '''
    main loop. 
    '''
    def loop(self):
        # get balance
        response = self.bitvavo.balance({})
        euro = filter(lambda x: x["symbol"] == "EUR", response)
        ltc = filter(lambda x: x["symbol"] == "LTC", response)
        for item in response:
            print(json.dumps(item, indent=4))
        # get current LTC stock price and price history
        response = self.bitvavo.tickerPrice({"market" : self.config["market"]})
        print(json.dumps(response, indent=4))
        current_price = float(response["price"])
        self. conn.execute("INSERT INTO HISTORY (market, value) VALUES (?, ?)", (self.config["market"], current_price))
        self.conn.commit()
        # determine if the trend is upward or downward
        # direction = 1
        # place order if within 5 percent of target (both sell and buy)
        # if current_price 
        self.s.enter(self.config["polling-time"], 1, self.loop)

test = CryptoTrader()