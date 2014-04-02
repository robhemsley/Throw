
import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.iostream
import tornado.httpclient
import urllib2
import socket
from tornado.options import define, options
import json, copy, time, hashlib, os.path, uuid, random, base64, StringIO, pyqrcode, zipfile
from subprocess import call

from tornado.options import define, options

from Client import Client
from Msg import Msg
from Msg import MsgCon
from File import File
from File import Chunk


TMP_FILE_DIR = "tmpfile/"

global _clients
_clients = {}
_clientsIds = {}
_clientsWebIds = {}

def clean_msg(msg):
    """
    Something Here
    """
    msg = str(msg).strip()
    jsonMsg = {}
    try:
        jsonMsg = json.loads(msg)
    except ValueError:
        pass
    
    return jsonMsg


    
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/socket", ThrowSocketHandler),
            (r"/download/(.*?)", DownloadHandler),
            (r"/qr/(.*?)", QRHandler),
        ]
        
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            autoescape=None,
            xheaders=True,
            debug=True,
            cookie_secret="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo="
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    
    def get_current_user(self):
        return self.get_secure_cookie("email")

class MainHandler(BaseHandler):
    def get(self):
        self.render("throw.html")
        
class QRHandler(BaseHandler):
    
    def get(self, data):
        print data
        output = StringIO.StringIO()
        image = pyqrcode.MakeQRImage(data)
        image.save(output, format="PNG")
        contents = output.getvalue()
        
        self.set_header("Content-Type", "image/png")
        self.write(contents)

        self.finish()

class DownloadHandler(BaseHandler):
    
    def get(self, id_filename):
        if "-" in id_filename:
            try:
                split = id_filename.split("-")
                filename = _clients[split[0]]._client._files[split[1].split("_")[0]].filename
                out =  _clients[split[0]]._client._files[split[1].split("_")[0]].flattern_chunks()
                    
                self.set_header("Content-Type", "application/octet-stream")
                self.set_header("Content-Disposition", "attachment; filename=\"%s\""% (filename)) 
                self.write(base64.b64decode(out[out.index("base64,")+7:]))
            except:
                pass
        else:
            if id_filename in _clients:
                file_like_object = StringIO.StringIO()
                zipfile_out = zipfile.ZipFile(file_like_object, mode='w')
                
                for file in _clients[id_filename]._client._files.itervalues():
                    filename = file.filename
                    file.inflate()
                    
                    out =  file.flattern_chunks()
                    print out
                    zipfile_out.writestr(filename, base64.b64decode(out[out.index("base64,")+7:]));
                
                zipfile_out.close()
                self.set_header("Content-Type", "application/octet-stream")
                self.set_header("Content-Disposition", "attachment; filename=\"%s\""% ("Throw.zip")) 
                
                self.write(file_like_object.getvalue())
        
        self.finish()

