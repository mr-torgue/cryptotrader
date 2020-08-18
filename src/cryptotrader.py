import AES
import pickle
import codecs
import sqlite3
import sched, time
import traceback
import json
import notificator

from pythonBitvavoApi.bitvavo import Bitvavo

class CryptoTrader:

    '''
    initializes CryptoTrader and starts the main loop
    '''
    def __init__(self):
        self.get_config()
        try:
            self.verify_config()
            self.bitvavo = Bitvavo({"apikey" : self.config["bitvavokey"], "apisecret" : self.config["bitvavosecret"]})
            self.conn = sqlite3.connect(self.config["db"])
            self.notificator = notificator.Notificator(self.config["mail-notification"])
            self.s = sched.scheduler(time.time, time.sleep)
            self.s.enter(1, 1, self.loop)
            self.s.run()
        except Exception as e:
            print(str(e))

    '''
    config is encrypted and encoded, so some effort has to be made to retrieve the config dictionary
    '''
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

    '''
    verify configuration by making sure that it contains all required fields
    '''
    def verify_config(self):
        required_fields = ["market", "sell-limit", "buy-limit", "sell-cap", "buy-cap", "polling-time", "timestamp", "bitvavokey", "bitvavosecret", "db", "mail-notification"]
        for field in required_fields:
            if field not in self.config:
                raise Exception("Missing required field: %s" % (field))
        self.config["sell-limit"] = float(self.config["sell-limit"])
        self.config["buy-limit"] = float(self.config["buy-limit"])
        self.config["sell-cap"] = float(self.config["sell-cap"])
        self.config["buy-cap"] = float(self.config["buy-cap"])
        self.config["polling-time"] = float(self.config["polling-time"])
        print(json.dumps(self.config, indent=4))
        print("Is the config correct (Y/N)?")
        if input() != "Y":
            exit(0)
    '''
    main loop:
    1. lookup balance for EUR and LTC
    2. lookup stock price for LTC and store it in the sqlite database
    3. calculate direction by summing difference for the last 3 days
    4. i 
    '''
    def loop(self):
        # get balance
        response = self.bitvavo.balance({})
        for item in response:
            print(json.dumps(item, indent=4))
            if item["symbol"] == "EUR":
                euro = float(item["available"])
            elif item["symbol"] == "LTC":
                ltc = float(item["available"])
        print(euro)
        print(ltc)
        # get current LTC stock price and price history
        response = self.bitvavo.tickerPrice({"market" : self.config["market"]})
        print(json.dumps(response, indent=4))
        current_price = float(response["price"])
        self.conn.execute("INSERT INTO HISTORY (market, value) VALUES (?, ?)", (self.config["market"], current_price))
        self.conn.commit()
        # determine if the trend is upward or downward
        cursor = self.conn.execute("SELECT value FROM HISTORY WHERE market=? AND timestamp>datetime('now', '-3 days') ORDER BY timestamp ASC;", (self.config["market"],))
        prices = cursor.fetchall()
        print(prices)
        direction = 0.0
        for i in range(1, len(prices)):
            price = prices[i][0]
            previous_price = prices[i-1][0]
            direction = price - previous_price
        # if current_price
        print(current_price) 
        if current_price < 0.95 * self.config["sell-limit"]:
            amount = self.config["sell-cap"] / current_price if ltc * current_price > self.config["sell-cap"] else ltc
            if amount != 0:
                self.notificator.notify("CryptoTrader will place an order:\nAmount: %s\nSell limit: %s\nCurrent price: %f\nThe current direction: %f\n" % (amount, self.config["sell-limit"], current_price, direction))
                #response = bitvavo.placeOrder(self.config["market"], 'sell', 'limit', { 'amount': amount, 'price': self.config["sell-limit"] })
        if current_price > 1.05 * self.config["buy-limit"]:
            amount = self.config["buy-cap"] / current_price if euro > self.config["buy-cap"] else euro / current_price
            if amount !=0:
                self.notificator.notify("CryptoTrader will place an order:\nAmount: %s\nBuy limit: %s\nCurrent price: %d\nThe current direction: %f\n" % (amount, self.config["buy-limit"], current_price, direction))
                #response = bitvavo.placeOrder(self.config["market"], 'buy', 'limit', { 'amount': amount, 'price': self.config["buy-limit"] })
        self.s.enter(self.config["polling-time"], 1, self.loop)

CryptoTrader()