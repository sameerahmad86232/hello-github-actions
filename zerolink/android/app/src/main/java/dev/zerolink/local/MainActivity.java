package dev.zerolink.local;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.database.Cursor;
import android.provider.OpenableColumns;
import android.graphics.Color;
import android.view.View;
import android.widget.*;
import android.os.Handler;
import android.os.Looper;
import android.os.Build;
import android.Manifest;
import android.content.pm.PackageManager;
import android.text.InputType;
import java.io.*;
import java.net.*;
import java.security.*;
import java.security.cert.X509Certificate;
import javax.net.ssl.*;
import java.util.*;
import java.util.concurrent.*;
import org.json.*;

public class MainActivity extends Activity {
 final ExecutorService worker=Executors.newSingleThreadExecutor();
 final Handler handler=new Handler(Looper.getMainLooper());
 SharedPreferences prefs; LinearLayout root,chat; ScrollView scroll; TextView status;
 EditText host,key,pin,message; String last=""; boolean active=false,busy=false;
 final ArrayList<Uri> pending=new ArrayList<>(); String pendingText=null;
 int bg=Color.rgb(15,23,32), panel=Color.rgb(30,43,56), ink=Color.rgb(232,240,247), mint=Color.rgb(120,228,181);
 int dp(float n){return (int)(n*getResources().getDisplayMetrics().density+.5f);}
 @Override public void onCreate(Bundle b){super.onCreate(b);prefs=getSharedPreferences("pair",MODE_PRIVATE);build();if(configured()&&prefs.getBoolean("auto",true))DiscoveryService.start(this);acceptIntent(getIntent());}
 @Override protected void onNewIntent(Intent i){super.onNewIntent(i);setIntent(i);acceptIntent(i);}
 @Override protected void onResume(){super.onResume();active=true;handler.removeCallbacks(tick);handler.post(tick);}
 @Override protected void onPause(){active=false;handler.removeCallbacks(tick);super.onPause();}
 @Override protected void onDestroy(){handler.removeCallbacks(tick);worker.shutdown();super.onDestroy();}
 final Runnable tick=new Runnable(){public void run(){if(active){refresh();handler.postDelayed(this,8000);}}};
 TextView text(String t,int size){TextView v=new TextView(this);v.setText(t);v.setTextSize(size);v.setTextColor(ink);return v;}
 EditText edit(String hint){EditText e=new EditText(this);e.setTextColor(ink);e.setHintTextColor(Color.rgb(155,176,190));e.setHint(hint);e.setSingleLine(true);e.setPadding(dp(12),dp(10),dp(12),dp(10));e.setBackgroundColor(panel);return e;}
 Button button(String label){Button b=new Button(this);b.setText(label);b.setAllCaps(false);b.setTextColor(Color.rgb(10,33,28));b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(mint));return b;}
 void add(LinearLayout l,View v){LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.bottomMargin=dp(8);l.addView(v,p);}
 void build(){root=new LinearLayout(this);root.setOrientation(1);root.setPadding(dp(18),dp(18),dp(18),dp(12));root.setBackgroundColor(bg);setContentView(root);
  TextView title=text("ZeroLink.",28);title.setTypeface(null,1);add(root,title);status=text("Offline · pair your laptop",13);add(root,status);
  LinearLayout pair=new LinearLayout(this);pair.setOrientation(1);host=edit("Laptop IP (optional fallback)");key=edit("Pairing key");pin=edit("Certificate fingerprint");key.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_PASSWORD);host.setText(prefs.getString("host",""));key.setText(prefs.getString("key",""));pin.setText(prefs.getString("pin",""));add(pair,host);add(pair,key);add(pair,pin);
  Button connect=button("Save & connect");add(pair,connect);connect.setOnClickListener(v->{String h=host.getText().toString().trim(),k=key.getText().toString().trim(),p=pin.getText().toString().replace(":","").trim().toLowerCase(Locale.ROOT);if((!h.isEmpty()&&!privateIP(h))||!k.matches("[a-fA-F0-9]{64}")||!p.matches("[a-f0-9]{64}")){status.setText("Enter the pairing key and fingerprint shown on Windows. IP is optional.");return;}prefs.edit().putString("host",h).putString("key",k).putString("pin",p).putBoolean("auto",true).remove("seen").apply();DiscoveryService.start(this);if(Build.VERSION.SDK_INT>=33&&checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},9);pair.setVisibility(View.GONE);last="";refresh();sendPending();});
  Button settings=button("Pair / change laptop");add(root,settings);settings.setOnClickListener(v->pair.setVisibility(pair.getVisibility()==View.VISIBLE?View.GONE:View.VISIBLE));add(root,pair);if(configured())pair.setVisibility(View.GONE);
  Switch automatic=new Switch(this);automatic.setText("Auto-connect in background");automatic.setTextColor(ink);automatic.setChecked(prefs.getBoolean("auto",true));add(root,automatic);automatic.setOnCheckedChangeListener((v,on)->{prefs.edit().putBoolean("auto",on).apply();if(on&&configured()){DiscoveryService.start(this);if(Build.VERSION.SDK_INT>=33&&checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},9);}else if(!on){stopService(new Intent(this,DiscoveryService.class));}});
  scroll=new ScrollView(this);chat=new LinearLayout(this);chat.setOrientation(1);scroll.addView(chat);root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));message=edit("Message, note, link or code");message.setSingleLine(false);message.setMaxLines(4);add(root,message);
  LinearLayout actions=new LinearLayout(this);Button attach=button("Attach files"),send=button("Send message");actions.addView(attach,new LinearLayout.LayoutParams(0,-2,1));actions.addView(send,new LinearLayout.LayoutParams(0,-2,1));add(root,actions);attach.setOnClickListener(v->{Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.setType("*/*");i.putExtra(Intent.EXTRA_ALLOW_MULTIPLE,true);i.addCategory(Intent.CATEGORY_OPENABLE);startActivityForResult(i,7);});send.setOnClickListener(v->{String t=message.getText().toString();if(t.trim().isEmpty())return;sendText(t,true);});
 }
 boolean configured(){return prefs.getString("key","").length()==64&&prefs.getString("pin","").length()==64;}
 static boolean privateIP(String h){try{String[] p=h.split("\\.",-1);if(p.length!=4)return false;int[] a=new int[4];for(int i=0;i<4;i++){if(!p[i].matches("[0-9]{1,3}"))return false;a[i]=Integer.parseInt(p[i]);if(a[i]>255)return false;}return a[0]==10||(a[0]==192&&a[1]==168)||(a[0]==172&&a[1]>=16&&a[1]<=31);}catch(Exception e){return false;}}
 static String hex(byte[] b){StringBuilder s=new StringBuilder();for(byte x:b)s.append(String.format(Locale.ROOT,"%02x",x&255));return s.toString();}
 HttpsURLConnection connection(String path,String method)throws Exception{
  String target=prefs.getString("host","");for(int attempt=0;!privateIP(target)&&attempt<12;attempt++){Thread.sleep(750);target=prefs.getString("host","");}final String h=target;String finger=prefs.getString("pin",""),secret=prefs.getString("key","");if(!privateIP(h)||finger.length()!=64||secret.length()!=64)throw new IOException("Pair your laptop first");
  TrustManager[] trust={new X509TrustManager(){public X509Certificate[] getAcceptedIssuers(){return new X509Certificate[0];}public void checkClientTrusted(X509Certificate[] c,String a)throws java.security.cert.CertificateException{throw new java.security.cert.CertificateException("Not supported");}public void checkServerTrusted(X509Certificate[] c,String a)throws java.security.cert.CertificateException{try{if(c==null||c.length==0)throw new Exception();c[0].checkValidity();String actual=hex(MessageDigest.getInstance("SHA-256").digest(c[0].getEncoded()));if(!MessageDigest.isEqual(actual.getBytes("US-ASCII"),finger.getBytes("US-ASCII")))throw new Exception("Pin mismatch");}catch(Exception e){throw new java.security.cert.CertificateException("Laptop identity does not match pairing fingerprint",e);}}}};
  SSLContext ssl=SSLContext.getInstance("TLS");ssl.init(null,trust,new SecureRandom());HttpsURLConnection c=(HttpsURLConnection)new URL("https://"+h+":47821"+path).openConnection(Proxy.NO_PROXY);c.setSSLSocketFactory(ssl.getSocketFactory());c.setHostnameVerifier((hostname,session)->hostname.equals(h));c.setInstanceFollowRedirects(false);c.setRequestMethod(method);c.setConnectTimeout(3500);c.setReadTimeout(30000);c.setRequestProperty("Authorization","Bearer "+secret);return c;
 }
 String response(HttpsURLConnection c)throws Exception{int code=c.getResponseCode();if(code<200||code>=300)throw new IOException("Laptop returned "+code);try(InputStream in=c.getInputStream();ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1){out.write(b,0,n);if(out.size()>16*1024*1024)throw new IOException("History too large");}return out.toString("UTF-8");}finally{c.disconnect();}}
 void task(Runnable r){worker.execute(r);}
 void update(String s){runOnUiThread(()->status.setText(s));}
 void refresh(){if(!configured()||busy)return;busy=true;task(()->{try{loadHistory();}catch(Exception e){update("Searching for your laptop · check hotspot and receiver");}finally{runOnUiThread(()->busy=false);}});}
 void loadHistory()throws Exception{String raw=response(connection("/history","GET"));JSONArray a=new JSONArray(raw);runOnUiThread(()->{status.setText("Connected · offline hotspot");if(raw.equals(last))return;last=raw;chat.removeAllViews();for(int i=0;i<a.length();i++){JSONObject x=a.optJSONObject(i);if(x==null)continue;boolean mine="phone".equals(x.optString("from"));String body="file".equals(x.optString("kind"))?"FILE  "+x.optString("name")+"\n"+x.optLong("size")+" bytes · saved on laptop":x.optString("text");TextView t=text(body+"\n"+x.optString("from")+" · "+x.optString("time").replace("T"," "),15);t.setPadding(dp(13),dp(10),dp(13),dp(10));t.setBackgroundColor(mine?Color.rgb(27,75,66):panel);LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-2,-2);p.gravity=mine?android.view.Gravity.END:android.view.Gravity.START;p.bottomMargin=dp(9);chat.addView(t,p);}scroll.post(()->scroll.fullScroll(View.FOCUS_DOWN));});}
 void sendText(String t,boolean clear){if(!configured()){update("Pair your laptop first");return;}task(()->{try{HttpsURLConnection c=connection("/message","POST");c.setDoOutput(true);c.setRequestProperty("Content-Type","application/json");byte[] b=new JSONObject().put("text",t).toString().getBytes("UTF-8");c.setFixedLengthStreamingMode(b.length);try(OutputStream o=c.getOutputStream()){o.write(b);}response(c);runOnUiThread(()->{if(clear&&message.getText().toString().equals(t))message.setText("");});update("Message saved on laptop");loadHistory();}catch(Exception e){update("Message failed · retry when laptop is connected");}});}
 String name(Uri u){try(Cursor c=getContentResolver().query(u,new String[]{OpenableColumns.DISPLAY_NAME},null,null,null)){if(c!=null&&c.moveToFirst())return c.getString(0);}catch(Exception e){}return "file";}
 void sendFiles(ArrayList<Uri> list){if(!configured()){pending.addAll(list);update("Pair your laptop to send selected files");return;}task(()->{for(Uri u:list){String n=name(u);try{update("Sending "+n+"…");MessageDigest hash=MessageDigest.getInstance("SHA-256");HttpsURLConnection c=connection("/file?name="+URLEncoder.encode(n,"UTF-8"),"POST");c.setDoOutput(true);c.setChunkedStreamingMode(65536);try(InputStream in=getContentResolver().openInputStream(u);OutputStream out=c.getOutputStream()){if(in==null)throw new IOException("File unavailable");byte[] b=new byte[65536];int k;while((k=in.read(b))!=-1){out.write(b,0,k);hash.update(b,0,k);}}JSONObject result=new JSONObject(response(c));if(!hex(hash.digest()).equalsIgnoreCase(result.optString("sha")))throw new IOException("Checksum mismatch");update("Saved: "+n);}catch(Exception e){update("Failed: "+n+" · select it again to retry");}}try{loadHistory();}catch(Exception ignored){}});}
 @Override protected void onActivityResult(int r,int result,Intent data){super.onActivityResult(r,result,data);if(r!=7||result!=RESULT_OK||data==null)return;ArrayList<Uri> list=new ArrayList<>();if(data.getClipData()!=null){for(int i=0;i<data.getClipData().getItemCount();i++)list.add(data.getClipData().getItemAt(i).getUri());}else if(data.getData()!=null)list.add(data.getData());sendFiles(list);}
 @SuppressWarnings("deprecation") void acceptIntent(Intent i){if(i==null)return;String a=i.getAction();if(Intent.ACTION_SEND.equals(a)||Intent.ACTION_SEND_MULTIPLE.equals(a)){String t=i.getStringExtra(Intent.EXTRA_TEXT);if(t!=null){message.setText(t);pendingText=t;}ArrayList<Uri> list=new ArrayList<>();if(Intent.ACTION_SEND_MULTIPLE.equals(a)){ArrayList<Uri> x=i.getParcelableArrayListExtra(Intent.EXTRA_STREAM);if(x!=null)list.addAll(x);}else{Uri u=i.getParcelableExtra(Intent.EXTRA_STREAM);if(u!=null)list.add(u);}pending.addAll(list);if(configured())sendPending();}}
 void sendPending(){if(pendingText!=null){String t=pendingText;pendingText=null;sendText(t,true);}if(!pending.isEmpty()){ArrayList<Uri> a=new ArrayList<>(pending);pending.clear();sendFiles(a);}}
}
