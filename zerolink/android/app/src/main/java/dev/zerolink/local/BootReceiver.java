package dev.zerolink.local;
import android.content.*;
public final class BootReceiver extends BroadcastReceiver {
 @Override public void onReceive(Context c,Intent i){
  if(Intent.ACTION_BOOT_COMPLETED.equals(i.getAction())&&c.getSharedPreferences("pair",Context.MODE_PRIVATE).getBoolean("auto",true)&&c.getSharedPreferences("pair",Context.MODE_PRIVATE).getString("key","").length()==64)DiscoveryService.start(c);
 }
}
