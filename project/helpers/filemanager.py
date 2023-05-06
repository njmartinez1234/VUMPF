# -*- coding: utf-8 -*-
from project import app
from werkzeug.utils import secure_filename
import glob,os
import sys
import fnmatch
import shutil
from flask import request
import imp
import os.path

from project.config import constants as CONSTANTS
from project.helpers import tools


ALLOWED_EXTENSIONS = set(CONSTANTS.allowed_extesions)
app.config['MAX_CONTENT_LENGTH'] = CONSTANTS.file_max_size * 1024 * 1024
app.config['UPLOAD_FOLDER'] = CONSTANTS.file_save_default_path

currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name
currentFileName = os.path.basename(__file__)

class FileManager:
    def __init__(self,save_path=None,path=None,sort_by_ext='*',pattern=None,file=None,show_hidden=False,max_results=None,zip_files=False):
        imp.reload(CONSTANTS)
        self.ext=sort_by_ext
        self.pattern=pattern
        self.save_path=save_path
        self.path=path
        self.show_hidden=show_hidden
        self.max_results=max_results
        self.zip_files=zip_files
        if self.ext=='*':
            self.ext=''

    def allowed_file_extensions(self,filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def file_upload(self):
        success=None
        msj=None
        files_path=''
        files_dict=[]
        if self.save_path is not None:
            if not os.path.exists(self.save_path):
                msj='Directory not found.'
                success=False
                return ({'success':success,'msj':msj,'token':request.headers['token'],'dir':self.save_path})
            else:
                app.config['UPLOAD_FOLDER'] = self.save_path
        if bool(request.files):
            for rqst_files in request.files:
                if  rqst_files is None:
                    msj='File(s) not included in request.'
                    success=False
                    return ({'success':success,'msj':msj,'token':request.headers['token'],'data':[]})
                elif request.files[rqst_files].filename == '':
                    msj='Please, select a valid file.'
                    success=False
                    return ({'success':success,'msj':msj,'token':request.headers['token'],'data':[]})
                else:
                    file = request.files[rqst_files]
                    files_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    if file and self.allowed_file_extensions(file.filename):
                        filename = secure_filename(file.filename)
                        try:
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        except Exception as e:
                            data=e,currentFileName,currentFuncName()
                            msj='Error uploading file.'
                            msj=tools.logHandler(data,CONSTANTS.display_errors,msj)
                            success=False
                        else: 
                            msj='File(s) uploaded correctly.'
                            files_dict.append(files_path)
                            success=True
                        finally:
                            pass
                    else:
                        msj='One or more files has a invalid extension.'
                        success=False
                        return ({'success':success,'msj':msj,'token':request.headers['token'],'file':files_path})
        else:
            msj='File(s) not included in request.'
            success=False
        return ({'success':success,'msj':msj,'token':request.headers['token'],'file':files_dict})

    def file_upload_ftp(self):
        self.save_path="".join(("/tmp/",request.headers['token']))
        app.config['UPLOAD_FOLDER'] = self.save_path
        if 'file' not in request.files:
            return False
        elif request.files['file'].filename == '':
            return False
        else:
            file = request.files['file']
            if file is not None:
                if self.allowed_file_extensions(file.filename):
                    filename = secure_filename(file.filename)
                    try:
                        if not os.path.exists(app.config['UPLOAD_FOLDER']):
                            os.makedirs(app.config['UPLOAD_FOLDER'])
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    except Exception as e:
                        data=e,currentFileName,currentFuncName()
                        msj='Error creating FTP directory.'
                        msj=tools.logHandler(data,CONSTANTS.display_errors,msj)
                        success=False
                        return ({'success':success,'msj':msj})
                    else: 
                        success=True
                        return ({'success':success})
                else:
                    return({'success':False,'msj':'One or more files has a invalid extension.'})
            else:
                return({'success':False,'msj':'Unable to upload file.'})

    def create_directory(self):
        success=None
        msj=None
        try:
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            else:
                return ({'success':True,'msj':'The directory already exists.'})
        except Exception as e:
            data=e,currentFileName,currentFuncName()
            msj='Error creating directory.'
            msj=tools.logHandler(data,CONSTANTS.display_errors,msj)
            success=False
        else: 
            msj='Directory created successfully.'
            success=True
        finally:
                pass
        return ({'success':success,'msj':msj})

    def remove_directory(self):
        success=None
        msj=None
        try:
            shutil.rmtree(self.path)
        except Exception as e:
            data=e,currentFileName,currentFuncName()
            msj='Error deleting directory.'
            msj=tools.logHandler(data,CONSTANTS.display_errors,msj)
            success=False
        else: 
            msj='Directory deleted successfully.'
            success=True
        finally:
                pass
        return ({'success':success,'msj':msj})    

    def remove_file(self):
        success=None
        msj=None
        cfile=self.check_existing_file()
        if cfile['success']:
            try:
                os.remove(self.path)
            except Exception as e:
                data=e,currentFileName,currentFuncName()
                msj='Error deleting file.'
                msj=tools.logHandler(data,CONSTANTS.display_errors,msj)
                success=False
            else: 
                msj='File deleted successfully.'
                success=True
            finally:
                    pass
            return ({'success':success,'msj':msj})
        else:
            return ({'success':False,'msj':'The file '+self.path+' does not exist.'})

    def find_file(self):
        items=[]
        pattern = "*"+self.pattern.upper()+"*"
        for (dirpath, dirnames, filenames) in os.walk(self.path):
            for file in filenames:
                if not self.show_hidden and file.startswith('.'):
                    pass
                else:
                    if len(self.ext)>0:
                        if file.endswith(self.ext):
                            if fnmatch.fnmatch(file.upper(), pattern):
                                items.append(os.path.join(dirpath,file))
                    else:
                        if fnmatch.fnmatch(file.upper(), pattern):
                            items.append(os.path.join(dirpath,file))
                if len(items) == self.max_results:
                    return ({'success':True,'msj':'OK','data':items})
                else:
                    pass

        if len(items) > 0:
            return ({'success':True,'msj':'OK','data':items})
        return ({'success':False,'msj':'File(s) not found.'})
    
    def list_directory(self):
        success=None
        msj=None
        data={}
        items=[]
        dirs=[]
        files=[]
        if self.check_existing_dir() is False:
            msj='Error listing directory.'
            success=False
            return ({'success':success,'msj':msj})
        try:
            for f in os.listdir(self.path):
                if len(self.ext)>0:
                    if f.endswith(self.ext):
                        items.append(f)
                else:
                    items.append(f)

            if len(items) > 0:
                for item in items:
                    if not self.show_hidden and item.startswith('.'):
                        pass
                    else:
                        abs_path=os.path.normpath(self.path)+'/'+item
                        if os.path.isfile(abs_path):
                            files.append(abs_path)
                        else:
                            dirs.append(abs_path)
            data.update({'directories':dirs,'files':files})
        except Exception as e:
            data=e,currentFileName,currentFuncName()
            msj='Error listing directory.'
            msj=tools.logHandler(data,CONSTANTS.display_errors,msj)
            success=False
        else: 
            msj='OK'
            success=True
        finally:
            if self.zip_files:
                zip_resp=self.zip_files_fn(data)
                return zip_resp
        return ({'success':success,'msj':msj,'data':data})

    def zip_files_fn(self,data):
        from zipfile import ZipFile
        success=None
        msj=None
        files_to_zip=[]
        file_paths = []
        for items in data:
            if items=='files':
                for files_and_dirs in data[items]:
                    files_to_zip.append(files_and_dirs)
            else:
                for  full_path in data[items]:
                    for root, directories, files in os.walk(full_path): 
                        for filename in files: 
                            filepath = os.path.join(root, filename) 
                            file_paths.append(filepath)

        file_paths.extend(files_to_zip)
        zip_file=CONSTANTS.zip_file_default_path+'/'+CONSTANTS.zip_file_name
        try:
            zp=ZipFile(zip_file,'w')
        except Exception as e:
            data=e,currentFileName,currentFuncName()
            msj='Error creating zip file.'
            msj=tools.logHandler(data,CONSTANTS.display_errors,msj)
            return ({'success':False,'msj':msj})
        else:
            with zp as zip: 
                for file in file_paths:
                    try:
                        zip.write(file)
                    except Exception as e:
                        data=e,currentFileName,currentFuncName()
                        msj='Error compressing file.'
                        msj=tools.logHandler(data,CONSTANTS.display_errors,msj)
                        success=False
                    else:
                        msj='OK'
                        success=True
                    finally:
                        pass
        finally:
            pass
        return ({'success':success,'msj':msj,'data':CONSTANTS.zip_file_name})

    def check_existing_file(self):
        success=None
        msj=None
        try:
            file=os.path.isfile(self.path)
        except Exception as e:
            data=e,currentFileName,currentFuncName()
            msj='Error listing directory.'
            msj=tools.logHandler(data,CONSTANTS.display_errors,msj)
            success=False
        else:
            if file:
                msj="File exist."
                success=True
            else:
                msj="File doesn't exist."
                success=False
        finally:
            pass
        return ({'success':success,'msj':msj})

    def check_existing_dir(self):
        try:
            if not os.path.exists(self.path):
                return False
            else:
                return True
        except Exception as e:
            data=e,currentFileName,currentFuncName()
            tools.logHandler(data,CONSTANTS.display_errors)