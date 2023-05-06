import ftplib
import sys
import os
import os.path
from project import app
from project.helpers.filemanager import FileManager
from werkzeug.utils import secure_filename
from project.config import constants as CONSTANTS
from project.helpers import tools
from flask import request

currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name
currentFileName = os.path.basename(__file__)

class FtpManager:
	def __init__(self,directory=None):
		self.directory=tools.getPOSTParams('directory','/')
	def ftp_conection(self):
		ftp = ftplib.FTP()
		try:
			ftp.connect(CONSTANTS.ftp_host,CONSTANTS.ftp_port)
		except Exception as e:
			msj='Unable to connect to FTP host.'
			success=False
		else:
			try:
				ftp.login(CONSTANTS.ftp_user, CONSTANTS.ftp_pass)
			except ftplib.all_errors as e:
				data=e,currentFileName,currentFuncName()
				msj='FTP authentication error.'
				msj=tools.logHandler(data,msj)
				success=False
			else:
				return ftp
		return ({'success':success,'msj':msj,'data':ftp})

	def list_diretory(self):
		c_ftp=None
		dirs=[]
		files=[]
		data={'folders':[],'files':[]}
		try:
			c_ftp=self.ftp_conection()
			if type(c_ftp)!=ftplib.FTP:
				return ({'success':c_ftp['success'],'msj':c_ftp['msj']})
			items = c_ftp.nlst(self.directory)
			if len(items) > 0:
				for item in items:
					abs_path=os.path.normpath(self.directory)+'/'+item
					try:
						c_ftp.cwd(abs_path)
					except Exception as e:
						files.append(abs_path)
					else:
						dirs.append(abs_path)
						c_ftp.cwd('..')
				data.update({'folders':dirs,'files':files})
			else:
				return ({'success':True,'data':data})
		except ftplib.all_errors as e:
			data=e,currentFileName,currentFuncName()
			msj='Error triying to get directory.'
			msj=tools.logHandler(data,msj)
			data=None
			success=False
		else:
			msj='OK'
			success=True
		finally:
			try:
				c_ftp.quit()
			except Exception as e:
				pass
		return ({'success':success,'msj':msj,'data':data})

	def check_existing(self):
		abs_path=os.path.normpath(self.directory)
		head,tail=os.path.dirname(abs_path),os.path.basename(abs_path)
		if head=='':
			head=tail+'/'
		c_ftp=self.ftp_conection()
		if type(c_ftp)!=ftplib.FTP:
			return ({'success':c_ftp['success'],'msj':c_ftp['msj'],'token':request.headers['token']})
		else:
			try:
				c_ftp.cwd(head)
			except Exception as e:
				msj='FTP folder does not exists.'
				success=False
			else:
				if tail!='':
					files = list(c_ftp.nlst('.'))
					if tail not in files:
						msj='File does not exists.'
						success=False
				success=True
				msj='OK'
			finally:
				c_ftp.quit()
		return ({'success':success,'msj':msj})

	def create_dir(self):
		if self.directory in (None,''):
			return ({'success':False,'msj':'Folder name required.'})
		c_ftp=self.ftp_conection()
		if type(c_ftp)!=ftplib.FTP:
			return ({'success':c_ftp['success'],'msj':c_ftp['msj'],'token':request.headers['token']})
		else:
			try:
				check_if_exist=self.check_existing()
				if check_if_exist['success']:
					msj='FTP folder already exists.'
					success=False
					#return ({'success':success,'msj':msj})
					path = os.path.normpath(self.directory)
					for x in path.split(os.sep):
						c_ftp.mkd(x)
						c_ftp.cwd(x)
				elif check_if_exist['success'] is False:
					path = os.path.normpath(self.directory)
					for x in path.split(os.sep):
						c_ftp.mkd(x)
						c_ftp.cwd(x)

				else:
					msj='Error executing command.'
					success=False		
			except ftplib.all_errors as e:
				data=e,currentFileName,currentFuncName()
				msj='Error triying to create FTP directory.'
				msj=tools.logHandler(data,msj)
				success=False
			else:
				msj='FTP directory created successfully.'
				success=True
			finally:
				c_ftp.quit()
		return ({'success':success,'msj':msj})
	
	def remove_dir(self):
		c_ftp=self.ftp_conection()
		if type(c_ftp)!=ftplib.FTP:
			return ({'success':c_ftp['success'],'msj':c_ftp['msj'],'token':request.headers['token']})
		check_if_exist=self.check_existing()
		if check_if_exist['success']:
			files = list(c_ftp.nlst(self.directory))
			abs_path=os.path.normpath(self.directory)+'/'
			for f in files:
				try:
					c_ftp.delete(abs_path+f)
				except Exception as e:
					c_ftp.rmd(abs_path+f)
			c_ftp.rmd(self.directory)
			msj='Folder removed successfully.'
			success=True
		elif check_if_exist['success'] is False:
			msj='FTP folder does not exists.'
			success=False
		else:
			success=False
		c_ftp.quit()
		return ({'success':success,'msj':msj})

	def move_to_ftp_directory(self,token,file,directory):
		c_ftp=self.ftp_conection()
		if type(c_ftp)!=ftplib.FTP:
			return ({'success':c_ftp['success'],'msj':c_ftp['msj'],'token':request.headers['token']})
		tmp_directory = "/".join(('/tmp',token,file))
		tmp_file = open(tmp_directory,'rb')
		try:
			c_ftp.cwd(directory)
			c_ftp.storbinary('STOR '+file, tmp_file)
		except Exception as e:
			data=e,currentFileName,currentFuncName()
			tools.logHandler(data)
			return False
		else:
			return True
		finally:
			c_ftp.quit()

	def upload_file(self):
		data=[]
		token=request.headers['token']
		if bool(request.files):
			file = tools.getPOSTParams('file')
			filename = secure_filename(file.filename)
			token=request.headers['token']
			c_ftp=self.ftp_conection()
			msj=None

			main_dir=self.directory
			self.directory=main_dir+filename
			check_if_exist=self.check_existing()
			self.directory=main_dir
			if check_if_exist['success'] and not tools.getPOSTParams('overwrite','False').lower() in ("yes", "true", "t", "1","si"):
				return ({'success':True,'msj':'File/folder already exist.','token':token,'data':main_dir+filename})
				
			if type(c_ftp)!=ftplib.FTP:
				return ({'success':c_ftp['success'],'msj':c_ftp['msj'],'token':token})
			else:
				try:
					c_ftp.cwd(self.directory)
				except Exception as e:
					try:
						dir_c=self.create_dir()
					except Exception as e:
						data=e,currentFileName,currentFuncName()
						tools.logHandler(data)
						return ({'success':dir_c['success'],'msj':dir_c['msj'],'token':token,'data':data})
				finally:
						c_ftp.quit()
						fm=FileManager().file_upload_ftp()
						if fm['success']:
							try:
								m_to_ftp=self.move_to_ftp_directory(token,filename,self.directory)
								abs_path=os.path.normpath(self.directory)+'/'+filename
							except Exception as e:
								data=e,currentFileName,currentFuncName()
								tools.logHandler(data)
								return ({'success':m_to_ftp['success'],'msj':m_to_ftp['msj'],'token':token,'data':data})
							else:
								msj='File uploaded successfully.'
								return ({'success':True,'msj':msj,'token':token,'data':abs_path})		
						else:
							return ({'success':fm['success'],'msj':fm['msj'],'token':token})
		else:
			msj='Undefined file.'
			return ({'success':False,'msj':msj,'token':token})

	def remove_file(self):
		c_ftp=self.ftp_conection()
		file = tools.getPOSTParams('file',None)
		if file in (None,'') or self.directory in (None,''):
			return ({'success':False,'msj':'Folder/File name required.'})
		if type(c_ftp)!=ftplib.FTP:
			return ({'success':c_ftp['success'],'msj':c_ftp['msj'],'token':request.headers['token']})
		check_if_exist=self.check_existing()
		if check_if_exist:
			files = list(c_ftp.nlst(self.directory))
			abs_path=os.path.normpath(self.directory)+'/'
			if file in files:
				c_ftp.delete(abs_path+file)
				msj='File removed successfully.'
				success=True
			else:
				msj='File does not exists.'
				success=False
		else:
			return ({'success':check_if_exist['success'],'msj':check_if_exist['msj'],'token':request.headers['token']})
		c_ftp.quit()
		return ({'success':success,'msj':msj})