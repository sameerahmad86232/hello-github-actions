package dev.zerolink.local;

import android.app.*;
import android.content.*;
import android.os.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.util.*;

public final class DiscoveryService extends Service {
 static final String CHANNEL="zerolink_connection";
 static final int NOTIFICATION=1822, PHONE_PORT=47823, DESKTOP_PORT=47822;
 private volatile boolean running=false;
 private volatile DatagramSocket socket;
 private Thread thread;
 private SharedPreferences prefs;
 private NotificationManager notifications;
 public static void start(Context c){
  Intent i=new Intent(c,DiscoveryService.class);
  try{c.startForegroundService(i);}catch(RuntimeException ignored){}
 }
 @Override public void onCreate(){
  super.onCreate();prefs=getSharedPreferences("pair",MODE_PRIVATE);
  notifications=getSystemService(NotificationManager.class);
  notifications.createNotificationChannel(new NotificationChannel(CHANNEL,"ZeroLink connection",NotificationManager.IMPORTANCE_LOW));
 }
 Notification notification(String text){
  Intent open=new Intent(this,MainActivity.class);
  PendingIntent pi=PendingIntent.getActivity(this,0,open,PendingIntent.FLAG_IMMUTABLE|PendingIntent.FLAG_UPDATE_CURRENT);
  return new Notification.Builder(this,CHANNEL).setSmallIcon(android.R.drawable.stat_sys_upload).setContentTitle("ZeroLink").setContentText(text).setContentIntent(pi).setOngoing(true).setOnlyAlertOnce(true).build();
 }
 @Override public int onStartCommand(Intent i,int flags,int id){
  startForeground(NOTIFICATION,notification("Searching for your paired laptop"));
  if(!prefs.getBoolean("auto",true)||prefs.getString("key","").length()!=64||prefs.getString("pin","").length()!=64){stopSelf();return START_NOT_STICKY;}
  if(!running){running=true;thread=new Thread(this::loop,"ZeroLink discovery");thread.start();}
  return START_STICKY;
 }
 @Override public IBinder onBind(Intent i){return null;}
 @Override public void onDestroy(){running=false;DatagramSocket s=socket;if(s!=null)s.close();if(thread!=null)thread.interrupt();super.onDestroy();}
 static String hex(byte[] b){StringBuilder s=new StringBuilder();for(byte x:b)s.append(String.format(Locale.ROOT,"%02x",x&255));return s.toString();}
 static String sign(String key,String payload)throws Exception{
  Mac mac=Mac.getInstance("HmacSHA256");mac.init(new SecretKeySpec(key.getBytes(StandardCharsets.UTF_8),"HmacSHA256"));
  return hex(mac.doFinal(payload.getBytes(StandardCharsets.UTF_8)));
 }
 byte[] query(String key,String fp)throws Exception{
  String p="ZL1-QUERY|"+fp+"|"+System.currentTimeMillis()/1000;
  return (p+"|"+sign(key,p)).getBytes(StandardCharsets.UTF_8);
 }
 boolean valid(String raw,String key,String fp)throws Exception{
  String[] p=raw.split("\\|",-1);if(p.length!=4||!p[0].equals("ZL1-BEACON")||!p[1].equals(fp))return false;
  long t=Long.parseLong(p[2]),now=System.currentTimeMillis()/1000;if(t<now-120||t>now+120)return false;
  String expected=sign(key,p[0]+"|"+p[1]+"|"+p[2]);return MessageDigest.isEqual(expected.getBytes(StandardCharsets.US_ASCII),p[3].getBytes(StandardCharsets.US_ASCII));
 }
 void send(DatagramSocket s,InetAddress ip,byte[] bytes){try{s.send(new DatagramPacket(bytes,bytes.length,ip,DESKTOP_PORT));}catch(Exception ignored){}}
 void discover(DatagramSocket s,String key,String fp)throws Exception{
  byte[] q=query(key,fp);String old=prefs.getString("host","");
  if(MainActivity.privateIP(old))send(s,InetAddress.getByName(old),q);
  send(s,InetAddress.getByName("255.255.255.255"),q);
  Enumeration<NetworkInterface> en=NetworkInterface.getNetworkInterfaces();
  if(en!=null)while(en.hasMoreElements()){
   NetworkInterface n=en.nextElement();if(!n.isUp()||n.isLoopback())continue;
   for(InterfaceAddress a:n.getInterfaceAddresses())if(a.getAddress() instanceof Inet4Address&&MainActivity.privateIP(a.getAddress().getHostAddress())&&a.getBroadcast()!=null)send(s,a.getBroadcast(),q);
  }
 }
 void loop(){
  while(running){
   try(DatagramSocket s=new DatagramSocket(null)){
    socket=s;s.setReuseAddress(true);s.setBroadcast(true);s.bind(new InetSocketAddress(PHONE_PORT));s.setSoTimeout(1500);
    long sent=0,seen=0;String label="";
    while(running){
     String key=prefs.getString("key",""),fp=prefs.getString("pin","");long now=SystemClock.elapsedRealtime();
     if(key.length()!=64||fp.length()!=64){Thread.sleep(1500);continue;}
     if(now-sent>=8000||sent==0){try{discover(s,key,fp);}catch(Exception ignored){}sent=now;}
     try{
      byte[] buf=new byte[512];DatagramPacket p=new DatagramPacket(buf,buf.length);s.receive(p);
      String ip=p.getAddress().getHostAddress();
      if(MainActivity.privateIP(ip)&&valid(new String(p.getData(),p.getOffset(),p.getLength(),StandardCharsets.UTF_8),key,fp)
         &&key.equals(prefs.getString("key",""))&&fp.equals(prefs.getString("pin",""))){
       prefs.edit().putString("host",ip).putLong("seen",System.currentTimeMillis()).apply();seen=SystemClock.elapsedRealtime();
      }
     }catch(Exception ignored){}
     String next=(seen!=0&&SystemClock.elapsedRealtime()-seen<25000)?"Paired laptop detected · ready to transfer":"Searching for your paired laptop";
     if(!next.equals(label)&&running){notifications.notify(NOTIFICATION,notification(next));label=next;}
    }
   }catch(Exception e){if(running)try{Thread.sleep(3000);}catch(InterruptedException ignored){}}
   finally{socket=null;}
  }
 }
}
