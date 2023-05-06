from flask import render_template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

from project import app
from project.helpers.filemanager import FileManager
from project.config import constants as CONSTANTS
from project.helpers import tools

from email import encoders
import datetime
import smtplib
import os,sys

currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name
currentFileName = os.path.basename(__file__)

class EmailManager:    
		def __init__(self,template=None,mail_to='',subject='',attachment=None,data={},_type=1):
				self.emailfrom  = CONSTANTS.mailer_adress
				self.emailpass = CONSTANTS.mailer_password
				self.attachment=attachment
				self.mail_to = mail_to
				self.subject = subject
				if template is not None:
					if '.html' in template:
						self.template = render_template(template,data=data) if _type==1 else template
					else:
						self.template=template
				else:
					self.template=''
				self.subject = subject
				self.type = 'html' if _type==1 else 'plain' 
		
		def email_send(self):
				try:
					msg = MIMEMultipart()
					msg['From'] = self.emailfrom
					msg['Subject'] = self.subject
					if self.attachment is not None:
						check_file=FileManager(path=self.attachment).check_existing_file()
						if check_file['success']:
							file_extension = os.path.splitext(self.attachment)
							part = MIMEBase('application', "octet-stream")
							part.set_payload(open(self.attachment, "rb").read())
							encoders.encode_base64(part)
							part.add_header('Content-Disposition', 'attachment; filename=attachment_'+datetime.datetime.now().strftime("%Y%m%d")+file_extension[1])
							msg.attach(part) 
						else:
							print('El archvo no existe',self.attachment)
							return False
					msg.attach(MIMEText(self.template, self.type))
					server = smtplib.SMTP(CONSTANTS.smtp_server)          
					server.starttls()           
					server.login(msg['From'], self.emailpass) 
					server.sendmail(msg['From'],self.mail_to, msg.as_string())           
					server.quit()
					return True
				except Exception as e:
					data=e,currentFileName,currentFuncName()
					msj='Unable to run query.'
					msj=tools.logHandler(data,msj)
				return msj
