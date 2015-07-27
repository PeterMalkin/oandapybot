import smtplib
import socket
from email.mime.text import MIMEText

class Email(object):
    def __init__(self, email_from, email_to, email_server, email_port, email_password,bot_name):
        self.email_from = email_from 
        self.email_to = email_to 
        self.email_server = email_server
        self.email_port = email_port
        self.email_password = email_password
        self.bot_name = bot_name 
        
    def Send(self, text):

        hostname = socket.gethostname()

        txt = "This is a message from oandabot " + self.bot_name + "("+hostname+")"
        txt += text
        
        e = MIMEText(txt, 'plain')
        e['Subject'] = "Oandabot " + self.bot_name + "("+hostname+")"
        e['From'] = self.email_from
        e['To'] = self.email_to
        
        s = smtplib.SMTP(self.email_server,self.email_port)
        s.login(self.email_from,self.email_password)
        s.sendmail(self.email_from,self.email_to,e.as_string())
        s.quit()
