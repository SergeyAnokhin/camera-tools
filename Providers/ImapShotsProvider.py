import email
import getpass, imaplib
import os
import sys
import logging
from email.parser import HeaderParser
import email.header
from Common.SecretConfig import SecretConfig
from Pipeline.Model.CamShot import CamShot

class ImapShotsProvider:

    def __init__(self, tempFolder = 'temp'):
        self.log = logging.getLogger('IMAP')
        self.config = SecretConfig()
        self.config.fromJsonFile()
        self.tempFolder = tempFolder
        self.CleanFolder()

    def CleanFolder(self):
        for filename in os.listdir(self.tempFolder):
            os.unlink(filename)

    def GetShots(self, imap_folder):
        self.Connect()
        mail = self.GetLastMail(imap_folder)
        os.makedirs(self.tempFolder, exist_ok=True)
        shots = self.SaveAttachments(mail, self.tempFolder + '/MDAlarm_{:%Y%m%d-%H%M%S}-{}.jpg')
        self.Disconnect()
        return shots

    # filePattern : /path_to_file/MDAlarm_{:%Y%m%d-%H%M%S}-{}.jpg
    def SaveAttachments(self, mail, filePattern: str):
        index = 0
        for part in mail.walk():
            if(part.get_content_maintype() != 'image'):
                continue
            fileName = part.get_filename()

            if bool(fileName):
                memShot = CamShot(fileName)
                dt = memShot.GetDatetime(fileName)
                shot = CamShot(filePattern.format(dt, index))
                if not shot.Exist() :
                    shot.Write(part.get_payload(decode=True))
                else:
                    self.log.info(f'[MAIL] Attachment already exists: {shot.fullname}')
                yield shot
            index += 1

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
        typ, accountDetails = self.imapSession.login(self.config.gmail_username, self.config.gmail_password)
        if typ != 'OK':
            self.log.debug('Not able to sign in!')
            print ('Not able to sign in!')
            raise ConnectionError('imap.gmail.com')
        self.log.debug(f'Connection: {accountDetails}')

    def Disconnect(self):
        self.imapSession.close()
        self.imapSession.logout()
