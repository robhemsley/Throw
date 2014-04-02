package uk.co.robhemsley.flow.trans;

import java.io.ByteArrayOutputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.util.Arrays;
import java.util.Random;


import org.json.JSONException;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;


import de.tavendo.autobahn.WebSocketConnection;
import de.tavendo.autobahn.WebSocketException;
import de.tavendo.autobahn.WebSocketHandler;

import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.ListActivity;
import android.content.ContentResolver;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Base64;
import android.util.Log;
import android.view.Menu;
import android.view.View;
import android.webkit.MimeTypeMap;
import android.widget.Button;
import android.widget.ImageView;

public class MainActivity extends Activity {
	private final WebSocketConnection mConnection = new WebSocketConnection();
	private final String wsuri = "ws://108.59.3.115:19708/socket";
	private Activity mActivity;

	String[] data1;
	String filename;
	String client_id;
	String qr_url;

	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);
		mActivity = this;
		
		setup();
		
		Intent intent = getIntent();
	    Bundle extras = intent.getExtras();
	    String action = intent.getAction();
	    
	    if (Intent.ACTION_SEND.equals(action)){
	    	if (extras.containsKey(Intent.EXTRA_STREAM)){
                Uri uri = (Uri) extras.getParcelable(Intent.EXTRA_STREAM);

                ContentResolver cr = getContentResolver();
                
				try {
					InputStream is = cr.openInputStream(uri);

					byte[] data = readBytes(is);
		            
		            String base64 = "data:"+getMimeType(uri.toString())+";base64,";
		            base64 += Base64.encodeToString(data, Base64.DEFAULT);
		            
		            data1 = splitBuffer(base64, 100000);
		            filename = uri.toString();
		    		
		    		IntentIntegrator integrator = new IntentIntegrator(this);
		    		integrator.initiateScan();
		    		
				} catch (FileNotFoundException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
	        }else if (extras.containsKey(Intent.EXTRA_TEXT)){
	        	return;
	        }
	    }
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		return true;
	}
	
	
	public void onActivityResult(int requestCode, int resultCode, Intent intent) {
		IntentResult scanResult = IntentIntegrator.parseActivityResult(requestCode, resultCode, intent);
		if (scanResult != null) {	
			send(filename.substring(filename.lastIndexOf('/')+1), data1);
			pushFile(scanResult.getContents());
		}
	}
	
	public static String getMimeType(String url){
	    String type = null;
	    String extension = MimeTypeMap.getFileExtensionFromUrl(url);
	    if (extension != null) {
	        MimeTypeMap mime = MimeTypeMap.getSingleton();
	        type = mime.getMimeTypeFromExtension(extension);
	    }
	    return type;
	}
	
	private void send(final String filename_in, final String[] base64) {
		Random randomGenerator = new Random();
		Integer tmp = new Integer(randomGenerator.nextInt(9999999));
 	
	   File test = new File(filename_in, tmp.toString(), base64.length);
	   for (int i = 0; i < base64.length; i++){
		   test.addChunk(new Chunk(i, test.getFileId(), base64[i]));
	   }
	   
	   Msg msg = new Msg(this.client_id);
	   msg.setBody(test.getAsJSON());
	   msg.setType(Msg.TYPE_FILE_INFO);
	   
	   mConnection.sendTextMessage(msg.getAsJSON());
	  
	   for (int i = 0; i < test.getChunks().size(); i++){
		   Msg msg1 = new Msg(this.client_id);
		   msg1.setBody(test.getChunk(i).getAsJSON());
		   msg1.setType(Msg.TYPE_FILE_CHUNK);
		   
		   mConnection.sendTextMessage(msg1.getAsJSON());
	   }
	}
	
	public void pushFile(final String scanResult){
		String client_id = scanResult.substring(scanResult.lastIndexOf("/")+1);
		Msg msg2 = new Msg(this.client_id);
		msg2.setBody("{\"client_id\": \""+client_id+"\"}");
		msg2.setType(Msg.TYPE_FILE_PUSH);
		mConnection.sendTextMessage(msg2.getAsJSON());
	   
		Intent intent = new Intent(Intent.ACTION_MAIN);
		intent.addCategory(Intent.CATEGORY_HOME);
		intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
		startActivity(intent);
		finish();
	}

	private void setup() {
		try {
			mConnection.connect(wsuri, new WebSocketHandler() {
	        	 
				@Override
				public void onOpen() {	
					  
				}

	            @Override
	            public void onTextMessage(String payload) {
	               process(payload);
	            }

	            @Override
	            public void onClose(int code, String reason) {
	
	            }
	            
	         });
		} catch (WebSocketException e) {
			Log.d("Error", e.toString());
	    }
	}
	
	public void process(String msg){
		JSONParser parser = new JSONParser();
		
		try {
			Object obj = parser.parse(msg);
			JSONObject msg_obj = (JSONObject) obj;
			long type = (Long) msg_obj.get("type");
			
			if(type == 3){
				this.client_id = (String) msg_obj.get("msg_id");
				JSONObject body = (JSONObject) msg_obj.get("body");
				this.qr_url = (String) body.get("marker");
				new DownloadImageTask((ImageView) findViewById(R.id.qr_img_view)).execute(this.qr_url);
			}
			
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}
	   
	   
	@SuppressLint("NewApi")
	public static byte[][] divideArray(byte[] source, int chunksize) {
		byte[][] ret = new byte[(int)Math.ceil(source.length / (double)chunksize)][chunksize];

	    int start = 0;

	    for(int i = 0; i < ret.length; i++) {
	    	ret[i] = Arrays.copyOfRange(source,start, start + chunksize);
	        start += chunksize ;
	    }

	    return ret;
	}

	public byte[] readBytes(InputStream inputStream) throws IOException {
		// this dynamically extends to take the bytes you read
		ByteArrayOutputStream byteBuffer = new ByteArrayOutputStream();

		// this is storage overwritten on each iteration with bytes
		int bufferSize = 1024;
		byte[] buffer = new byte[bufferSize];

		// we need to know how may bytes were read to write them to the byteBuffer
		int len = 0;
		while ((len = inputStream.read(buffer)) != -1) {
			byteBuffer.write(buffer, 0, len);
		}

		// and then we can return your byte array.
		return byteBuffer.toByteArray();
	}
	
	public String[] splitBuffer(String input, int maxLength){
	    int elements = (input.length() + maxLength - 1) / maxLength;
	    String[] ret = new String[elements];
	    for (int i = 0; i < elements; i++)
	    {
	        int start = i * maxLength;
	        ret[i] = input.substring(start, Math.min(input.length(),
	                                                 start + maxLength));
	    }
	    return ret;
	}
	
	private class DownloadImageTask extends AsyncTask<String, Void, Bitmap> {
		  ImageView bmImage;

		  public DownloadImageTask(ImageView bmImage) {
		      this.bmImage = bmImage;
		  }

		  protected Bitmap doInBackground(String... urls) {
		      String urldisplay = urls[0];
		      Bitmap mIcon11 = null;
		      try {
		        InputStream in = new java.net.URL(urldisplay).openStream();
		        mIcon11 = BitmapFactory.decodeStream(in);
		      } catch (Exception e) {
		          Log.e("Error", e.getMessage());
		          e.printStackTrace();
		      }
		      return mIcon11;
		  }

		  protected void onPostExecute(Bitmap result) {
		      bmImage.setImageBitmap(result);
		  }
		}
}
