package com.fouste.openring;

import android.content.Context;
import android.content.Intent;
import android.support.v4.view.ViewPager;
import android.util.Log;

import com.google.firebase.iid.FirebaseInstanceId;
import com.google.firebase.messaging.FirebaseMessaging;
import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

public class MyFirebaseMessagingService extends FirebaseMessagingService {

    private String token;
    private static final String TAG = "4DBG";



    @Override
    public void onNewToken(String s) {

        Log.i(TAG,"<fbms> Token is "+s);
        getSharedPreferences("_", MODE_PRIVATE).edit().putString("fb", s).apply();
        super.onNewToken(s);

    }

    @Override
    public void onMessageReceived(RemoteMessage remoteMessage) {

        Log.i(TAG,"<fbms> Notification title is " + remoteMessage.getNotification().getTitle());
        Log.d(TAG, "From: " + remoteMessage.getFrom());


        //broadcast to mainActivity, so it can change fragment
        Intent i = new Intent();
        i.setAction("com.fouste.openring");
        i.addFlags(Intent.FLAG_INCLUDE_STOPPED_PACKAGES);
        sendBroadcast(i);





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
        return context.getSharedPreferences("_", MODE_PRIVATE).getString("fb", "empty");
    }
}
