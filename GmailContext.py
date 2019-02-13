import email
import getpass, imaplib
import os
import sys
from SecretConfig import SecretConfig


class GmailContext():

    def __init__(self):
        self.config = SecretConfig()
        self.config.fromJsonFile()

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

    def GetLastMailAtachments(self, imap_folder:  str, output_dir: str):
        self.imapSession.select(imap_folder)
        typ, data = self.imapSession.search(None, 'ALL')
        if typ != 'OK':
                print ('Error searching Inbox.')
                raise

        # Iterating over all emails
        msgId = data[0].split()[-1]
        #for msgId in data[0].split(): 
        print('MsgId: ', msgId)
        typ, messageParts = self.imapSession.fetch(msgId, '(RFC822)')
        if typ != 'OK':
            print ('Error fetching mail.')
            raise

        emailBody = messageParts[0][1].decode('utf-8')
        mail = email.message_from_string(emailBody)

        for part in mail.walk():
            if(part.get_content_maintype() != 'image'):
                continue
            fileName = part.get_filename()

            if bool(fileName):
                filePath = os.path.join(output_dir, fileName)
                if not os.path.isfile(filePath) :
                    print (filePath)
                    fp = open(filePath, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()