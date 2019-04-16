import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from Common.SecretConfig import SecretConfig
from Processors.Processor import Processor

class MailSenderProcessor(Processor):
    sender: str = 'home.assistant.sergey@gmail.com'
    to: [] = ['home.assistant.sergey@gmail.com', 'anokhin.sergey@gmail.com']

    def __init__(self, isSimulation: bool = False):
        super().__init__("IMAP")
        self.config = SecretConfig()
        self.config.fromJsonFile()
        self.isSimulation = isSimulation

    def Process(self, pShots: []):
        #send_mail(self, subject, text, files=None):
        subject = "SUBJECT"
        body = "BODY"

        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = COMMASPACE.join(self.to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach(MIMEText(body))

        for pShot in pShots or []:
            f = pShot.Shot.fullname
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
        self.log.debug(f"[IMAP] Send mail: '{subject}'")
        if not self.isSimulation:
            smtp.sendmail(self.sender, self.to, msg.as_string())
        smtp.quit() 
        smtp.close()

        pShots[0].Metadata["IMAP"] = {}
        pShots[0].Metadata["IMAP"]["Subject"] = subject
        pShots[0].Metadata["IMAP"]["Body"] = body
        pShots[0].Metadata["IMAP"]["MessageSize"] = len(msg.as_string())
        return pShots
