package com.fouste.openring;


import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
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
        //setup webView
        webView = (WebView) view.findViewById(R.id.streamWebView);
        webView.setWebViewClient(new WebViewClient());
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setBuiltInZoomControls(true);
        webSettings.setLoadWithOverviewMode(true);
        webView.setInitialScale(110);
        //webSettings.setUseWideViewPort(true);
        //webSettings.setDefaultZoom(WebSettings.ZoomDensity.FAR);

        // Inflate the layout for this fragment
        return view;
    }




    public void disconnect(){
        Log.i(TAG, "<strm> DISCONNECT");

        webView.loadUrl("");
    }
    public void connect(){
        Log.i(TAG, "<strm> CONNECT");
        //extract saved web adress
        SharedPreferences sharedPref = this.getActivity().getSharedPreferences("userConf", Context.MODE_PRIVATE);
        String ip = sharedPref.getString("serverIp","188.2.18.204");
        Log.i(TAG, "http://" + ip + ":5000");

        //setup url
        webView.loadUrl("http://" + ip + ":5000");
    }

}
