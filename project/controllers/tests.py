# -*- coding: utf-8 -*-
#Flask packages
from flask import request
from flask import Blueprint
from flask import session
from flask.json import jsonify
from flask import render_template
import json as simplejson

#Vump packages
from project import app
from project.config import constants as CONSTANTS
from project.models.database import db
from project.helpers import tools
from project.helpers.custom_decorators import *
from project.helpers.filemanager import FileManager
from project.helpers.ftp import FtpManager
from project.helpers.csv import CsvManager
from project.helpers.emailmanager import EmailManager
from project.helpers.threadmanager import *

#S3
from project.libraries.S3Man import S3Manger

#Building packages
import datetime
import threading
import csv
import os
import time


func=os.path.splitext(os.path.basename(__file__))[0]
tests = Blueprint(func, __name__)
@tests.route('/', methods=['GET','POST'])
#@authorize
def test_index():
    return ('url_root:'+str(request.url_root)+'base_url:'+str(request.base_url))


@tests.route('/s3',methods=['GET','POST'])
#S3 files manager
#[op] = Operation type [list_buckets,list_files,upload_file,delete_file,download_file,tmp_download_url]
#[bucket_name] = Bucket name
#[file_name] = Bucket Filename 
#[file_path] = Local file path
#[exp_time] = temp download file url expiration time ms
#URL http://localhost:8082/tests/s3?op=list_buckets
#@authorize
def main_s3():
    path=request.args.get('op')
    bucket_name=request.args.get('bucket_name','')
    exp_time=tools.getPOSTParams('exp_time',3600)
    file_name=tools.getPOSTParams('file_name',None)
    file_path=tools.getPOSTParams('file_path',None)
    override_file=tools.getPOSTParams('override_file','False').lower() in ("yes", "true", "t", "1","si")
    #oneworld-listings-images
    if path=='list_buckets':
        resut=S3Manger().list_buckets()
    elif path=='list_files':
        resut=S3Manger(file_name=file_name,file_path=None,bucket=bucket_name,override=None).list_objects()
    elif path=='upload_file':
        resut=S3Manger(file_name=file_name,file_path=file_path,bucket=bucket_name,override=override_file).upload_file()
    elif path=='delete_file':
        resut=S3Manger(file_name=file_name,bucket=bucket_name).delete_file()
    elif path=='download_file':
        resut=S3Manger(file_path=None,file_name=file_name,bucket=bucket_name).download_file()
    elif path=='tmp_download_url':
        path=request.args.get('op')
        resut=S3Manger(file_name=file_name,bucket=bucket_name,exp_time=exp_time).temp_download_url()
    else:
        return 'NO permitido'
    return jsonify(resut)


@tests.route('/render_html_template')
#Render templates function
#URL http://localhost:8082/tests/render_html_template
def render_html_template():
    return render_template('welcome_mail_template.html',data=None)


@tests.route('/send_html_template')
#Send email html template
#[template] = This content can be an html template.
#[data] = This is data for template.html.
#[mail_to[]] = Recipts.
#[subject] = Maile Subject.
def renderhtml_fn():
    query = """ SELECT * FROM public.table; """
    response=db(query=query).execute()
    if not response['success']:
        return response
    email = EmailManager(template="Template.html",data=response['data'],mail_to='mail1@mail.com,mail2@mail.com',subject='Mail Subject')
    email.email_send()


@tests.route('/email_send')
#Email send
#[template] = This content can be an html template.
#[data] = This is data for template.html.
#[mail_to[]] = Recipts.
#[subject] = Maile Subject.
#[attachment] = File path to attach files to email
def mailer():
    email = EmailManager(template="welcome_mail_template.html",data=None,mail_to=['njmartinez.construsenales@gmail.com','njmartinez0820@gmail.com'],subject='Mail Subject',attachment=None)
    resut=email.email_send()
    return jsonify({'success':True,'msj':resut,'data':None})


