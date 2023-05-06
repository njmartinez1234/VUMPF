# -*- coding: utf-8 -*-
# __version__ = '0.1'
from flask import Flask
import os
import importlib
import sys
from pathlib import Path

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'random'
app.config['DISPLAY_ERRORS']=True
app.config['SERVER_PATH'] = Path(__file__).parents[0]
app.debug = True
  
for f in os.listdir(os.path.join(str(app.config['SERVER_PATH']),'controllers')):
    if f !='__init__.py':
        if f.endswith('.py'):
            try:
                module = importlib.import_module(os.path.basename(os.path.dirname(__file__))+'.controllers.'+os.path.splitext(f)[0], package=os.path.splitext(f)[0])
            except Exception as e:
                print(f,e)
                sys.exit(0)
            else:
                 app.register_blueprint(getattr(module, os.path.splitext(f)[0]),url_prefix=os.sep+os.path.splitext(f)[0])
                 pass
