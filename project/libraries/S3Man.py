import sys
import os
from project import app
from project.helpers.filemanager import FileManager
from project.config import constants as CONSTANTS
from project.helpers import tools
import imp
import boto3

from project import app
from project.helpers.filemanager import FileManager

currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name
currentFileName = os.path.basename(__file__)

class S3Manger:
    def __init__(self,file_name=None,file_path=None,bucket=None,override=False,exp_time=60):
        imp.reload(CONSTANTS)

        self.data=''
        self.connection=None
        self.s3_msj=''
        self.file_name=file_name
        self.file_path=file_path
        self.override=override
        self.exp_time=exp_time

        self.region_name=CONSTANTS.s3_region
        self.aws_access_key_id=CONSTANTS.s3_access_key
        self.aws_secret_access_key=CONSTANTS.s3_secret
        self.bucket=bucket

        try:
            s3 = boto3.client("s3", 
                              region_name=self.region_name, 
                              aws_access_key_id=self.aws_access_key_id, 
                              aws_secret_access_key=self.aws_secret_access_key)
        except Exception as e:
            data=e,currentFileName,currentFuncName()
            msj='Error conecting to S3, please check your credentials'
            msj=tools.logHandler(data,CONSTANTS.display_errors,msj)
            self.s3_msj=msj
            self.connection=None
        else:
            self.connection = s3

    def list_buckets(self):
        if self.connection is None:
            return ({'success':False,'msg':self.s3_msj})
        else:
            try:
                bucket_response = self.connection.list_buckets()
            except Exception as e:
                data=e,currentFileName,currentFuncName()
                msj='Unable to list S3 buckets.'
                msj=tools.logHandler(data,CONSTANTS.display_errors,msj)
                return ({'success':False,'msj':msj})
            else:
                buckets = bucket_response["Buckets"]
                b_names=[]
                for itmes in buckets:
                    b_names.append(itmes['Name'])
                return ({"success": True,"data":b_names})
            finally:
                pass

    def list_objects(self):
        if self.connection is None:
            return ({'success':False,'msg':self.s3_msj})
        else:
            try:
                response = self.connection.list_objects(Bucket=self.bucket,MaxKeys=10, Prefix=self.file_name)
            except Exception as e:
                data=e,currentFileName,currentFuncName()
                msj='Unable to list objects, you may like to try connecting using another region name.'
                msj=tools.logHandler(data,CONSTANTS.display_errors,msj)
                return ({'success':False,'msj':msj})
            else:
                if 'Contents' in response:
                    return ({"success": True,"data": response['Contents']})
                return ({"success": False,"msj": 'File does not exist.'})

    def upload_file(self):
        if self.connection is None:
            return ({'success':False,'msg':self.s3_msj})
        else:
            file = FileManager(path=self.file_path).check_existing_file()
            if file['success']:
                self.file_name=os.path.split(self.file_path)[1]
                if not self.override:
                    if self.list_objects()['success']:
                        return ({'success':False,'msg':'File already exist.'})
                try:
                    self.connection.upload_file(Filename=self.file_path, Bucket=self.bucket, Key=self.file_name)
                except Exception as e:
                    data=e,currentFileName,currentFuncName()
                    msj='Error uploading file.'
                    msj=tools.logHandler(data,CONSTANTS.display_errors,msj)
                    return ({'success':False,'msj':msj})
                else:
                    return ({"success": True,"msj":'File uploaded successfully.'})
            return file

    def delete_file(self):
        if self.connection is None:
            return ({'success':False,'msg':self.s3_msj})
        else:
            if self.list_objects()['success']:
                try:
                    self.connection.delete_object(Bucket=self.bucket, Key=self.file_name)
                except Exception as e:
                    data=e,currentFileName,currentFuncName()
                    msj='Error uploading file.'
                    msj=tools.logHandler(data,CONSTANTS.display_errors,msj)
                    return ({'success':False,'msj':msj})
                else:
                    return ({"success": True,"msj":'File deleted successfully.'})
            else:
                return (self.list_objects())

    def download_file(self):
        if self.connection is None:
            return ({'success':False,'msg':self.s3_msj})
        else:
            if self.list_objects()['success']:
                try:
                    if self.file_path is None:
                        self.file_path=CONSTANTS.file_save_default_path+self.file_name
                    self.connection.download_file(Filename=self.file_path, Bucket=self.bucket, Key=self.file_name)
                except Exception as e:
                    data=e,currentFileName,currentFuncName()
                    msj='Error downloading file.'
                    msj=tools.logHandler(data,CONSTANTS.display_errors,msj)
                    return ({'success':False,'msj':msj})
                else:
                    return ({"success": True,"msj":'File downloaded successfully.','data':self.file_path})
            else:
                return (self.list_objects())

    def create_bucket(self):
        if self.connection is None:
            return ({'success':False,'msg':self.s3_msj})
        else:
            pass

    def temp_download_url(self):
        if self.connection is None:
            return ({'success':False,'msg':self.s3_msj})
        else:
            try:
                url=self.connection.generate_presigned_url('get_object',Params={'Bucket': self.bucket,'Key': self.file_name},ExpiresIn=self.exp_time)
            except Exception as e:
                data=e,currentFileName,currentFuncName()
                msj='Error generating url.'
                msj=tools.logHandler(data,CONSTANTS.display_errors,msj)
                return ({'success':False,'msj':msj})
            return ({"success": True,"data":url})