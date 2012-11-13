#!/usr/bin/python
import httplib2
import pprint
import mimetypes
import smtplib
import os

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

import config 

def main():
	# From http://www.mathstat.dal.ca/~selinger/ocr-test/
	files_to_send = ['test-images/Test1-th.png', 'test-images/Test1-th5.png', 'test-images/Test1.jpg', 'test-images/Test2-th.png', 'test-images/Test2-th5.png', 'test-images/Test2.jpg']

	googleDriveClient = GoogleDriveClient()
	emailClient = EmailClient()
	driveService = googleDriveClient.getDriveService()	
	for file_to_send in files_to_send:
		mime_type = mimetypes.guess_type(file_to_send)
		googleDriveClient.uploadFile(driveService, file_to_send, mime_type[0], file_to_send, True, config.OCR_LANGUAGE)
		emailClient.sendEmail('claes@holmerson.net', ['claes@holmerson.net'], file_to_send, file_to_send, [file_to_send])

class EmailClient:

	def __init__(self):
		self.smtp_server = config.SMTP_SERVER
		self.smtp_port = config.SMTP_PORT
		self.email_user = config.EMAIL_USER
		self.email_password = config.EMAIL_PASSWORD

	def sendEmail(self, send_from, send_to, subject, text, files=[]):
		smtpserver = smtplib.SMTP(self.smtp_server, self.smtp_port)

		smtpserver.ehlo()
		smtpserver.starttls()
		smtpserver.ehlo()
		smtpserver.login(self.email_user, self.email_password)

		msg = MIMEMultipart()
		msg['From'] = send_from
		msg['To'] = COMMASPACE.join(send_to)
		msg['Date'] = formatdate(localtime=True)
		msg['Subject'] = subject

		msg.attach( MIMEText(text) )

		for f in files:
			part = MIMEBase('application', "octet-stream")
			part.set_payload( open(f,"rb").read() )
			Encoders.encode_base64(part)
			part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
			msg.attach(part)
		
		smtpserver.sendmail(send_from, send_to, msg.as_string())
		smtpserver.close()			
		
class GoogleDriveClient:
		
	def __init__(self):
		pass
		
	def getDriveService(self):
		# Check https://developers.google.com/drive/scopes for all available scopes
		OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

		# Redirect URI for installed apps
		REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

		# Run through the OAuth flow and retrieve credentials
		flow = flow_from_clientsecrets('client_secrets.json',
									   scope=OAUTH_SCOPE,
									   redirect_uri=REDIRECT_URI)
									   
		storage = Storage('credentials.json')
		credentials = storage.get()
		if credentials is None or credentials.invalid == True:
		  credentials = run(flow, storage)
		  
		# Create an httplib2.Http object and authorize it with our credentials
		http = httplib2.Http()
		http = credentials.authorize(http)

		drive_service = build('drive', 'v2', http=http)
		return drive_service

	def uploadFile(self, drive_service, filename, mime_type, title, ocr=True, ocrLanguage = 'en'):
		# Insert a file
		media_body = MediaFileUpload(filename, mimetype='text/plain', resumable=True)
		body = {
		  'title': title,
		  'mimeType': mime_type,
		  'ocr': ocr,
		  'ocrLanguage': ocrLanguage
		}

		file = drive_service.files().insert(body=body, media_body=media_body, ocr=False).execute()
		print('File ID: %s' % file['id'])
		pprint.pprint(file)	

if __name__ == '__main__':
    main()	