import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from Common.SecretConfig import SecretConfig


class ImapGmailHelper:
    sender: str = 'home.assistant.sergey@gmail.com'
    to: [] = ['home.assistant.sergey@gmail.com', 'anokhin.sergey@gmail.com']
    server = ''

    def __init__(self):
        self.config = SecretConfig()
        self.config.fromJsonFile()

    def send_mail(self, subject, text, files=None):
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = COMMASPACE.join(self.to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach(MIMEText(text))

        for f in files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(f)
                )
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            msg.attach(part)

        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls() 
        smtp.login(self.config.gmail_username, self.config.gmail_password)
        text = msg.as_string() 
        print("[IMAP] Send mail: '{}'".format(subject))
        smtp.sendmail(self.sender, self.to, msg.as_string())
        smtp.quit() 
        smtp.close()
