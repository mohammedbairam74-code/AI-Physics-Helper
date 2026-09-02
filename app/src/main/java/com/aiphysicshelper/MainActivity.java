package com.aiphysicshelper;

import android.app.*;
import android.os.Bundle;
import android.content.*;
import android.graphics.Color;
import android.net.Uri;
import android.view.*;
import android.webkit.*;
import android.widget.*;

public class MainActivity extends Activity {
    private WebView web;
    private android.content.SharedPreferences prefs;
    private static final int PICK_IMAGE=42;
    private ValueCallback<Uri[]> uploadCallback;
    private String apiBase(){ return prefs.getString("api_base", "http://10.0.2.2:8000"); }

    @Override public void onCreate(Bundle b){ super.onCreate(b); prefs=getSharedPreferences("physics",MODE_PRIVATE); showMain(); }
    private void showMain(){
        LinearLayout root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL); root.setBackgroundColor(Color.rgb(8,17,31));
        LinearLayout bar=new LinearLayout(this); bar.setGravity(Gravity.CENTER_VERTICAL); bar.setPadding(18,8,12,8);
        TextView title=new TextView(this); title.setText("🔬 AI Physics Helper"); title.setTextColor(Color.WHITE); title.setTextSize(19); title.setTypeface(null,1);
        bar.addView(title,new LinearLayout.LayoutParams(0,58,1));
        Button settings=new Button(this); settings.setText("⚙"); settings.setOnClickListener(v->showSettings()); bar.addView(settings,new LinearLayout.LayoutParams(60,58));
        root.addView(bar);
        web=new WebView(this); WebSettings ws=web.getSettings(); ws.setJavaScriptEnabled(true); ws.setDomStorageEnabled(true); ws.setAllowFileAccess(true); ws.setAllowContentAccess(true); ws.setBuiltInZoomControls(false);
        web.setWebViewClient(new WebViewClient()); web.setWebChromeClient(new WebChromeClient(){
            @Override public boolean onShowFileChooser(WebView w, ValueCallback<Uri[]> cb, FileChooserParams p){ uploadCallback=cb; Intent i=new Intent(Intent.ACTION_GET_CONTENT); i.setType("image/*"); i.addCategory(Intent.CATEGORY_OPENABLE); startActivityForResult(i,PICK_IMAGE); return true; }
        });
        web.loadUrl("file:///android_asset/index.html?api="+Uri.encode(apiBase()));
        root.addView(web,new LinearLayout.LayoutParams(-1,0,1)); setContentView(root);
    }
    private void showSettings(){
        final EditText input=new EditText(this); input.setSingleLine(true); input.setText(apiBase()); input.setHint("https://your-server.example.com");
        LinearLayout box=new LinearLayout(this); box.setPadding(30,10,30,0); box.setOrientation(LinearLayout.VERTICAL);
        TextView note=new TextView(this); note.setText("عنوان خادم AI Physics Helper. لا تضع مفتاح OpenAI هنا."); note.setPadding(0,0,0,12); box.addView(note); box.addView(input);
        new AlertDialog.Builder(this).setTitle("إعداد الخادم").setView(box).setPositiveButton("حفظ",(d,w)->{ prefs.edit().putString("api_base",normalize(input.getText().toString())).apply(); web.reload(); }).setNegativeButton("إلغاء",null).show();
    }
    private String normalize(String s){ s=s.trim(); while(s.endsWith("/")) s=s.substring(0,s.length()-1); return s; }
    @Override protected void onActivityResult(int req,int res,Intent data){ super.onActivityResult(req,res,data); if(req==PICK_IMAGE && uploadCallback!=null){ Uri[] r=(res==RESULT_OK && data!=null && data.getData()!=null)?new Uri[]{data.getData()}:null; uploadCallback.onReceiveValue(r); uploadCallback=null; } }
    @Override public void onBackPressed(){ if(web!=null && web.canGoBack()) web.goBack(); else super.onBackPressed(); }
}