def process(conn, msg):
    print msg
    msg_obj = Msg(msg)
    #print msg_obj
        
    if msg_obj.get_type() == MsgCon.TYPE_FILE_INFO:
        body = tornado.escape.json_decode(msg_obj.get_body())
        print body
        conn._tmp_files[body["file_id"]] = File(body["filename"], body["file_id"], body["file_chunk_count"])
        #print "File Info: ID-%s Name-%s Length-%d"% (body["file_id"], body["filename"], body["file_chunk_count"])
        tmp_msg = Msg(None, "0000000000")        
        tmp_msg.set_value("msg_id", msg_obj.get_msg_id())
        tmp_msg.set_type(MsgCon.TYPE_ACK)
        tmp_msg.set_body({"status": 200})
        conn.write_message(str(tmp_msg))
        
    elif msg_obj.get_type() == MsgCon.TYPE_FILE_PUSH:
        body = tornado.escape.json_decode(msg_obj.get_body())
        print "PUSH"
        
        for file_obj in conn._client._files.itervalues():
            if file_obj.file_id not in _clients[body["client_id"]]._downloaded:
                tmp_msg = Msg(None, "0000000000")
                tmp_msg.set_type(MsgCon.TYPE_FILE_INFO)
                tmp_msg.set_body(file_obj.get_dict())
                _clients[body["client_id"]].write_message(str(tmp_msg))
                     
                     
                print file_obj.file_id
                print file_obj.file_ref
                file_obj.inflate()
                   
                for chunk in file_obj._chunks.itervalues():
                    tmp_msg1 = Msg(None, "0000000000")
                    tmp_msg1.set_type(MsgCon.TYPE_FILE_CHUNK)
    
                    print chunk.file_id
                    print chunk.chunk_id
                    tmp_msg1.set_body(chunk.__dict__)
                    _clients[body["client_id"]].write_message(str(tmp_msg1))
                    
                _clients[body["client_id"]]._downloaded.append(file_obj.file_id);
                print "DONE"
            
            print conn._client._files

        
    elif msg_obj.get_type() == MsgCon.TYPE_FILE_REQUEST:
        body = tornado.escape.json_decode(msg_obj.get_body())
        
        print _clients[body["client_id"]]._client._files

        for file_obj in _clients[body["client_id"]]._client._files.itervalues():
            if file_obj.file_id not in conn._downloaded:

                tmp_msg = Msg(None, "0000000000")
                tmp_msg.set_type(MsgCon.TYPE_FILE_INFO)
                tmp_msg.set_body(file_obj.get_dict())
                conn.write_message(str(tmp_msg))
                     
                     
                print file_obj.file_id
                print file_obj.file_ref
                file_obj.inflate()
                   
                for chunk in file_obj._chunks.itervalues():
                    tmp_msg1 = Msg(None, "0000000000")
                    tmp_msg1.set_type(MsgCon.TYPE_FILE_CHUNK)
    
                    print chunk.file_id
                    print chunk.chunk_id
                    tmp_msg1.set_body(chunk.__dict__)
                    conn.write_message(str(tmp_msg1))
                    
                conn._downloaded.append(file_obj.file_id);
                print "DONE"
            
            print conn._client._files
                
        
    elif msg_obj.get_type() == MsgCon.TYPE_FILE_CHUNK:
        body = tornado.escape.json_decode(msg_obj.get_body())
        # body
        tmp_file = conn._tmp_files[body["file_id"]]
        tmp_file.add_chunk(Chunk(body))
        
        tmp_msg = Msg(None, "0000000000")
        tmp_msg.set_value("msg_id", msg_obj.get_msg_id())
        tmp_msg.set_type(MsgCon.TYPE_ACK)
        tmp_msg.set_body({"status": 200})
        conn.write_message(str(tmp_msg))

        #print "File Chunk: ID-%s Chunk-%d"% (body["file_id"], body["chunk_id"])
        
        if tmp_file.check_chunks() == 0:
            print "File Received: ID-%s"% (body["file_id"])
            if tmp_file.validate():
                print "File Validated: ID-%s"% (body["file_id"])
                tmp_file.deflate(TMP_FILE_DIR)
                
                conn._client.add_file(tmp_file)
                conn._tmp_files[body["file_id"]] = None
                del conn._tmp_files[body["file_id"]]
                
                tmp_msg = Msg(None, "0000000000")
                tmp_msg.set_value("msg_id", msg_obj.get_msg_id())
                tmp_msg.set_type(MsgCon.TYPE_ACK)
                tmp_msg.set_body({"status": 200})
                conn.write_message(str(tmp_msg))
                
                
                
                
                
                
                
                
                
            else:
                print "FILE WENT WRONG" 
        
    """
    print msg
    if msg == "stop":
        f = open("tmpfile/test.jpg", 'w')
        f.write(base64.b64decode(conn._fileData["test"]))
        f.close()
        conn._fileData["test"] = ""
        del conn._fileData["test"]
        print "Written"
        print conn._fileData
    elif msg == "open":
        #call(["open", "test.jpg"])
        print "OPEN CALLED"
        print conn._fileData

        #_tmpTest[len(_tmpTest)-1].write_message("http://127.0.0.1:8080/download/test.jpg")
        #conn.write_message("http://10.3.2.13:8080/Download/test.jpg");
    elif msg == "start":
        conn._fileData["test"] = ""
        print "Start"
    else:
        if "test" not in conn._fileData:
            conn._fileData["test"] = ""
            print "CLEAN"
        conn._fileData["test"] += msg  """

class ThrowSocketHandler(tornado.websocket.WebSocketHandler):
    _client = None
    _tmp_files = {}
    _downloaded = []

    def allow_draft76(self):
        return True

    def open(self):
        self._client = ""
        self._tmp_files = {}
        self._downloaded = []
        global _clients

        while True:
            print _clients
            tmp_id = str(random.randint(0,999999)).zfill(10)
            print tmp_id
            if id not in _clients: 
                self._client = Client(tmp_id)
                _clients[tmp_id] = self
                break
        
        print _clients
        
        self._client._files = {}
        tmp_msg = Msg(None, self._client.client_id)
        tmp_msg.set_type(MsgCon.TYPE_CONN_DETAILS)
        tmp_msg.set_body(self._client.get_details())
        self.write_message(str(tmp_msg))
                
    def on_close(self): 
        id = self._client.client_id
        self._client.cleanUp()
        self._client = None
        del self._client
        _clients[id] = None
        del _clients[id] 

    def on_message(self, message):
        parsed = tornado.escape.json_decode(message)
        process(self, parsed)
        

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = Application()
    app.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
    