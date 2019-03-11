import datetime
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from Common.SecretConfig import SecretConfig

class MailSenderPostProcessor:
    sender: str = 'home.assistant.sergey@gmail.com'
    to: [] = ['home.assistant.sergey@gmail.com', 'anokhin.sergey@gmail.com']
    server = ''

    def __init__(self):
        self.config = SecretConfig()
        self.config.fromJsonFile()

    def GetShots(self):
        return ([], datetime.datetime.now())