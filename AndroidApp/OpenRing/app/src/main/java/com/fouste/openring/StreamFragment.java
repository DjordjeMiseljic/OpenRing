package com.fouste.openring;


import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;


/**
 * A simple {@link Fragment} subclass.
 */
public class StreamFragment extends Fragment {
    private static final String TAG = "4DBG";

    public WebView webView;

    public StreamFragment() {
        // Required empty public constructor

    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_stream, container, false);
        //extract saved web adress
        SharedPreferences sharedPref = this.getActivity().getSharedPreferences("userData", Context.MODE_PRIVATE);
        String url = sharedPref.getString("webAdress","http://188.2.18.204:5000");
        //setup webView
        webView = (WebView) view.findViewById(R.id.streamWebView);
        webView.setWebViewClient(new WebViewClient());
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setBuiltInZoomControls(true);

        // Inflate the layout for this fragment
        return view;
    }

    @Override
    public void onPause() {
        webView.loadUrl("");
        super.onPause();
    }

    public void disconnect(){
        Log.i(TAG, "DISCONNECT");
        //webView = (WebView) getView().findViewById(R.id.streamWebView);
        //webView.setWebViewClient(new WebViewClient());
        webView.loadUrl("");
    }
    public void connect(){
        Log.i(TAG, "CONNECT");

        //webView = (WebView) getView().findViewById(R.id.streamWebView);
        //webView.setWebViewClient(new WebViewClient());
        webView.loadUrl("http://188.2.18.204:5000");
    }

}