@tests.route('/mongo',methods=['GET'])
#Mongo db 
#[order][GET]=Order result data
#[active_group][GET]=Data base active group
#[collection]=Mongo collection name
#[expor_csv]=Export data to csv
#URL http://localhost:8082/tests/mongo?active_group=database4&collection=properties&order=True&expor_csv=True
#@authorize
def mongo_fn():
    from project.helpers import serializer

    active_group=request.args.get('active_group')
    collection=request.args.get('collection')
    expor_csv=tools.getPOSTParams('expor_csv','False').lower() in ("yes", "true", "t", "1","si")
    order=tools.getPOSTParams('order','False').lower() in ("yes", "true", "t", "1","si")

    response=db(order=order,active_group=active_group).mongo_execute(collection=collection)
    if not response['success']:
        return response
    result = response.find({},{'_id':1}).sort('ModificationTimestamp',-1).skip(0).limit(1000)
    result = serializer.proxytodict(result,True)

    if expor_csv:
        csv = CsvManager(data=result,file_path='/tmp/csv_path/',file_name=None,delimiter=';',index=False,overwrite=True)
        return jsonify(csv.data_to_csv())

    return ({"success": True,"msg":'OK',"data":result})


@tests.route('/crud',methods=['GET'])
#SELECT,UPDATE,INSERT table,funtions,views
#@authorize
def select_fn():
    #[order][GET]=Order result data
    #[active_group][GET]=Data base active group
    #[query][GET]=Query string

    #URL http://localhost:8082/tests/crud?active_group=database1&expor_csv=True&show_db_name=False&order=True&result_type=2
    
    active_group=request.args.get('active_group')
    expor_csv=tools.getPOSTParams('expor_csv','False').lower() in ("yes", "true", "t", "1","si")
    show_db_name=tools.getPOSTParams('show_db_name','False').lower() in ("yes", "true", "t", "1","si")
    order=tools.getPOSTParams('order','False').lower() in ("yes", "true", "t", "1","si")
    result_type=request.args.get('result_type')

    query = """ select * from pg_stat_activity limit 10 """
    response=db(query=query,order=order,active_group=active_group,show_db_name=show_db_name,result_type=int(result_type)).execute()
    results=[]
    if response['success']:
        results.append(response['data'])
    else:
        return jsonify(response)

    if expor_csv:
        csv = CsvManager(data=results,file_name=None,delimiter=';',index=False,overwrite=True)
        return jsonify(csv.data_to_csv())
    return jsonify(response)

        
@tests.route('/crud_multi_db')
#Multi DataBase CRUD
#[show_db_name][GET]=Show data base name in result
#[result_type][GET]=Result data type, 1=Show result keys - 2=Do not show result keys
#[daemon][GET]=Demonize treaths
#URL http://localhost:8082/tests/crud_multi_db?result_type=2&expor_csv=True&show_db_name=True&order=True&daemon=True

#@authorize
@runing_threads
def select_multi_db_fn():
    expor_csv=tools.getPOSTParams('expor_csv','False').lower() in ("yes", "true", "t", "1","si")
    show_db_name=tools.getPOSTParams('show_db_name','False').lower() in ("yes", "true", "t", "1","si")
    order=tools.getPOSTParams('order','False').lower() in ("yes", "true", "t", "1","si")
    daemon=tools.getPOSTParams('daemon','False').lower() in ("yes", "true", "t", "1","si")
    result_type=request.args.get('result_type')
    
    dbs=['database1','database2']
    query=""" SELECT * from table """
    dataArray=[]
    thread_pool=[]
    
    for db_name in dbs:
        now = datetime.datetime.now()
        for x in range(0,100):
            result = EncodeThread(name='t_'+tools.getToken(5)+'_'+db_name, target=query_exc, args = (db_name,query,order,show_db_name,result_type)).pool()
            thread_pool.append(result)
    dataArray=StartThread(thread_pool=thread_pool,max_threads=10,daemon=daemon).run()
        
    if expor_csv:
        csv = CsvManager(data=dataArray,file_name=None,delimiter=';',index=False,overwrite=True)
        return jsonify(csv.data_to_csv())
    else:
        return jsonify(dataArray)

def query_exc(db_name,query,order,show_db_name,result_type,out_queue):
    response=db(active_group=db_name,query=query,order=order,show_db_name=show_db_name,result_type=int(result_type)).execute()
    if response['success'] and response['data'] is not None:
        out_queue.put(response['data'])
    else:
        out_queue.put(None)
        pass


@tests.route('/create_directory', methods=['POST'])
#Create directory
#[path][POST]=Path to create
#URL http://localhost:8082/tests/create_directory
#@authorize
def create_directory():
    path=request.args.get('path')
    file = FileManager(path=path).create_directory()
    return jsonify(file)

