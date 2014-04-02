'''
Created on Jan 24, 2013

@author: rob
'''

import os.path, time, StringIO

SERVER_IP = "10.189.112.21:8080"

class Client:
    """
    Doc String
    """
    client_id = ""
    location = (0,0)
    _files = {}
    _connect_time = 0
    _marker = None
    
    def __init__(self, client_id, location = None):
        """
        
        """
        _files = {}
        _marker = None
        self.client_id = client_id
        if location == None:
            self.location = (-200, -200)
        else:
            self.location = location
        self._connect_time = time.time()
        
    def add_file(self, file_obj):
        """
        DocString
        """        
        self._files[file_obj.file_id] = file_obj
        
    def get_marker(self):
        """
        
        //WARNING - This uses basic 10 digit numbers for matching and so can easily be scraped and hacked
        change to UUID or something similar
        """
        print "WHAT"
        return "http://%s/qr/http://%s/download/%s"% (SERVER_IP, SERVER_IP, self.client_id)
                    
    def get_details(self):
        return {"client_id": self.client_id, "files": "", "marker": self.get_marker(), "connect_time": self._connect_time}
            
    def cleanUp(self):
        for file_obj in self._files.itervalues():
            print file_obj.file_ref
            if os.path.exists(file_obj.file_ref):
                os.remove(file_obj.file_ref)
        self._files = {}

                        
    def __del__(self):
        for file_obj in self._files.itervalues():
            if os.path.exists(file_obj.file_ref):
                os.remove(file_obj.file_ref)
        self._files = {}
