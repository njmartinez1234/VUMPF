# -*- coding: utf-8 -*-from project.helpers import tools
import hashlib
import random, string
from flask import session
from flask import request
import json
import urllib.request as ur
import inspect
import sys
from project.config import constants as CONSTANTS
from project import app

def computeMD5hash(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()

def getToken(longitud):
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(longitud))

def getPOSTParams(key,value=None):
    return request.args.get(key) if key in request.args else (request.form[key] if key in request.form else (request.files[key] if key in request.files else value))

def notEmpty(s):
    return bool(s and s.strip())

def clearSession():
    try:
        session.clear()
        return ({"success":True,"msj":'Session finished.'})
    except Exception:
        return ({"success":False,"msj":'Error finishing session.'})

def logHandler(error_desc,msj='',show_l=app.config['DISPLAY_ERRORS']):
    print(error_desc,msj,show_l)
    line_num=inspect.currentframe().f_back.f_lineno
    error,file,func=error_desc
    error_line='Error: '+str(error)+' File:'+file+' Function name:<< '+func+' >> On try block exception line number:'+str(line_num)
    if show_l:
        print(str(error_line))
        return str(error_line)
    return msj