@tests.route('/remove_directory', methods=['POST'])
#Remove directory and its contents
#[path][POST] =Path to remove
#URL http://localhost:8082/tests/remove_directory
#@authorize
def remove_directory():
    path=tools.getPOSTParams('path',None)
    file = FileManager(path=path).remove_directory()
    return jsonify(file)

@tests.route('/upload_file', methods=['POST'])
#Upload file to certain path
#[save_path][POST]=Path to save file
#[file][POST]=File
#URL http://localhost:8082/tests/upload_file?save_path=/tmp/
#@authorize
def upload_file():
    save_path=tools.getPOSTParams('save_path','/tmp/')
    file = FileManager(save_path=save_path).file_upload()
    return jsonify(file)

@tests.route('/remove_file', methods=['POST'])
#Upload file to certain path
#[file_path][POST]=File to remove
#URL http://localhost:8082/tests/remove_file?file_path=/tmp/file.txt
#@authorize
def remove_file():
    file_path=tools.getPOSTParams('file_path',None)
    file = FileManager(path=file_path).remove_file()
    return jsonify(file)
    
@tests.route('/list_dir_files', methods=['POST','GET'])
#List files of certain path
#[path][POST]=Directory path
#[sort_by_ext][POST]=Sort by file extension
#[show_hidden][POST]=Show hidden files
#[zip_files][POST]=Zip listed files or folder
#URL http://localhost:8082/tests/list_dir_files?path=/tmp/&sort_by_ext=png&show_hidden=True
#@authorize
def list_directory_files():
    path=tools.getPOSTParams('path','/')
    sort_by_ext=tools.getPOSTParams('sort_by_ext','*')
    show_hidden=tools.getPOSTParams('show_hidden','False').lower() in ("yes", "true", "t", "1","si")
    zip_files=tools.getPOSTParams('zip_files','False').lower() in ("yes", "true", "t", "1","si")
    dir_content = FileManager(path=path,sort_by_ext=sort_by_ext,show_hidden=show_hidden,zip_files=zip_files).list_directory()
    return jsonify(dir_content)


@tests.route('/find_files', methods=['POST','GET'])
#Find files in certain path
#[path][POST]=Directory path
#[pattern][POST]=Partial file name
#[sort_by_ext][POST]=Sort by file extension
#[show_hidden][POST]=Show or not hidden
#[max_results][POST]=Show number of results
#URL http://localhost:8082/tests/find_files?path=/tmp/&sort_by_ext=*&show_hidden=False&pattern=filename&max_results=5
#@authorize
def find_files():
    path=request.args.get('path')
    pattern=request.args.get('pattern')
    show_hidden=tools.getPOSTParams('show_hidden','False').lower() in ("yes", "true", "t", "1","si")
    sort_by_ext=request.args.get('sort_by_ext')
    max_results=request.args.get('max_results')
    dir_content = FileManager(path=path,pattern=pattern,show_hidden=show_hidden,sort_by_ext=sort_by_ext,max_results=max_results).find_file()
    return jsonify(dir_content)


@tests.route('/ftp_list_dir', methods=['POST','GET'])
#List FTP dir / Method=GET/
#[directory][POST][GET] = FTP directory
#URL http://localhost:8082/tests/ftp?directory=Folder
#@authorize
def ftp_list_dir():
    ftp_response=FtpManager().list_diretory()
    return jsonify(ftp_response)

@tests.route('/ftp_create_dir', methods=['POST','GET'])
#List FTP dir / Method=GET/
#[directory][POST][GET] = FTP directory
#URL http://localhost:8082/tests/ftp_create_dir?directory=Folder
#@authorize
def ftp_create_dir():
    new_dir=request.args.get('directory',None)
    ftp_response=FtpManager(directory=new_dir).create_dir()
    return ftp_response

@tests.route('/ftp_remove_dir', methods=['POST','GET'])
#Remove FTP dir / Method=GET/
#[directory][POST][GET] = FTP directory
#URL http://localhost:8082/tests/ftp_remove_dir?directory=Folder
#@authorize
def ftp_remove_dir():
    new_dir=request.args.get('directory',None)
    ftp_response=FtpManager(directory=new_dir).remove_dir()
    return ftp_response

