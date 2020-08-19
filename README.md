# CryptoTrader
Cryptotrader is a python3 utility which buys and sells cryptocurrencies automatically. It currently only supports litecoin and uses bitvavo as a broker. CryptoTrader is written in python and is tested on linux. It should work on other operating systems as well, with some modifications.

# DISCLAIMER
USE AT OWN RISK! MR TORGUE IS NOT RESPONSIBLE FOR ANY LOSSES.

# Description
The program loads a configuration file which specifies the following fields:
| Field | Description |
| --- | --- |
| sell-limit | cryptotrader will sell if the current LTC price is above this limit |
| buy-limit | cryptotrader will buy if the current LTC price is below this limit |
| sell-cap | cryptotrader will not sell more than sell-cap euro worth of LTC |
| buy-cap | cryptotrader will not buy more than buy-cap worth of LTC|
| polling-time | specifies the interval in seconds in which cryptotrader will check the LTC prices |
| mail-notification | specifies the mail address to send notification to |
| bitvavokey | API key for BitVavo |
| bitvavosecret | API secret for BitVavo |

The configuration is encrypted using AES. Key has to be specified when the program starts. 
CryptoTrader places an order if the current price gets within 5 percent of the limit. 
A notification is send when placing an order. The caps specify the amount in euros which can be sold or bought every day.

CryptoTrader uses a sqlite database to store price history. The database is created when executing the configcreator. It is stored as a .db file.
cryptotrader.log logs all actions.

# installation and configuration

* install python3 pip3 and sqlite3
* adduser cryptotrader && passwd cryptotrader
* su cryptotrader
* cd ~
* virtualenv -p /usr/local/bin/python3.7 .virtualenv
* source .virtualenv/bin/activate
* git clone https://github.com/mr-torgue/cryptotrader.git (-b dev)
* cd cryptotrader
* pip3 install -r requirements.txt
* cd src
* python3 configcreator.py

Now the script can be run as "python3 cryptotrader.py". 


## install as a service
Does not work yet. The startup of CryptoTrader requires some interaction. If anyone knows how to do this with services, please contact me.

# Executing CryptoTrader
Simply run python3 cryptotrader.py and follow the instructions. Config extension end with '.enc', make sure you specify this.
To run CryptoTrader in the background:
* python3 cryptotrader.py
* CTRL+Z
* jobs -l
* disown -h %[jobid] (not PID)
* bg %[jobid]

# TODO
* Add more crypto currencies
* Secure notifications using PGP
* Add an API so the notifications mail can contain a confirmation link
* Use machine learning to get more insights about limits
* Create an android app