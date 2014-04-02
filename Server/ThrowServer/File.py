'''
Created on Jan 24, 2013

@author: rob
'''

import os.path, time, base64, uuid, json


class File:
    """
    Doc String
    """
    _chunks = {}
    path = None
    filename = None
    file_id = None
    file_chunk_count = None
    type_header = None
    
    file_ref = ""

    def __init__(self, filename, file_id= None, chunk_count=None, path = None):
        """
        
        """
        self.file_ref = ""
        self._chunks = {}
        self.file_id = file_id
        self.filename = filename
        self.file_chunk_count = chunk_count
        if path != None:
            path = os.path.abspath(path)
            self.path = path
            self.filename = os.path.basename(path) 
        
    def add_chunk(self, chunk):
        self._chunks[chunk.chunk_id] = chunk
        
    def flattern_chunks(self):
        output = ""
        for chunk_id in range(len(self._chunks)):
            output += self._chunks[chunk_id].data
            
        return output
    
    def check_chunks(self):
        return self.file_chunk_count - len(self._chunks)
    
    def validate(self):
        chunk_count = self.file_chunk_count
        file_id = self.file_id
        
        if len(self._chunks) != chunk_count:
            return False
            
        for i in range(len(self._chunks)):
            if i not in self._chunks:
                return False
            
            if self._chunks[i].file_id != file_id:
                return False
            
        return True
    
    def save(self, filename):
        self.validate()
        f = open(filename, "w")
        chunks = self.flattern_chunks()
        if chunks.find("base64,") > 0:
            self.type_header = chunks[:chunks.index("base64,")+7]
            f.write(base64.b64decode(chunks[chunks.index("base64,")+7:]))
        else:
            f.write(base64.b64decode(chunks))
        f.close()
        
    def deflate(self, tmpdir):
        #Why didn't you just pickle the god dam thing.... - As you can't see the img
        while True:
            tmp = os.path.abspath(tmpdir+str(uuid.uuid4())+"-"+self.filename)
            if not os.path.exists(tmp):
                self.save(tmp)
                self._chunks = {}
                break
            
        self.file_ref = tmp
        
    def inflate(self):
        if os.path.exists(self.file_ref):
            f = open(self.file_ref)
            tmp = ""
            tmp += f.read()
            f.close()
            #if self.type_header == None:
            #    out = "data:image/jpg;base64," 
            #else:
            out = self.type_header
            out += base64.b64encode(tmp)
            
            split = self.split_len(out, 100000)
            for i in range(len(split)):
                self.add_chunk(Chunk({"file_id": self.file_id, "chunk_id": i, "data": split[i]}))
        else:
            print "THE FILE DOES NOT EXist"
            print self.file_ref
                    
    def split_len(self, seq, length):
        return [seq[i:i+length] for i in range(0, len(seq), length)]
    
        
    def get_dict(self):
        return {"filename": self.filename, "file_id": self.file_id,"file_chunk_count": self.file_chunk_count}
        
    def __str__(self):
        return str(self.get_dict())
    
    def __repr__(self):
        return self.__str__()
        
        
class Chunk:
    """
    """
    chunk_id = None
    file_id = None
    data = None
    
    def __init__(self, chunk_msg):
        self.chunk_id = chunk_msg["chunk_id"]
        self.file_id = chunk_msg["file_id"]
        self.data = chunk_msg["data"] 
        
    
    
    