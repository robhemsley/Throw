function ThrowCore(serverURL){
	
	if (serverURL == undefined){
		this.serverURL = document.domain+"/socket";
	}else{
		this.serverURL = serverURL+"/socket";
	}
					
	this.ws = undefined;
	this.handlers = {};
	this.callback = {};
	
	this.TYPE_SYSTEM = 0;
    this.TYPE_DATA = 1;
    this.TYPE_DEBUG = 2;
    this.TYPE_CONN_DETAILS = 3;
    this.TYPE_FILE_INFO = 4;
    this.TYPE_FILE_CHUNK = 5;
    this.TYPE_ACK = 6;
    this.TYPE_FILE_REQUEST = 7;
    
    this.client = undefined
	
	var throwcore = this;

	var createWs = function(url){
		websocket = 'ws://'+url;
	  
		if (window.WebSocket) {
			ws = new WebSocket(websocket);
		}else if (window.MozWebSocket) {
			ws = MozWebSocket(websocket);
		}else {
			alert('WebSocket Not Supported');
		}
		
		return ws;
	}
	
	var checkConnState = function(){
		if (this.ws == undefined || this.ws.readyState > 1){
			connect();
		}
	}
	
	this.status = function(){
		if (this.ws == undefined || this.ws.readyState > 1){
			return 0;
		}else{
			return 1;
		}
	}

	this.connect = function(callback){
		this.ws = createWs(this.serverURL);
		this.ws.onmessage = this.onmessage;
		this.ws.onopen = this.onopen;
		this.ws.onclose = this.onclose;
		callback();
	}
	
	this.disconnect = function(){
		this.ws.close(1000, "Client Disconnect");
	}
	
	this.sendThrowMsg = function (type, body, callback){
		msg = new Msg(undefined, this.client["client_id"]);
		
		msg.set_type(type);
		msg.set_body(body);
		
		if (callback != undefined){
			this.callback[msg.get_msg_id()] = callback;
		}
		console.log(msg);
		
		this.ws.send(msg.to_string());
		if ("onsend" in this.handlers){
			this.handlers["onsend"]["function"](msg.to_string());
		}
	}
	
	this.getClientFiles = function (client_id){
		this.sendThrowMsg(this.TYPE_FILE_REQUEST, JSON.stringify({"client_id": client_id}));
	}
	
	this.sendFile = function(fileObj){
		fr = new FileReader();
				
		var name = fileObj.name;
		/*if (fileObj.type.indexOf("image") !== -1){
			console.log("IMAGE");
			var image = new Image();
        	image.onload = function() {
            	alert('Width:'+this.width +' Height:'+ this.height+' '+ Math.round(chosen.size/1024)+'KB');
        	};
        	image.src = url.createObjectURL(chosen);    
		}*/
        fr.onloadend = function(evt){
        	console.log(evt);
        	console.log("sdaa");
			throwcore.sendUriFile(evt.target.result, name);
        };
        fr.readAsDataURL(fileObj);
	}
	
	this.sendUriFile = function(uriData, filename){	
		tmp = new ThrowFile(filename, uriData);
				
		out = {"filename": tmp.filename, "file_id": tmp.file_id, "file_chunk_count": tmp.chunks.length}
		this.sendThrowMsg(this.TYPE_FILE_INFO, JSON.stringify(out));
		
		if(this.handlers.hasOwnProperty('uploadstart')){
			this.handlers["uploadstart"]["function"](out);
		}
		
		steps = 100/tmp.chunks.length;
		start = 0;
		
		for (i=0;i<tmp.chunks.length; i++){
			start += steps;
			
			
			this.sendThrowMsg(this.TYPE_FILE_CHUNK, JSON.stringify(tmp.chunks[i]), (function(tmp, i){
				return function(){
					console.log("RESPONSE");
					console.log(tmp.chunks[i]);
					
					if(throwcore.handlers.hasOwnProperty('uploadprogress')){
						throwcore.handlers["uploadprogress"]["function"](tmp, tmp.chunks[i], i, tmp.chunks.length, tmp.getTimeEst(i));
					}
				}
			}(tmp, i)));

			

		}
		console.log("SENT");
		
		if(this.handlers.hasOwnProperty('uploadfinish')){
			this.handlers["uploadfinish"]["function"](tmp);
		}
	}
	
	
	this.processMsg = function(msg){
		if (this.client == undefined){
			msgObj = new Msg(msg, undefined);
		}else{
			msgObj = new Msg(msg);
		}
		
		if (msgObj.get_msg_id() in this.callback){
			this.callback[msgObj.get_msg_id()](msgObj);
			delete this.callback[msgObj.get_msg_id()];
		}
		if (msgObj.get_type() == this.TYPE_CONN_DETAILS){
			this.client = msgObj.get_body();
			console.log(this.client);
			
		}else{
			if(msgObj.get_type() == this.TYPE_FILE_INFO){
				console.log("INFO");
				tmp = msgObj.get_body();		
								
				tmp_file = new ThrowFile(tmp.filename, undefined, tmp.file_id, tmp.file_chunk_count)
				
				if (this.client.files == ""){
					this.client.files = {};				
				}
				this.client.files[tmp_file.file_id] = tmp_file
				
				if(this.handlers.hasOwnProperty('downloadstart')){
					this.handlers["downloadstart"]["function"](tmp_file);
				}
					
			}else{
				if(msgObj.get_type() == this.TYPE_FILE_CHUNK){
					console.log("CHUNK");
					
					tmp = msgObj.get_body();	
					tmp_chunk = new Chunk(tmp.chunk_id, tmp.file_id, tmp.data);	
					console.log(tmp_chunk);
					
					file = this.client.files[tmp.file_id];
					
					file.addChunk(tmp.data);
					
					if(this.handlers.hasOwnProperty('downloadprogress')){
						this.handlers["downloadprogress"]["function"](file, tmp.chunk_id, file.file_chunk_count, file.getTimeEst(tmp.chunk_id));
					}	
					
					if (file.check_chunks() == 0){
					
						if(this.handlers.hasOwnProperty('downloadfinish')){
							this.handlers["downloadfinish"]["function"](file);
						}
							
						console.log("File Received");
						console.log(file.get_base64()); 
					}
				}
			}
		}
		




		if (msgObj.get_type() in this.callback){
			this.callback[msgObj.get_type()](msgObj);
			delete this.callback[msgObj.get_type()];
		}			          	          		
	}
	
	this.addEventListener = function(type, callback) {
		this.callback[type] = callback;
	};

	this.onmessage = function (evt) {
		throwcore.processMsg(evt.data);
		if ("onmessage" in throwcore.handlers){
			throwcore.handlers["onmessage"]["function"](evt);
		}
	};
	  
	this.onopen = function() {
		if ("onopen" in throwcore.handlers){
			throwcore.handlers["onopen"]["function"]();
		}
	};
  
	this.onclose = function(evt) {
		if ("onclose" in throwcore.handlers){
			throwcore.handlers["onclose"]["function"]();
		}
	};
	
	this.addHandler = function(name, func, strCast){
		if (strCast == undefined){
			strCast = false;
		}
		this.handlers[name] = {"function": func, "strCast": strCast};
	}
}     


