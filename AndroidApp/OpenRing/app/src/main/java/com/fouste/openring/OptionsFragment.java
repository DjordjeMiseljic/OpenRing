package com.fouste.openring;


import android.content.Context;
import android.content.SharedPreferences;
import android.inputmethodservice.ExtractEditText;
import android.os.Bundle;
import android.support.v4.app.Fragment;
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


    EditText adressInput;
    TextView adressInfo;



    public OptionsFragment() {
        // Required empty public constructor
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
                saveData(v);
            }
        });
        return view;
    }



    public void saveData(View view) {
        SharedPreferences sharedPref = this.getActivity().getSharedPreferences("defaultValues",0);
        SharedPreferences.Editor editor = sharedPref.edit();
        editor.putString("webAdress",adressInput.getText().toString());
        editor.apply();

        Toast.makeText(this.getActivity(), "Data Saved", Toast.LENGTH_LONG).show();
    }
}
