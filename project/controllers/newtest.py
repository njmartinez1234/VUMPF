# -*- coding: utf-8 -*-
from project import app
from flask import request
from flask import Blueprint
import os
from project.helpers import tools
import json

func=os.path.splitext(os.path.basename(__file__))[0]
newtest = Blueprint(func, __name__)

@newtest.route('/' , methods=['GET','POST'])
def newtest_index():
	return 'Index function'
