'''
Created on Jan 24, 2013

@author: rob
'''
import time, json, random

class MsgCon:
    """
    MsgCon - Class
        Provides constant variables for use with the message object.
    """
    TYPE_SYSTEM = 0
    TYPE_DATA = 1
    TYPE_DEBUG = 2
    TYPE_CONN_DETAILS = 3
    TYPE_FILE_INFO = 4;
    TYPE_FILE_CHUNK = 5;
    TYPE_ACK = 6;
    TYPE_FILE_REQUEST = 7;
    TYPE_FILE_PUSH = 8;


class Msg:
    _data = None
    
    def __init__(self, data = None, usr_id = None):
        if usr_id == None:
            if data != None:
                usr_id = data["msg_id"].split("-")[0]
            
        if data == None:
            self._data = {"type": "", "body": "", "timestamp": "", "msg_id": "%s-%d"%(usr_id, random.randint(0,999999))}
        else:
            self._data = data
    
    def get_value(self, key):
        if key in self._data:
            return self._data[key]
        else:
            return None
    
    def set_value(self, key, value):
        self._data[key] = value
        
    def set_type(self, value):
        self.set_value("type", value)
        
    def get_type(self):
        return self.get_value("type")
        
    def set_body(self, value):
        self.set_value("body", value)
        
    def get_body(self):
        return self.get_value("body")

    def set_msg_id(self, value):
        self.set_value("msg_id", value)
        
    def get_msg_id(self):
        return self.get_value("msg_id")
        
    def set_timestamp(self, value):
        self.set_value("timestamp", value)
        
    def get_timestamp(self):
        return self.get_value("timestamp")
    
    def __str__(self):
        self.set_value("timestamp" ,str(time.time()))
        return str(json.dumps(self._data))
    
    def __repr__(self):
        return self.__str__()