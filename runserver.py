#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,socket
from project import app
from project.config import constants as CONSTANTS
import imp
import sys
sys.dont_write_bytecode = True

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 1))
if CONSTANTS.server_ip is None:
    CONSTANTS.server_ip = s.getsockname()[0]

if __name__ == '__main__':
    imp.reload(CONSTANTS)
    port = int(os.environ.get("PORT", CONSTANTS.server_port))
    app.run(CONSTANTS.server_ip, port=port)
