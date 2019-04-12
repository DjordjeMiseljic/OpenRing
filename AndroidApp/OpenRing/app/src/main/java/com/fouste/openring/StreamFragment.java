package com.fouste.openring;


import android.os.Bundle;
import android.support.v4.app.Fragment;
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

    private WebView webView;

    public StreamFragment() {
        // Required empty public constructor

    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_stream, container, false);
        webView = (WebView) view.findViewById(R.id.streamWebView);
        webView.setWebViewClient(new WebViewClient());
        webView.loadUrl("http://www.google.com");
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        // Inflate the layout for this fragment
        return view;
    }



}
