import sys
import os

import pandas
import imp
from flask import request

from project import app
from project.helpers.filemanager import FileManager
from project.config import constants as CONSTANTS
from project.helpers import tools

import csv
from collections import defaultdict
#You can use all this Pandas read_csv options:
# pandas.read_csv(filepath_or_buffer, sep=', ', delimiter=None, header='infer', names=None, 
#               index_col=None, usecols=None, squeeze=False, prefix=None, mangle_dupe_cols=True, 
#               dtype=None, engine=None, converters=None, true_values=None, false_values=None, 
#               skipinitialspace=False, skiprows=None, nrows=None, na_values=None, keep_default_na=True, 
#               na_filter=True, verbose=False, skip_blank_lines=True, parse_dates=False, infer_datetime_format=False, 
#               keep_date_col=False, date_parser=None, dayfirst=False, iterator=False, chunksize=None, 
#               compression='infer', thousands=None, decimal=b'.', lineterminator=None, quotechar='"', 
#               quoting=0, escapechar=None, comment=None, encoding=None, dialect=None, tupleize_cols=None, 
#               error_bad_lines=True, warn_bad_lines=True, skipfooter=0, doublequote=True, 
#               delim_whitespace=False, low_memory=True, memory_map=False, float_precision=None)
#More info: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html
currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name
currentFileName = os.path.basename(__file__)

class CsvManager:
    def __init__(self,data=None,file_path=CONSTANTS.csv_default_path,file_name=None,delimiter=CONSTANTS.csv_delimiter,index=False,overwrite=False,skip_header=0):
            imp.reload(CONSTANTS)
            self.data=data
            self.skip_header=skip_header
            self.file_name=file_name
            self.delimiter=delimiter
            self.overwrite=overwrite
            self.index=index
            if file_path is not None:
                self.file_path=file_path
            if file_name is None or file_name=='':
                self.file_name=CONSTANTS.csv_file_name

    def data_to_csv(self):
        file_path_name=self.file_path+self.file_name
        uri_path=request.url_root+CONSTANTS.default_folder
        file_check = FileManager(path=file_path_name).check_existing_file()
        if file_check['success']:
            if not self.overwrite:
                return ({'success':False,'msj':'The file already exists.'})
        else:
            mkdir=FileManager(path=self.file_path).create_directory()
            if mkdir['success']:
                pass
            else:
                return ({'success':False,'msj':mkdir['msj']})
        if self.data is not None and len(self.data)>0:
            new_data=[]
            if type(self.data)==list and type(self.data[0])==dict:
                for items in self.data:
                    documents=list(items.items())
                    counter=0
                    for k,v in documents:
                        for sk in items[k]:
                            new_data.append(dict(items[k][counter]))
                            counter+=1
            elif type(self.data)==dict:
                for items in self.data:
                    new_data.append(dict(self.data[items]))                
            else:
                try:
                    self.data[0][0]
                except Exception as e:
                    for items in self.data:
                        for items2 in items:
                            new_data.append(items2)
                else:
                    for items in self.data:
                        for val in items:
                            new_data.append(dict(val))

            self.data=new_data
            df = pandas.DataFrame(data=self.data)
            try:
                df.to_csv(file_path_name, sep=self.delimiter,index=self.index)
            except Exception as e:
                data=e,currentFileName,currentFuncName()
                msj='Unable to save file.'
                msj=tools.logHandler(data,msj)
                return ({'success':False,'msj':msj})
            else:
                pass
        else:
            return ({'success':False,'msj':'Data is empty.'})
        #return ({'success':True,'msj':'File created successfully.','data':[uri_path+self.file_name]})
        return ({'success':True,'msj':'File created successfully.','data':[file_path_name]})

    def read(self):
        file_check = FileManager(path=self.file_path).check_existing_file()
        if file_check['success']:
            try:
                data = pandas.read_csv(self.file_path,sep=self.delimiter,skiprows=self.skip_header,skip_blank_lines=True)
            except Exception as e:
                data=e,currentFileName,currentFuncName()
                msj='Failed to open requested file.'
                msj=tools.logHandler(data,msj)
                return ({'success':False,'msj':msj})
            else:
                return ({'success':True,'data':data,'msj':'OK'})
        else:
            return ({'success':False,'msj':'Can\'t find the requested file.'})