@tests.route('/ftp_upload_file', methods=['POST'])
#Upload file to FTP / Method=POST/
#[directory][POST][GET] = FTP directory
#[file][POST] = File to upload
#URL http://localhost:8082/tests/ftp_upload_file
def ftp_upload_file():
    ftp_response=FtpManager().upload_file()
    return ftp_response

@tests.route('/ftp_remove_file', methods=['POST','GET'])
#Delete file on FTP / Method=POST/ 
#[directory][POST][GET] = FTP directory
#[file][POST][GET] = File to remove
#URL http://localhost:8082/tests/ftp_remove_file
def ftp_remove_file():
    ftp_response=FtpManager().remove_file()
    return ftp_response

@tests.route('/csv_create')
#Create CSV from table
#[data[]] = Data to feed csv
#[file_path] = Path to save csv file
#[file_name] = csv File name
#[delimiter] = csv delimiter [',',';','|']
#[index] = [True,False]
#[overwrite] = [True,False] Overwrite existing csv file
#URL http://localhost:8081/tests/csv_create
#@authorize
def csv_create_fn():
    query = """ SELECT * from table """
    response=db(query=query,active_group='dor').execute()
    csv = CsvManager(data=response['data'],file_path='/tmp/csv_path/',file_name=None,delimiter=';',index=False,overwrite=True)
    return jsonify(csv.data_to_csv())


@tests.route('/csv_read', methods=['POST'])
#Read csv file
#[file_path][POST] = csv File route
#[delimiter][POST] = csv File delimiter
#[skip_header][POST] = Skip csv # of header lines (0,1)
#URL http://localhost:8082/tests/csv_read?file_path=/home/user/csv_file.csv&delimiter=;&skip_header=0
#@authorize
def csv_read_fn():
    from project.helpers import serializer
    file_path=request.args.get('file_path')
    delimiter=request.args.get('delimiter')
    skip_header=request.args.get('skip_header')
    response=CsvManager(file_path=file_path,delimiter=delimiter,skip_header=int(skip_header)).read()
    if response['success']:
        csv_data=response['data'].to_dict()
        result = serializer.proxytodict(csv_data,True)
        return jsonify({'success':True,'data':result})
    else:
        return jsonify({'success':True,'msj':'Unable to read CSV file.'})

@tests.route('/multi_threading')
#Multi thread task manager
#[daemon] = Demonize task on server
#[workers] = Number of workers 
#@authorize
@runing_threads
def main():
    daemon=tools.getPOSTParams('daemon','False').lower() in ("yes", "true", "t", "1","si")
    workers=tools.getPOSTParams('workers',1)
    dataArray=[]
    thread_pool=[]
        
    for iteration in range(0,10):
        result = EncodeThread(name='t_name:'+tools.getToken(5), target=function, args = (10,)).pool()
        thread_pool.append(result)
    dataArray=StartThread(thread_pool=thread_pool,max_threads=int(workers),daemon=daemon).run()
    return jsonify({'success':True,'data':dataArray})

def function(arg,out_queue):
    for loop in range(0,arg):
        print("Fun Working {}".format(loop))
        time.sleep(10)
    out_queue.put('fun finished')


@tests.route('/zip',methods=['GET','POST'])
#[path] = Path to folder or file to compress
#[sort_by_ext] = Filter by file extension
#[show_hidden] = Include hidden files (linux)
#URL http://localhost:8082/tests/zip?path=/tmp/&sort_by_ext=jpeg
#@authorize
def zip():
    from zipfile import ZipFile
    path=tools.getPOSTParams('path','/')
    sort_by_ext=tools.getPOSTParams('sort_by_ext','*')
    show_hidden=tools.getPOSTParams('show_hidden','False').lower() in ("yes", "true", "t", "1","si")
    dir_content = FileManager(path=path,sort_by_ext=sort_by_ext,show_hidden=show_hidden).list_directory()
    files_to_zip=[]

    for items in dir_content['data']:
        for files_and_dirs in dir_content['data'][items]:
            files_to_zip.append(files_and_dirs)
    file_paths = []
    
    for  direct in files_to_zip:
        for root, directories, files in os.walk(direct):
            for filename in files: 
                filepath = os.path.join(root, filename) 
                file_paths.append(filepath)

    with ZipFile('/tmp/my_python_files.zip','w') as zip: 
        for file in file_paths: 
            zip.write(file) 
            
    return jsonify({'success':True,"msg":'OK','data':'/tmp/my_python_files.zip'})
