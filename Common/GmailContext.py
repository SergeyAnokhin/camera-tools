import email
import getpass, imaplib
import os
import sys
from email.parser import HeaderParser
import email.header
from Common.SecretConfig import SecretConfig
from Common.CommonHelper import CommonHelper

class GmailContext():

    def __init__(self):
        self.config = SecretConfig()
        self.config.fromJsonFile()
        self.helper = CommonHelper()

    def DownoadLastAttachments(self, imap_folder: str, temp: str):
        Connect()
        GetLastMail(imap_folder)
        SaveAttachments(mail, temp + '/MDAlarm_{:%Y%m%d-%H%M%S}-{}.jpg')
        Disconnect()

    def Connect(self):
        self.imapSession = imaplib.IMAP4_SSL('imap.gmail.com')
        typ, accountDetails = self.imapSession.login(self.config.username, self.config.password)
        if typ != 'OK':
            print ('Not able to sign in!')
            raise
        print('[MAIL] Connection: ', accountDetails)

    def Disconnect(self):
        self.imapSession.close()
        self.imapSession.logout()

    def GetLastMail(self, imap_folder:  str):
        self.imapSession.select(imap_folder)
        typ, data = self.imapSession.search(None, 'ALL')
        if typ != 'OK':
                print ('Error searching Inbox.')
                raise

        # Iterating over all emails
        ids = data[0].split()
        print('[MAIL] Found "{}" mails in "{}"'.format(len(ids), imap_folder))
        msgId = ids[-1]
        #for msgId in data[0].split(): 
        typ, messageParts = self.imapSession.fetch(msgId, '(RFC822)')
        if typ != 'OK':
            print ('Error fetching mail.')
            raise

        emailBody = messageParts[0][1].decode('utf-8')
        mail = email.message_from_string(emailBody)
        subject, _ = email.header.decode_header(mail['subject'])[0]
        print("[MAIL] #{} | {}".format(msgId, subject))

        return mail

    # filePattern : /path_to_file/MDAlarm_{:%Y%m%d-%H%M%S}-{}.jpg
    def SaveAttachments(self, mail, filePattern: str):
        index = 0
        for part in mail.walk():
            if(part.get_content_maintype() != 'image'):
                continue
            fileName = part.get_filename()

            if bool(fileName):
                dt = self.helper.get_datetime(fileName)
                filePath = filePattern.format(dt, index)
                #filePath = os.path.join(output_dir, fileName)
                if not os.path.isfile(filePath) :
                    print ('[MAIL] Save mail attachment to: ', filePath)
                    fp = open(filePath, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()
                else:
                    print ('[MAIL] Attachment already exists: ', filePath)
            index += 1