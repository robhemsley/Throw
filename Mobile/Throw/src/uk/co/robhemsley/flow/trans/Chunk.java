package uk.co.robhemsley.flow.trans;

import java.io.IOException;

import org.codehaus.jackson.JsonGenerationException;
import org.codehaus.jackson.annotate.JsonIgnore;
import org.codehaus.jackson.annotate.JsonProperty;
import org.codehaus.jackson.map.JsonMappingException;
import org.codehaus.jackson.map.ObjectMapper;

public class Chunk {
	private int 		chunk_id;
	private String 		file_id;
	private String 		data;
	
	public Chunk(int chunk_id, String file_id, String data){
		this.chunk_id = chunk_id;
		this.file_id = file_id;
		this.data = data;
	}
	
	@JsonProperty("chunk_id")
	public int getChunkID() {
		return chunk_id;
	}

	public void setChunkID(int chunk_id) {
		this.chunk_id = chunk_id;
	}
	
	@JsonProperty("file_id")
	public String getFileID() {
		return file_id;
	}

	public void setFileID(String file_id) {
		this.file_id = file_id;
	}
	
	@JsonProperty("data")
	public String getData() {
		return data;
	}

	public void setData(String data) {
		this.data = data;
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