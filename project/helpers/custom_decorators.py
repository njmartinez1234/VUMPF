# -*- coding: utf-8 -*-
from functools import wraps
from flask import request
from flask import session
from flask import jsonify
from flask import redirect
import datetime
from project.helpers import tools

from project.config import constants as CONSTANTS
import imp

def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kws):
            imp.reload(CONSTANTS)
            if not session.keys():
                return jsonify({'success':False,'msg':'You are not allowed to perform this operation.','code':'4545'})
            elif 'Token' not in request.headers:
                return jsonify({'success':False,'msg':'Invalid header parameters.'})                
            elif request.headers['Token'] not in session['data_sesion']['token']:
                return jsonify({'success':False,'msg':'Invalid token.'})
            else:                
                session_time = datetime.datetime.now() - session['data_sesion']['datetime']                
                if session_time.seconds > CONSTANTS.session_time:
                    tools.clearSession()
                    return jsonify({"success": False,"msj":'Session has expired.' ,'code':'4546' })
                else:
                  data = session['data_sesion']
                  data['datetime'] = datetime.datetime.now()
                  session['data_sesion'] = data      
                  return f(*args, **kws)
                  
    return decorated_function

def runing_threads(f):
    @wraps(f)
    def threads_fn(*args, **kws):
        import threading
        threads=[]
        main_thread = threading.main_thread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            else:
                if 'hread' in t.getName():
                    pass
                else:
                    threads.append(t.getName())
        if len(threads)>0:
            return jsonify({'success':False,'msg':'There are jobs runing, must wait for it to finish..','data':threads})
        else:
            return f(*args, **kws)
    return threads_fn