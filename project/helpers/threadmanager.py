# -*- coding: utf-8 -*-
import threading
import logging
import time
import queue
import os
import sys
from itertools import islice
from project.helpers import tools

currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name
currentFileName = os.path.basename(__file__)

class EncodeThread(threading.Thread):

    def __init__(self, **kwargs):
        self.my_queue = queue.Queue()
        self.kwargs=kwargs
        listx = list(self.kwargs['args'])
        listx.append(self.my_queue)
        args = tuple(listx)
        self.threads=threads=[]
        if self.kwargs['name'] is None:
            self.kwargs['name']='t_'+tools.getToken(7)
        super().__init__(target=self.kwargs['target'],args=args, name=self.kwargs['name'],
                         daemon=None)
        t=self
        self.threads.append(t)

    def pool(self):
        return (self.threads)

class StartThread():

    def __init__(self, thread_pool,max_threads=24,daemon=False):
        self.pool=thread_pool
        self.max_threads=max_threads
        self.daemon=daemon

    def run(self):
        dataArray=list()
        thread_pool=list()
        for t_arr in list(self.chunk(self.pool, self.max_threads)):
            for t in t_arr:
                thread_pool.append(t[0].getName())
                try:
                    t[0].start()
                except Exception as e:
                    data=e,currentFileName,currentFuncName()
                    msj='Unable to start threads.'
                    msj=tools.logHandler(data,msj)
                    return ({'success':False,'msj':msj})

            if not self.daemon:
                try:
                    for t in t_arr:
                        t[0].join()
                        func_value = t[0].my_queue.get()
                        if func_value:
                            dataArray.append(func_value)
                        else:
                            pass
                except Exception as e:
                    data=e,currentFileName,currentFuncName()
                    msj='There are some issues on queue.'
                    msj=tools.logHandler(data,msj)
                    return ({'success':False,'msj':msj})
        if self.daemon:
            return ({'success':True,'msg':'Task generated.','data':thread_pool})
        return dataArray

    def chunk(self,it, size):
        it = iter(it)
        return iter(lambda: tuple(islice(it, size)), ())