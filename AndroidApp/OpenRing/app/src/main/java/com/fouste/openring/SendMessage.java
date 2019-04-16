package com.fouste.openring;

import android.os.AsyncTask;
import android.util.Log;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.Socket;
import java.nio.Buffer;

public class SendMessage extends AsyncTask <String, Void, Void> {
    private Exception exception;
    private static final String TAG = "4DBG";

    @Override
    protected Void doInBackground(String... params) {
        try{
            try{
                Socket socket = new Socket("192.168.0.16",5004);
                Log.i(TAG,"Connected");
                PrintWriter outToServer = new PrintWriter(new OutputStreamWriter(socket.getOutputStream()));
                outToServer.print(params[0]);
                outToServer.flush();

                Log.i(TAG,"Sent:" + params[0]);
                BufferedReader mBufferIn = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                String mServerMessage = mBufferIn.readLine();
                Log.i(TAG,"Read:" + mServerMessage);

                socket.close();


            }catch (IOException e){
                e.printStackTrace();
            }
        }catch (Exception e){
            this.exception = e;
            return null;
        }
        return null;
    }
}
