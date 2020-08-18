import smtplib

class Notificator:


    def __init__(self, recipient):
        self.sender = "Crypto@Trader.com"
        self.recipients = [recipient]
        self.smtp = smtplib.SMTP('localhost')

    def notify(self, message):
        try:
            mailmessage = """From: CryptoTrader <%s>
To: %s <%s>
Subject: CryptoTrader notification

%s
""" % (self.sender, self.recipients[0], self.recipients[0], message)
            self.smtp.sendmail(self.sender, self.recipients, mailmessage)         
            print("Successfully sent email")
        except smtplib.SMTPException as e:
            print(e)
            print("Error: unable to send email")


x = Notificator("me@folmer.info")
x.notify("test")
