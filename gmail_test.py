from GmailContext import GmailContext

gmail = GmailContext()
gmail.Connect()
gmail.GetLastMailAtachments('camera/foscam', 'attachments')
gmail.Disconnect()