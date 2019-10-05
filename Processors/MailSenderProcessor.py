import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from Common.SecretConfig import SecretConfig
from Processors.Processor import Processor
from Pipeline.Model.PipelineShot import PipelineShot

class MailSenderProcessor(Processor):
    sender: str = 'home.assistant.sergey@gmail.com'
    to: [] = ['home.assistant.sergey@gmail.com', 'anokhin.sergey@gmail.com']

    def __init__(self, isSimulation: bool = False):
        super().__init__("IMAP")
        self.secretConfig = SecretConfig()
        self.secretConfig.fromJsonFile()
        self.isSimulation = isSimulation

    def Process(self, pShots: []):
        #send_mail(self, subject, text, files=None):
        self.log.info(f'### PROCESS: ***{self.name}*** ######################')
        subject = self.GetSubject(pShots)
        body = self.GetBody(pShots)

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

        self.log.debug(f"- Send mail: '{subject}' to {self.to}")
        self.log.debug(f"- Body: \n{body}")
        if not self.isSimulation:
            smtp = smtplib.SMTP('smtp.gmail.com', 587)
            smtp.starttls()
            smtp.login(self.secretConfig.gmail_username, self.secretConfig.gmail_password)
            smtp.sendmail(self.sender, self.to, msg.as_string())
            smtp.quit() 
            smtp.close()

        pShots[0].Metadata["IMAP"] = {}
        pShots[0].Metadata["IMAP"]["Subject"] = subject
        pShots[0].Metadata["IMAP"]["Body"] = body
        pShots[0].Metadata["IMAP"]["MessageSize"] = len(msg.as_string())
        return pShots

    def GetSubject(self, pShots: []):
        dt = pShots[0].Shot.GetDatetime()
        camera = self.config.camera
        subject = f"{camera} @{dt:%H:%M} "

        labels = self.GetAllLabels(pShots)
        labelsCount = self.GetMaximumCountPerShot(pShots, labels)

        details = " ".join(labelsCount)
        return subject + details + f' ({dt:%d.%m.%Y})'

    def GetMaximumCountPerShot(self, pShots: [], labels: []):
        all_dict = {}
        for pShot in pShots:
            if "YOLO" not in pShot.Metadata:
                continue
            current_dict = {}
            for area in pShot.Metadata["YOLO"]:
                label = area["label"]
                if label in current_dict:
                    current_dict[label] += + 1
                else:
                    current_dict[label] = 1

            for label in current_dict:
                if label in all_dict:
                    count = all_dict[label]
                    if current_dict[label] > count:
                        all_dict[label] = current_dict[label]
                else:
                    all_dict[label] = current_dict[label]
        #print(all_dict)
        results = []
        for label in all_dict:
            count = all_dict[label]
            if count == 1:
                results.append(label)
            else:
                results.append(f'{label}:{count}')
        return results

    def GetAllLabels(self, pShots: []):
        list = []
        for pShot in pShots:
            if "YOLO" not in pShot.Metadata:
                continue
            for area in pShot.Metadata["YOLO"]:
                list.append(area["label"]) 
            
        return set(list)

    def GetBody(self, pShots: []):
        body = ""
        for shot in pShots:
            body += f'#{shot.Index}: {shot.OriginalShot.filename} \n'
            if 'YOLO' in shot.Metadata:
                yolo = shot.Metadata['YOLO']
                for item in yolo:
                    body += f'- YOLO: {item["label"]} ({item["confidence"]}) prof: {item["size"][0]}x{item["size"][1]} = {item["profile_proportion"]} @{item["center_coordinate"][0]}x{item["center_coordinate"][1]}\n'
            if 'DIFF' in shot.Metadata:
                diff = shot.Metadata['DIFF']
                body += f'- DIFF: {diff["Diff"]["TotalArea"]}\n'
                if "boxes" in diff:
                    for item in diff["boxes"]:
                        body += f'  - BOX {item["area"]} prof: {item["profile_proportion"]} @{item["center"][0]}x{item["center"][1]}\n'
            if 'TRAC' in shot.Metadata:
                trac = shot.Metadata['TRAC']
                for key in trac:
                    body += f'- TRAC angle {trac[key]["angle"]} distance {trac[key]["distance"]} \n'
        return body