function Chunk(chunk_id, file_id, data){
	this.chunk_id = chunk_id
	this.file_id = file_id;
	this.data = data;
}

function ThrowFile(filename, uriData, file_id, file_chunk_count){	
	this.filename = filename;
	this.file_id = file_id;
	this.chunks = [];
	this.file_chunk_count = file_chunk_count;
	this.time = Math.round(new Date().getTime());
		
	this.addChunk = function(chunkData){
		this.chunks.push(new Chunk(this.chunks.length, this.file_id, chunkData));
	};
	
	this.check_chunks = function(){
		return this.file_chunk_count - this.chunks.length
	}
	
	this.getTimeEst = function(count){
		nowTime = Math.round(new Date().getTime())
		timeSoFar = (nowTime - this.time);
		timePerChunk = parseFloat(parseFloat(timeSoFar)/parseFloat(count));
		
		return Math.round((timePerChunk*(this.file_chunk_count-count))/1000);
	}
	
	this.get_base64 = function(){
		out = ""
		for (i=0; i < this.chunks.length; i++){
			console.log(this.chunks[i]);
			out += this.chunks[i].data;
		}
		return out;
	}
	
	if (this.file_id == undefined){
		this.file_id = String(Math.floor(Math.random()*999999));
	}
	
	//Max File Size = 1000
	if (uriData != undefined){
		splitUri = uriData.match(/.{1,100000}/g);
		for (i =0; i < splitUri.length; i ++){
			this.addChunk(splitUri[i]);
		}
		this.file_chunk_count = this.chunks.length;
	}
}

function Msg(msg, usr_id) {
	this.data = {};
	
	if (usr_id == undefined){
		usr_id = "";
	}
	
	if (msg == undefined){	
		this.data = {"type": "", "body": "", "timestamp": "", "msg_id": String(usr_id)+String(Math.floor(Math.random()*999999))};
	}else{
		jsonMsg = {};
		try{
			jsonMsg = JSON.parse(msg);
		}catch(err){}
		
		this.data = jsonMsg;
	}
	
	if (usr_id == undefined){
		if (msg != undefined){	
			usr_id = this.data["msg_id"].split("-")[0]
			this.data["msg_id"] = String(usr_id)+String(Math.floor(Math.random()*999999));
		}
	}
	
	this.get_value = function(key){
		if (key in this.data){
			return this.data[key];
		}else{
			return undefined;
		}
	};
	
	this.set_value = function(key, value){
		this.data[key] = value;
	};	
	
	this.get_type = function(){
		return this.get_value("type")
	};
	
	this.get_body = function(){
		return this.get_value("body")
	};
	
	this.get_timestamp = function(){
		return this.get_value("timestamp")
	};	
	
	this.get_msg_id = function(){
		return this.get_value("msg_id")
	};	

	this.set_type = function(val){
		this.set_value("type", val);
	};
	
	this.set_body = function(val){
		this.set_value("body", val);
	};			
	
	this.set_timestamp = function(val){
		this.set_value("timestamp", val);
	};
	
	this.set_msg_id = function(val){
		return this.set_value("msg_id", val)
	};	

	this.to_string = function () {
		this.set_timestamp(Math.round(new Date().getTime()/1000.0))
		return JSON.stringify(this.data)
	};
}