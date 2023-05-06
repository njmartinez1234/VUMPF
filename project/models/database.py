# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
import sqlalchemy
import pymysql
from pymongo import MongoClient
import random, string
from project.helpers import serializer
import re
import datetime
import json
import sys
import os

from project import app
from project.helpers import tools
from project.config import constants as CONSTANTS

currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name
currentFileName = os.path.basename(__file__)

class db:
	def __init__(self,query='',active_group= 'default',order=False,show_db_name=False,result_type=2):
		self.connection=None
		self.trans=None
		self.close =True
		self.query=query
		self.order=order
		self.active_group=active_group
		self.show_db_name=show_db_name
		self.result_type=result_type
		url_db=''
		self.mongo_session=False
		self.db_msj=''
		engine=None
		configdb = json.loads(open(CONSTANTS.project_root+'/config/database.json').read())
		active_db = (configdb['active_group']['default'])
		self.db_alias=''

		if active_group != 'default':
			active_db=active_group
		if active_group in configdb:
			self.db_msj='Error conecting to database with the provided settings.'
			self.connection=None
		else:
			if configdb['db_connections'][active_db]['driver']=='sqlite':
				url_db = '{0}:///{1}:'.format(configdb['db_connections'][active_db]['driver'],configdb['db_connections'][active_db]['dbpath'])
			elif configdb['db_connections'][active_db]['driver']=='mongodb':
					url_db = '{0}://{1}'.format(configdb['db_connections'][active_db]['driver'],configdb['db_connections'][active_db]['dburl'])
					db_name = configdb['db_connections'][active_db]['bdname']
					self.mongo_session=True
			else:
				try:
					url_db = '{0}://{1}:{2}@{3}:{4}/{5}'.format(configdb['db_connections'][active_db]['driver'],configdb['db_connections'][active_db]['user'],configdb['db_connections'][active_db]['password'],configdb['db_connections'][active_db]['host'],configdb['db_connections'][active_db]['port'],configdb['db_connections'][active_db]['bdname'])
				except Exception as e:
					data=e,currentFileName,currentFuncName()
					msj='Error conecting to database'
					msj=tools.logHandler(data,msj)
					return ({"success": False,"msg":msj})
			if self.mongo_session:
				try:
					db = MongoClient(url_db)
					db.server_info()
				except Exception as e:
					data=e,currentFileName,currentFuncName()
					msj='Error conecting to database'
					msj=tools.logHandler(data,msj)
					self.db_msj=msj
					self.connection=None
					return None
				else:
					self.connection = db[db_name]
			else:
				try:
					db = create_engine(url_db)
					engine = db.engine
					self.connection = engine.connect()
				except Exception as e:
					data=e,currentFileName,currentFuncName()
					msj='Error connecting to database.'
					msj=tools.logHandler(data,msj)
					self.db_msj=msj
					self.connection=None
					return None
					
		if 'alias' in configdb['db_connections'][active_db]:
			self.db_alias=configdb['db_connections'][active_db]['alias']
		else:
			self.db_alias=self.active_group

	def mongo_execute(self,collection):
		if self.connection is None:
			return ({'success':False,'msg':self.db_msj})
		elif not self.mongo_session:
			return ({'success':False,'msg':'Error connecting to database.'})
		else:
			if collection=='':
				return ({'success':False,'msg':'Collection names cannot be empty'})
			mycol = self.connection[collection]
			return mycol

	def execute(self):
		if self.connection is None:
			return ({'success':False,'msg':self.db_msj})
		else:
			try:
				if self.close:
					self.trans = self.connection.begin()
				result = self.connection.execute(self.query)
			except Exception as e:
				data=e,currentFileName,currentFuncName()
				if self.close:
					self.trans.rollback()
					msj='Unable to run query.'
					msj=tools.logHandler(data,msj)
				return ({"success": False,"msg":msj})
			else: 
				if self.close:
					self.trans.commit()
					try:
						result = serializer.proxytodict(result,self.order)
					except Exception as e:
						data=e,currentFileName,currentFuncName()
						msj='Query did not returned any value.'
						dataArray={}			
						if self.result_type in (1,2) :
							if self.show_db_name:
								dataArray.update({self.active_group : msj})
							else:
								dataArray.update({None:msj})
						else:
							return ({"success": False,"msg":"Invalid data result."})
						msj=tools.logHandler(data,msj)
						return ({"success": True,"msg":msj,'data':dataArray})
				
				dataArray=None
				if self.show_db_name:
					counter=0
					for x in result:
						result[counter].update({'db_name':self.active_group})
						result[counter].move_to_end('db_name', last=False)
						counter+=1
				if self.result_type == 1: 
					dataArray={}
					dataArray.update({self.active_group : result})
				elif self.result_type == 2:
					dataArray=[]
					dataArray.extend(result)
				else:
					return ({"success": False,"msg":"Invalid data arrangement mode."})
				return ({"success": True,"msg":'OK',"data":dataArray})
			finally:
				if self.close:			
					self.connection.detach()
					self.connection.close()
	
	def row_query(self):
		"""Query return one row.

		Params:
		query -- String query database
		order -- Boolean order, Default False
		"""
		if self.connection is None:
			return ({'success':False,'msg':self.db_msj})
		else:
			try:
				if self.close:
					self.trans = self.connection.begin()
				result = self.connection.execute(self.query)
				result = serializer.proxytodict(result,self.order)
			except Exception as e:
				data=e,currentFileName,currentFuncName()
				msj='Error during query execution.'
				msj=tools.logHandler(data,msj)
				if self.close:
					self.trans.rollback()
				return ({'success':False,'msg':msj})
			else: 
				if self.close:
					self.trans.commit()
				return ({"success": True,"msg":'OK',"data":[] if not result else result[0]})
			finally:
				if self.close:			
					self.connection.detach()
					self.connection.close()

	def execute_transaction(self):
		"""execute Query .

		Params:
		query -- String query database
		"""
		if self.connection is None:
			return False
		else:
			try:
				if self.close:
					self.trans = self.connection.begin()
				self.connection.execute(self.query)
			except Exception as e:
				data=e,currentFileName,currentFuncName()
				msj=tools.logHandler(data,msj)
				if self.close:
					self.trans.rollback()
				return ({"success": False,"msg":msj})
				#return False
			else: 
				if self.close:
					self.trans.commit()
				return True
			finally:
				if self.close:			
					self.connection.detach()
					self.connection.close()

	def begin(self):
		self.trans = self.connection.begin()
		self.close =False
	
	def rollback(self):
		self.trans.rollback()
		self.close =True
		self.connection.detach()
		self.connection.close()
	
	def commit(self):
		self.trans.commit()
		self.close =True
		self.connection.detach()
		self.connection.close()		
