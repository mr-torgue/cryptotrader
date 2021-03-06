import AES
import pickle
import codecs
import sqlite3
import sched, time
import traceback
import json
import notificator
import getpass
import logging
import os
import datetime

from pythonBitvavoApi.bitvavo import Bitvavo

class CryptoTrader:

    '''
    initializes CryptoTrader and starts the main loop
    '''
    def __init__(self):
        self.get_config()
        try:
            logging.basicConfig(filename=self.filename + '.log',level=logging.DEBUG)
            self.bitvavo = Bitvavo({"apikey" : self.config["bitvavokey"], "apisecret" : self.config["bitvavosecret"]})
            response = self.bitvavo.markets({"market" : self.config["market"]})
            self.config["base"] = response["base"]
            self.config["quote"] = response["quote"]
            self.verify_config()
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
        self.filename, _ = os.path.splitext(enc_config_file)
        try:
            with open(enc_config_file, "r") as f:
                encryptedconfig = f.read()
                try:
                    print("Enter configuration password:")
                    password = getpass.getpass()
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
        for key in self.config:
            if key == "bitvavokey" or key == "bitvavosecret":
                print("\t%s: '%s%s%s'" % (key, self.config[key][:16], (len(self.config[key]) - 17) * '*', self.config[key][-1]))
            else:
                print("\t%s: '%s'" % (key, self.config[key]))
        print("Is the config correct (Y/N)?")
        if input() != "Y":
            exit(0)

    '''
    main loop:
    '''
    def loop(self):
        logging.info("TIME: %s" % (str(datetime.datetime.now())))
        last_sell = 0
        last_buy = 0
        interval = 86400 # 24*60*60 in seconds
        # get balance
        response = self.bitvavo.balance({})
        for item in response:
            logging.info("BALANCE %s:\n%s" % (item["symbol"], json.dumps(item, indent=4)))
            if item["symbol"] == self.config["base"]:
                base = float(item["available"])
            elif item["symbol"] == self.config["quote"]:
                quote = float(item["available"])
        # get current LTC stock price and price history
        response = self.bitvavo.tickerPrice({"market" : self.config["market"]})
        logging.info("Market PRICE:\n%s" % (json.dumps(response, indent=4)))
        current_price = float(response["price"])
        self.conn.execute("INSERT INTO HISTORY (market, value) VALUES (?, ?)", (self.config["market"], current_price))
        self.conn.commit()
        # determine if the trend is upward or downward
        cursor = self.conn.execute("SELECT value FROM HISTORY WHERE market=? AND timestamp>datetime('now', '-3 days') ORDER BY timestamp ASC;", (self.config["market"],))
        prices = cursor.fetchall()
        direction = 0.0
        for i in range(1, len(prices)):
            price = prices[i][0]
            previous_price = prices[i-1][0]
            direction = price - previous_price
        # if current_price
        current_time = datetime.datetime.now().timestamp()
        if current_price > (0.99 * self.config["sell-limit"]) and (current_time - last_sell) > interval:
            amount = round(self.config["sell-cap"] / current_price if base * current_price > self.config["sell-cap"] else base, 2)
            logging.info("""Trying to SELL %f %s for %f %s a piece.
                Total: %f
                Current price: %f""" 
                % (amount, self.config["base"], self.config["sell-limit"], self.config["quote"], amount * self.config["sell-limit"], current_price))
            if amount != 0:
                self.notificator.notify("""CryptoTrader will sell %s %s:
                    Base: %s %s
                    Selling price per item: %s %s
                    Total: %s %s
                    Current price: %f %s
                    The current direction: %f""" 
                    % (amount, self.config["base"], amount, self.config["base"], current_price, self.config["quote"], amount * self.config["sell-limit"], self.config["quote"], current_price, self.config["quote"], direction))
                #response = self.bitvavo.placeOrder(self.config["market"], 'sell', 'limit', { 'amount': str(amount), 'price': str(self.config["sell-limit"]) })
                last_sell = current_time
                #logging.info(response)
        if current_price < (1.01 * self.config["buy-limit"]) and (current_time - last_buy) > interval:
            amount = round(self.config["buy-cap"] / current_price if quote > self.config["buy-cap"] else quote / current_price, 2)
            logging.info("""Trying to BUY %f %s for %f %s a piece.
                Total: %f
                Current price: %f""" 
                % (amount, self.config["base"], self.config["buy-limit"], quote, amount * self.config["buy-limit"], current_price))
            if amount !=0:
                self.notificator.notify("""CryptoTrader will buy %s %s:
                    Base: %s %s
                    Buying price per item: %s %s
                    Total: %s %s
                    Current price: %f %s
                    The current direction: %f""" 
                    % (amount, self.config["base"], amount, self.config["base"], current_price, self.config["quote"], amount * self.config["buy-limit"], self.config["quote"], current_price, self.config["quote"], direction))
                #response = self.bitvavo.placeOrder(self.config["market"], 'buy', 'limit', { 'amount': str(amount), 'price': str(self.config["buy-limit"]) })
                last_buy = current_time
                #logging.info(response)
        self.s.enter(self.config["polling-time"], 1, self.loop)

CryptoTrader()