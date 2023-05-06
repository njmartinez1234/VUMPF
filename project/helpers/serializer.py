import decimal, datetime
from project import app
import json
from collections import OrderedDict
import pymongo
from bson import ObjectId
def proxytodict(resultProxy,order):
    app.config['JSON_SORT_KEYS'] = order
    if type(resultProxy)==dict:
        return resultProxy
    #Handle mongo results
    elif type(resultProxy)==pymongo.cursor.Cursor:
        dataArray={}
        count=0
        for i in resultProxy:
            documents=list(i.items())
            for k,v in documents:
                if isinstance(v, ObjectId):
                    i[k]=str(v)
            dataArray.update({count : dict(i.items())})
            count=count+1
        return dataArray
    return [OrderedDict(zip(x.keys(),list(map(lambda val: val.isoformat() if isinstance(val, datetime.date) else (float(val) if isinstance(val, decimal.Decimal) else (bytes(val) if isinstance(val, (bytes, bytearray,memoryview)) else val)), x)))) for x in resultProxy]
