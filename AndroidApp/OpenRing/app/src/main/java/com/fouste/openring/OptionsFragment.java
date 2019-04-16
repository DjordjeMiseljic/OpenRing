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
import android.widget.TextView;
import android.widget.Toast;

import org.w3c.dom.Text;


/**
 * A simple {@link Fragment} subclass.
 */
public class OptionsFragment extends Fragment {
    private static final String TAG = "4DBG";


    EditText adressInput;
    TextView adressInfo;
    SocketCall activityCommander;


    public OptionsFragment() {
        // Required empty public constructor
    }

    // Make interface
    public interface SocketCall{
        void sendMessage(String  message);
    }


    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if(context instanceof SocketCall) {
            activityCommander = (SocketCall) context;
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View view = inflater.inflate(R.layout.fragment_options, container, false);

        // Find references to Text
        adressInput = (EditText) view.findViewById(R.id.optionsWebAdressEditText);
        adressInfo = (TextView) view.findViewById(R.id.optionsWebAdressTextView);




        // Implement button
        Button button = (Button) view.findViewById(R.id.optionsSaveDataButton);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Call save data method
                saveData(v);
                // Send update to server via interface activityCommander
                SharedPreferences sharedPref = getActivity().getSharedPreferences("userConf", Context.MODE_PRIVATE);
                String ip = sharedPref.getString("serverIp","188.2.18.204");
                Log.i(TAG,"Sending mesage "+ip);

                activityCommander.sendMessage("ip is: "+ip);

            }
        });
        return view;
    }



    public void saveData(View view) {
        SharedPreferences sharedPref = this.getActivity().getSharedPreferences("userConf",0);
        SharedPreferences.Editor editor = sharedPref.edit();
        editor.putString("ip",adressInput.getText().toString());
        editor.apply();

        Toast.makeText(this.getActivity(), "Data Saved", Toast.LENGTH_LONG).show();
    }
}
