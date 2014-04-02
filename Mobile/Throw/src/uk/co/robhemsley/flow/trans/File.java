package uk.co.robhemsley.flow.trans;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import org.codehaus.jackson.JsonGenerationException;
import org.codehaus.jackson.annotate.JsonIgnore;
import org.codehaus.jackson.annotate.JsonProperty;
import org.codehaus.jackson.map.JsonMappingException;
import org.codehaus.jackson.map.ObjectMapper;

public class File {
	private String filename;	
	private String file_id;
	private int file_chunk_count;
	private ArrayList<Chunk> chunks = new ArrayList<Chunk>();
	
	public File(String filename, String file_id, int file_chunk_count){
		this.setFilename(filename);
		this.setFileId(file_id);
		this.set_file_chunk_count(file_chunk_count);
	}
	
	public void addChunk(Chunk chunk){
		this.chunks.add(chunk);
	}
	
	@JsonIgnore
	public ArrayList<Chunk> getChunks(){
		return this.chunks;
	}

	public Chunk getChunk(int i){
		return this.chunks.get(i);
	}
	
	@JsonProperty("file_id")
	public String getFileId() {
		return file_id;
	}

	public void setFileId(String file_id) {
		this.file_id = file_id;
	}

	@JsonProperty("filename")
	public String getFilename() {
		return filename;
	}

	public void setFilename(String filename) {
		this.filename = filename;
	}

	@JsonProperty("file_chunk_count")
	public int get_file_chunk_count() {
		return file_chunk_count;
	}

	public void set_file_chunk_count(int file_chunk_count) {
		this.file_chunk_count = file_chunk_count;
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
