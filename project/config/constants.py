# -*- coding: utf-8 -*-
import datetime
import json
import os

#Server settings
project_root=os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..',''))
server_port=8082
#-----If server_ip constant is None, it will take local network ip
server_ip='localhost'

#Mailer settings
mailer_adress=''
mailer_password=''
smtp_server=''
smtp_port=447

#FTP settings
ftp_host='localhost'
ftp_port=21
ftp_user='ftp_user'
ftp_pass='ftp_password'
ftp_root_route='/'

#Folder settings
default_folder='static/'
file_save_default_path=project_root+'/'+default_folder

#CSV Manager setting
csv_default_path=file_save_default_path
csv_delimiter=';'
csv_file_name='csv_file_'+datetime.datetime.now().strftime("%Y%m%d%M%S")+'.csv'

#File settings
allowed_extesions=['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','csv','mp4','mp3']
file_max_size=10 #Megabytes
zip_file_default_path=file_save_default_path
zip_file_name='zip_'+datetime.datetime.now().strftime("%Y%m%d%M%S")+'.zip'

#Recapcha
recaptcha_private_key = '6LcwYyUUAAAAA4541d8zvFiQGGJxCfmO0U-rX_av'

#User Session time in Seconds
session_time=30

#Amazon S3 authication
s3_region='us-east-1'
s3_access_key='ABCDEFGHIJKLMNOPQ'
s3_secret='UVpSd4eb6pbff4Ql6Xtg8q8/kyhjxrXgtIzXvKhQ'

display_errors=False