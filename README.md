# cryptotrader
Cryptotrader is a python utility which buys and sells cryptocurrencies automatically. It currently only supports litecoin and uses bitvavo as a broker. Cryptotrader is written in python and is tested on linux. It should work on other operating systems as well.

# ...
The program loads a configuration file which specifies the following fields:
| Field | Description |
| --- | --- |
| sell-limit | cryptotrader will sell if the current LTC price is above this limit |
| buy-limit | cryptotrader will buy if the current LTC price is below this limit |
| sell-cap | cryptotrader will not sell more than sell-cap euro worth of LTC |
| buy-cap | cryptotrader will not buy more than buy-cap worth of LTC|
| polling-time | specifies the interval in seconds in which cryptotrader will check the LTC prices |
| mail-notification | specifies the mail address to send notification to |

The configuration is encrypted using AES. Key has to be specified when the program starts. 
CryptoTrader places an order if the current price gets within 5 percent of the limit. 
A notification is send when placing an order.


# installation and configuration

* install python3 pip3 and sqlite3
* pip3 install -r requirements.txt
* cd src
* python3 configcreator.py

Now the script can be run as "python3 cryptotrader.py". 

## install as a service
Change the following template to install cryptotrader as a service. Save as cryptotrader.service in /lib/systemd/system/.
```
[Unit]
Description=cryptotrader
After=multi-user.target
Conflicts=getty@tty1.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/file/cryptotrader.py
StandardInput=tty-force

[Install]
WantedBy=multi-user.target
```
Do the following to enable and start service:
```
sudo systemctl enable cryptotrader.service
sudo systemctl start cryptotrader.service
```
# TODO
* Add more crypto currencies
* Secure notifications using PGP
* Add an API so the notifications mail can contain a confirmation link
* Use ML to get good limits
* Create an android app