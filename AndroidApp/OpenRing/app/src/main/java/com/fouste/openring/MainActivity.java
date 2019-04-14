package com.fouste.openring;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.support.annotation.NonNull;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.design.widget.TabLayout;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;

import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentPagerAdapter;
import android.support.v4.view.ViewPager;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;

import android.view.WindowManager;
import android.webkit.WebView;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.OnSuccessListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.FirebaseApp;
import com.google.firebase.iid.FirebaseInstanceId;
import com.google.firebase.iid.FirebaseInstanceIdService;
import com.google.firebase.iid.InstanceIdResult;
import com.google.firebase.messaging.FirebaseMessagingService;

import java.io.StringReader;

public class MainActivity extends AppCompatActivity{

    /**
     * The {@link android.support.v4.view.PagerAdapter} that will provide
     * fragments for each of the sections. We use a
     * {@link FragmentPagerAdapter} derivative, which will keep every
     * loaded fragment in memory. If this becomes too memory intensive, it
     * may be best to switch to a
     * {@link android.support.v4.app.FragmentStatePagerAdapter}.
     */
    private static final String TAG = "4DBG";

    private String token;
    private BroadcastReceiver mReceiver;
    private Fragment left, middle, right;
    private int currPos=1;
    private SectionsPagerAdapter mSectionsPagerAdapter;
    public ViewPager mViewPager;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        // ADD TOOLBAR
        //Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        //setSupportActionBar(toolbar);


        // Create the adapter that will return a fragment for each of the three
        // primary sections of the activity.
        mSectionsPagerAdapter = new SectionsPagerAdapter(getSupportFragmentManager());

        // Set up the ViewPager with the sections adapter.
        mViewPager = (ViewPager) findViewById(R.id.container);
        mViewPager.setAdapter(mSectionsPagerAdapter);
        mViewPager.setCurrentItem(1);
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_PAN);

        IntentFilter intentFilter = new IntentFilter(
                "com.fouste.openring");
        mReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
//                //extract our message from intent
//                String msg_for_me = intent.getStringExtra("some_msg");
//                //log our message value
//                Log.i(TAG, "BCAST RECIEVED");
//                mViewPager.setCurrentItem(2,true);
                  Toast.makeText(MainActivity.this, "Detection", Toast.LENGTH_LONG).show();
            }
        };
        this.registerReceiver(mReceiver, intentFilter);



        mViewPager.addOnPageChangeListener(new ViewPager.SimpleOnPageChangeListener(){
            @Override
            public void onPageSelected(int position) {
                // Check if this is the page you want.
                switch(position){
                    case 0:
                        Log.i(TAG, "<main> LEFT");
                        currPos=0;
                        ((StreamFragment)right).disconnect();
                        break;
                    case 1:
                        Log.i(TAG, "<main> MIDDLE");
                        currPos=1;
                        ((StreamFragment)right).disconnect();
                        break;
                    case 2:
                        Log.i(TAG, "<main> RIGHT");
                        currPos=2;
                        ((StreamFragment)right).connect();
                        break;
                }

            }
        });


        FirebaseApp.initializeApp(this);
        FirebaseInstanceId.getInstance().getInstanceId().addOnSuccessListener( MainActivity.this,  new OnSuccessListener<InstanceIdResult>() {
            @Override
            public void onSuccess(InstanceIdResult instanceIdResult) {
                String token = instanceIdResult.getToken();
                Log.i(TAG,"Token: "+ token);
            }
        });
        //Log.i(TAG, "<main> static get token: "+ MyFirebaseMessagingService.getToken(this));
        //token = MyFirebaseMessagingService.getToken(this);
        //getSharedPreferences("_", MODE_PRIVATE).edit().putString("fb", token).apply();
        //Log.i(TAG, "<main> get token: "+ token);





    } // END OF ON CREATE *****



    @Override
    public void onPause() {
        ((StreamFragment)right).disconnect();
        super.onPause();
    }

    @Override
    public void onResume() {
        if(currPos==2)
            ((StreamFragment)right).connect();
        super.onResume();
    }

    /**
     * A {@link FragmentPagerAdapter} that returns a fragment corresponding to
     * one of the sections/tabs/pages.
     */
    public class SectionsPagerAdapter extends FragmentPagerAdapter {

        public SectionsPagerAdapter(FragmentManager fm) {
            super(fm);
        }

        @Override
        public Fragment getItem(int position) {
            // getItem is called to instantiate the fragment for the given page.
            // Return a PlaceholderFragment (defined as a static inner class below).
            switch(position){
                case 0:
                    if(left == null)
                        left = new OptionsFragment();
                    return left;
                case 1:
                    if(middle== null)
                        middle = new HomeFragment();
                    return middle;
                case 2:
                    if(right== null)
                        right = new StreamFragment();
                    return right;
            }
            return null;
        }

        @Override
        public int getCount() {
            // Show 3 total pages.
            return 3;
        }
    }






}
