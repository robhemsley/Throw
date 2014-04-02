package uk.co.robhemsley.flow.trans;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

import org.codehaus.jackson.JsonGenerationException;
import org.codehaus.jackson.annotate.JsonIgnore;
import org.codehaus.jackson.annotate.JsonProperty;
import org.codehaus.jackson.map.JsonMappingException;
import org.codehaus.jackson.map.ObjectMapper;

public class Msg {
	@JsonIgnore
	public static int TYPE_SYSTEM = 0;
	@JsonIgnore
	public static int TYPE_DATA = 1;
	@JsonIgnore
	public static int TYPE_DEBUG = 2;
	@JsonIgnore
	public static int TYPE_CONN_DETAILS = 3;
	@JsonIgnore
	public static int TYPE_FILE_INFO = 4;
	@JsonIgnore
	public static int TYPE_FILE_CHUNK = 5;
	@JsonIgnore
	public static int TYPE_ACK = 6;
	@JsonIgnore
	public static int TYPE_FILE_REQUEST = 7;
	@JsonIgnore
	public static int TYPE_FILE_PUSH = 8;
	
	private int type;
	private String body;
	private long timestamp;
	private String msg_id;
	
	public Msg(String usr_id){
		this.setMsgId(usr_id);
		this.setTimestamp(System.currentTimeMillis()/1000);
		
		Random randomGenerator = new Random();
		this.setMsgId(usr_id+"-"+new Integer(randomGenerator.nextInt(9999999)).toString());
	}

	@JsonProperty("type")
	public int getType() {
		return type;
	}

	public void setType(int type) {
		this.type = type;
	}

	@JsonProperty("body")
	public String getBody() {
		return body;
	}

	public void setBody(String body) {
		this.body = body;
	}

	@JsonProperty("timestamp")
	public long getTimestamp() {
		return timestamp;
	}

	public void setTimestamp(long timestamp) {
		this.timestamp = timestamp;
	}

	@JsonProperty("msg_id")
	public String getMsgId() {
		return msg_id;
	}

	public void setMsgId(String msg_id) {
		this.msg_id = msg_id;
	}
	
	@JsonIgnore
	public String getAsJSON() {
	    ObjectMapper mapper = new ObjectMapper();
	    try {
			return mapper.writeValueAsString(this) ;
		} catch (JsonGenerationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (JsonMappingException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} 
	    return "";
	}

}
