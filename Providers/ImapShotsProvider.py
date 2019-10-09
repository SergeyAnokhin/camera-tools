import email, getpass, imaplib, os, sys, logging, datetime
from email.parser import HeaderParser
import email.header
from Common.SecretConfig import SecretConfig
from Common.CommonHelper import CommonHelper
from Pipeline.Model.CamShot import CamShot
from Archiver.CameraArchiveConfig import CameraArchiveConfig
from Pipeline.Model.PipelineShot import PipelineShot
from Providers.Provider import Provider

class ImapShotsProvider(Provider):

    def __init__(self, tempFolder = 'temp'):
        super().__init__("IMAP")
        self.secretConfig = SecretConfig()
        self.secretConfig.fromJsonFile()
        self.tempFolder = tempFolder
        self.helper = CommonHelper()

    def GetShotsProtected(self, pShots: []):
        self.Connect()
        mail = self.GetLastMail(self.config.imap_folder)
        os.makedirs(self.tempFolder, exist_ok=True)
        file_template = self.tempFolder + '/{:%Y%m%d-%H%M%S}-{}.jpg'
        shots = self.SaveAttachments(mail, file_template, self.CleanOldFiles)
        pShots.extend(shots)
        self.Disconnect()
        return shots

    def CleanOldFiles(self, shot: CamShot):
        secs = self.config.camera_triggered_interval_sec
        condition = lambda f: self.helper.FileNameByDateRange(f, shot.GetDatetime(), secs)
        removed = self.helper.CleanFolder(self.tempFolder, condition)
        [self.log.info(f'REMOVED: {f}') for f in removed]

    # filePattern : /path_to_file/{:%Y%m%d-%H%M%S}-{}.jpg
    def SaveAttachments(self, mail, filePattern: str, beforeFirstSave: None):
        index = 0
        result = []
        for part in mail.walk():
            if(part.get_content_maintype() != 'image'):
                continue
            fileName = part.get_filename()

            if bool(fileName):
                memShot = CamShot(fileName)
                dt = memShot.GetDatetime()
                dt = dt + datetime.timedelta(0,index)
                shot = CamShot(filePattern.format(dt, self.config.camera))
                if beforeFirstSave and index == 0:
                    beforeFirstSave(shot)
                if not shot.Exist() :
                    shot.Write(part.get_payload(decode=True))
                else:
                    self.log.info(f'[MAIL] Attachment already exists: {shot.fullname}')

                pShot = PipelineShot(shot, index)
                meta = self.CreateMetadata(pShot)
                meta["datetime"] = str(dt)
                #self.log.info(f'Attachment time : {dt}')
                result.append(pShot)
            index += 1
        return result

    def GetLastMail(self, imap_folder: str):
        self.imapSession.select(imap_folder)
        typ, data = self.imapSession.search(None, 'ALL')
        if typ != 'OK':
            self.log.error(f'Error searching in imap folder: {imap_folder}')
            raise ValueError('Error searching in imap folder: ' + imap_folder)

        # Iterating over all emails
        ids = data[0].split()
        self.log.debug(f'Found {len(ids)} mails in "{imap_folder}"')
        msgId = ids[-1].decode('utf-8')
        #for msgId in data[0].split(): 
        typ, messageParts = self.imapSession.fetch(msgId, '(RFC822)')
        if typ != 'OK':
            self.log.error(f'Error fetching mail: {msgId}')
            raise ValueError('Error fetching mail: ' + msgId)

        emailBody = messageParts[0][1].decode('utf-8')
        mail = email.message_from_string(emailBody)
        subject, _ = email.header.decode_header(mail['subject'])[0]
        self.log.info("#{} | {}".format(msgId, subject.decode('utf-8')))
        return mail

    def Connect(self):
        self.imapSession = imaplib.IMAP4_SSL('imap.gmail.com')
        typ, accountDetails = self.imapSession.login(self.secretConfig.gmail_username, self.secretConfig.gmail_password)
        if typ != 'OK':
            self.log.debug('Not able to sign in!')
            print ('Not able to sign in!')
            raise ConnectionError('imap.gmail.com')
        self.log.debug(f'Connection: {accountDetails}')

    def Disconnect(self):
        self.imapSession.close()
        self.imapSession.logout()
