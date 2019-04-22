package com.fouste.openring;


import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.inputmethodservice.ExtractEditText;
import android.net.sip.SipSession;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.RatingBar;
import android.widget.SeekBar;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import org.w3c.dom.Text;


/**
 * A simple {@link Fragment} subclass.
 */
public class OptionsFragment extends Fragment {
    private static final String TAG = "4DBG";


    private EditText adressInput;
    private TextView adressInfo;
    private Switch dropboxSwitch;
    private EditText dropboxEditText;
    private SeekBar faceFrames;
    private SeekBar motionFrames;
    private EditText secondsEditText;

    //SocketCall activityCommander;
    private SendMessage pidgeon = new SendMessage();


    public OptionsFragment() {
        // Required empty public constructor
    }

    //THIS INTERFACE IS NOT NEEDED AS SENDMESSAGE CLASS CAN BE CALLED FROM FRAGMENT
//    // Make interface
//    public interface SocketCall{
//        void sendMessage(String  message);
//    }
//    @Override
//    public void onAttach(Context context) {
//        super.onAttach(context);
//        if(context instanceof SocketCall) {
//            activityCommander = (SocketCall) context;
//        }
//    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View view = inflater.inflate(R.layout.fragment_options, container, false);


        // Find references to Text
        adressInput = (EditText) view.findViewById(R.id.optionsWebAdressEditText);
        adressInfo = (TextView) view.findViewById(R.id.optionsWebAdressTextView);
        dropboxSwitch = (Switch) view.findViewById(R.id.optionsDropboxSwitch);
        dropboxEditText = (EditText) view.findViewById(R.id.optionsDropboxEditText);
        faceFrames = (SeekBar) view.findViewById(R.id.optionsFaceSeekBar);
        motionFrames = (SeekBar) view.findViewById(R.id.optionsMotionSeekBar);
        secondsEditText = (EditText) view.findViewById(R.id.optionsSecondsEditText);


        //Get user configuration and fill boxes with exxtracted info
        SharedPreferences sharedPref = getActivity().getSharedPreferences("userConf", Context.MODE_PRIVATE);
        String ip = sharedPref.getString("serverIp","188.2.18.204");
        adressInput.setText(ip);

        String dat = sharedPref.getString("dropbox_access_token","6dGbZTzREuAAAAAAAAAAPSQcX4tC4XW4BiojXXCb9ETgy4fAWL_8dAlCvXkzZxhg");
        dropboxEditText.setText(dat);

        boolean switchVal = sharedPref.getBoolean("use_dropbox",false);
        dropboxSwitch.setChecked(switchVal);

        int faceFramesVal = sharedPref.getInt("min_face_frames",4);
        faceFrames.setProgress(11-(faceFramesVal));

        int motionFramesVal = sharedPref.getInt("min_motion_frames",4);
        motionFrames.setProgress(11-(motionFramesVal));

        int sec = sharedPref.getInt("min_upload_seconds",3);
        secondsEditText.setText(Integer.toString(sec));

        // Implement button
        Button button = (Button) view.findViewById(R.id.optionsSaveDataButton);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Call save data method
                saveData(v);
                // Send update to server via interface activityCommander
                sendData(v);

                //activityCommander is not longer needed but left for future use
                //activityCommander.sendMessage("token=None");


            }
        });
        return view;
    }



    public void saveData(View view) {
        SharedPreferences sharedPref = this.getActivity().getSharedPreferences("userConf",0);
        SharedPreferences.Editor editor = sharedPref.edit();

        editor.putString("ip",adressInput.getText().toString());
        editor.putString("dropbox_access_token",dropboxEditText.getText().toString());
        editor.putBoolean("use_dropbox",dropboxSwitch.isChecked());
        editor.putInt("min_face_frames", 11-faceFrames.getProgress());
        editor.putInt("min_motion_frames", 11-motionFrames.getProgress());
        editor.putInt("min_upload_seconds", Integer.parseInt(secondsEditText.getText().toString()));
    editor.apply();

        Toast.makeText(this.getActivity(), "Data Saved", Toast.LENGTH_LONG).show();
    }

    public void sendData(View view){
        SharedPreferences sharedPref = getActivity().getSharedPreferences("userConf", Context.MODE_PRIVATE);
        new SendMessage().execute("token="+sharedPref.getString("token",""));
        new SendMessage().execute("dropbox_access_token="+sharedPref.getString("dropbox_access_token","6dGbZTzREuAAAAAAAAAAPSQcX4tC4XW4BiojXXCb9ETgy4fAWL_8dAlCvXkzZxhg"));
        new SendMessage().execute("use_dropbox="+Boolean.toString(sharedPref.getBoolean("use_dropbox",false)));
        new SendMessage().execute("min_face_frames="+Integer.toString(sharedPref.getInt("min_face_frames",4)));
        new SendMessage().execute("min_motion_frames="+Integer.toString(sharedPref.getInt("min_motion_frames",4)));
        new SendMessage().execute("min_upload_seconds="+Integer.toString(sharedPref.getInt("min_upload_seconds",3)));

    }
}
