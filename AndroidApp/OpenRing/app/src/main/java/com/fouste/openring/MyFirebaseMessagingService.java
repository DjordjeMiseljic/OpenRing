package com.fouste.openring;

import android.content.Context;
import android.content.Intent;
import android.support.v4.view.ViewPager;
import android.util.Log;
import android.widget.Toast;

import com.google.firebase.iid.FirebaseInstanceId;
import com.google.firebase.messaging.FirebaseMessaging;
import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

public class MyFirebaseMessagingService extends FirebaseMessagingService {

    private String token;
    private static final String TAG = "4DBG";

    private SendMessage pidgeon = new SendMessage();


    @Override
    public void onNewToken(String s) {

        Log.i(TAG,"<fbms> Token is "+s);
        getSharedPreferences("userConf", MODE_PRIVATE).edit().putString("token", s).apply();
        //Send message via tcp
        pidgeon.execute("token="+s);
        super.onNewToken(s);

    }

    @Override
    public void onMessageReceived(RemoteMessage remoteMessage) {

        Log.i(TAG,"<fbms> Notification title is " + remoteMessage.getNotification().getTitle());
        Log.d(TAG, "From: " + remoteMessage.getFrom());


//         THIS BROADCAST IS NOT NEEDED AS ONMESSAGE IS NOT CALLED WHEN APP IS IN SLEEP/SHUT DOWN
//         IT WILL BE USED TO SEND TOAST TO USER WHEN SOMETHING IS DETECTED
//         UPDATES ARE NEEDED ON FIREBASE PART, AS ENABLING MANUAL FRAGMENT SWITCH WOULD BR COMPLICATED
//         broadcast to mainActivity, so it can change fragment
        Intent i = new Intent();
        i.setAction("com.fouste.openring");
        i.addFlags(Intent.FLAG_INCLUDE_STOPPED_PACKAGES);
        sendBroadcast(i);

        // Make a toast pop-up so user can be notified even if he is not watching stream fragment
        // Toast.makeText(MyFirebaseMessagingService.this.getApplicationContext(),"Warning: Detection! Switch to video stream",Toast.LENGTH_SHORT).show();

        // Check if message contains a data payload.
        if (remoteMessage.getData().size() > 0) {
            Log.d(TAG, "<fbms> Message data payload: " + remoteMessage.getData());
        }
        // Check if message contains a notification payload.
        if (remoteMessage.getNotification() != null) {
            Log.d(TAG, "<fbms> Message Notification Body: " + remoteMessage.getNotification().getBody());
        }

        super.onMessageReceived(remoteMessage);
   }



    public static String getToken(Context context) {
        return context.getSharedPreferences("userConf", MODE_PRIVATE).getString("token", "empty");
    }
}
