"""Adds the notification icon (mode 'icon') and, in mode 'full', the Thrive home-screen widget."""
import os, sys
mode = sys.argv[1] if len(sys.argv) > 1 else 'icon'
base = 'android/app/src/main'; res = base + '/res'; pkg = base + '/java/com/thrive/money'
def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(text)

w(res + '/drawable/ic_stat_thrive.xml', '''<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
  <path android:fillColor="#FFFFFFFF" android:pathData="M12,22V12 M12,16C12,10 8,8 4,8c0,5 3,8 8,8z M12,13c0,-6 4,-8 8,-8c0,5 -3,8 -8,8z"/>
</vector>
''')
if mode != 'full':
    sys.exit(0)

w(pkg + '/MainActivity.java', '''package com.thrive.money;

import android.content.Intent;
import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(ThriveWidgetPlugin.class);
        super.onCreate(savedInstanceState);
        handleRoute(getIntent());
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        handleRoute(intent);
    }

    private void handleRoute(Intent i) {
        if (i == null) return;
        final String r = i.getStringExtra("route");
        if (r == null || r.isEmpty()) return;
        i.removeExtra("route");
        final String js = "location.hash='" + r.replaceAll("[^a-z]", "") + "'";
        getBridge().getWebView().postDelayed(new Runnable() {
            @Override public void run() { getBridge().getWebView().evaluateJavascript(js, null); }
        }, 500);
    }
}
''')
w(pkg + '/ThriveWidgetPlugin.java', '''package com.thrive.money;

import android.content.Context;
import android.content.SharedPreferences;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "ThriveWidget")
public class ThriveWidgetPlugin extends Plugin {
    @PluginMethod
    public void update(PluginCall call) {
        Context ctx = getContext();
        SharedPreferences.Editor ed = ctx.getSharedPreferences("thrive_widget", Context.MODE_PRIVATE).edit();
        ed.putString("title", call.getString("title", "Left today"));
        ed.putString("amount", call.getString("amount", "Open Thrive"));
        ed.putString("sub", call.getString("sub", ""));
        ed.putString("balance", call.getString("balance", "Open Thrive"));
        Integer pct = call.getInt("pct", 0);
        ed.putInt("pct", pct == null ? 0 : pct);
        ed.apply();
        ThriveWidgetProvider.refreshAll(ctx);
        ThriveQuickWidgetProvider.refreshAll(ctx);
        call.resolve();
    }
}
''')
w(pkg + '/ThriveWidgetProvider.java', '''package com.thrive.money;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.widget.RemoteViews;

public class ThriveWidgetProvider extends AppWidgetProvider {
    @Override
    public void onUpdate(Context ctx, AppWidgetManager mgr, int[] ids) {
        for (int id : ids) draw(ctx, mgr, id);
    }

    static void draw(Context ctx, AppWidgetManager mgr, int id) {
        SharedPreferences p = ctx.getSharedPreferences("thrive_widget", Context.MODE_PRIVATE);
        RemoteViews v = new RemoteViews(ctx.getPackageName(), R.layout.thrive_widget);
        v.setTextViewText(R.id.w_title, p.getString("title", "Left today"));
        v.setTextViewText(R.id.w_amount, p.getString("amount", "Open Thrive"));
        v.setTextViewText(R.id.w_sub, p.getString("sub", "Tap to set up"));
        v.setProgressBar(R.id.w_bar, 100, p.getInt("pct", 0), false);
        Intent i = new Intent(ctx, MainActivity.class);
        i.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pi = PendingIntent.getActivity(ctx, 0, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        v.setOnClickPendingIntent(R.id.w_root, pi);
        mgr.updateAppWidget(id, v);
    }

    static void refreshAll(Context ctx) {
        AppWidgetManager m = AppWidgetManager.getInstance(ctx);
        int[] ids = m.getAppWidgetIds(new ComponentName(ctx, ThriveWidgetProvider.class));
        for (int id : ids) draw(ctx, m, id);
    }
}
''')
w(pkg + '/ThriveQuickWidgetProvider.java', '''package com.thrive.money;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.widget.RemoteViews;

public class ThriveQuickWidgetProvider extends AppWidgetProvider {
    @Override
    public void onUpdate(Context ctx, AppWidgetManager mgr, int[] ids) {
        for (int id : ids) draw(ctx, mgr, id);
    }

    static PendingIntent pi(Context ctx, String route, int code) {
        Intent i = new Intent(ctx, MainActivity.class);
        i.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        if (route != null && !route.isEmpty()) i.putExtra("route", route);
        return PendingIntent.getActivity(ctx, code, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    static void draw(Context ctx, AppWidgetManager mgr, int id) {
        SharedPreferences p = ctx.getSharedPreferences("thrive_widget", Context.MODE_PRIVATE);
        RemoteViews v = new RemoteViews(ctx.getPackageName(), R.layout.thrive_quick_widget);
        v.setTextViewText(R.id.q_balance, p.getString("balance", "Open Thrive"));
        v.setOnClickPendingIntent(R.id.q_add, pi(ctx, "add", 11));
        v.setOnClickPendingIntent(R.id.q_open, pi(ctx, "", 12));
        mgr.updateAppWidget(id, v);
    }

    static void refreshAll(Context ctx) {
        AppWidgetManager m = AppWidgetManager.getInstance(ctx);
        int[] ids = m.getAppWidgetIds(new ComponentName(ctx, ThriveQuickWidgetProvider.class));
        for (int id : ids) draw(ctx, m, id);
    }
}
''')
w(res + '/layout/thrive_quick_widget.xml', '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:orientation="horizontal" android:gravity="center_vertical"
    android:padding="14dp" android:background="@drawable/thrive_widget_bg">
    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1" android:orientation="vertical">
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Available" android:textColor="#9CB3A9" android:textSize="12sp" android:textStyle="bold"/>
        <TextView android:id="@+id/q_balance" android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="Open Thrive" android:textColor="#F1F8F4" android:textSize="22sp" android:textStyle="bold"/>
    </LinearLayout>
    <TextView android:id="@+id/q_add" android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:text="+ Add" android:textColor="#04241A" android:textSize="14sp" android:textStyle="bold"
        android:paddingLeft="16dp" android:paddingRight="16dp" android:paddingTop="10dp" android:paddingBottom="10dp"
        android:background="@drawable/thrive_btn_bg"/>
    <TextView android:id="@+id/q_open" android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:text="Open" android:textColor="#F1F8F4" android:textSize="14sp" android:textStyle="bold"
        android:paddingLeft="12dp" android:paddingRight="4dp" android:paddingTop="10dp" android:paddingBottom="10dp"/>
</LinearLayout>
''')
w(res + '/drawable/thrive_btn_bg.xml', '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#14B884"/>
    <corners android:radius="16dp"/>
</shape>
''')
w(res + '/xml/thrive_quick_widget_info.xml', '''<?xml version="1.0" encoding="utf-8"?>
<appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android"
    android:minWidth="250dp" android:minHeight="70dp"
    android:updatePeriodMillis="1800000"
    android:initialLayout="@layout/thrive_quick_widget"
    android:resizeMode="horizontal"
    android:widgetCategory="home_screen"
    android:description="@string/thrive_quick_desc"/>
''')
w(res + '/layout/thrive_widget.xml', '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/w_root"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp"
    android:background="@drawable/thrive_widget_bg">
    <TextView android:id="@+id/w_title" android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:text="Left today" android:textColor="#9CB3A9" android:textSize="13sp" android:textStyle="bold"/>
    <TextView android:id="@+id/w_amount" android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:text="Open Thrive" android:textColor="#F1F8F4" android:textSize="30sp" android:textStyle="bold"
        android:layout_marginTop="2dp"/>
    <ProgressBar android:id="@+id/w_bar" style="?android:attr/progressBarStyleHorizontal"
        android:layout_width="match_parent" android:layout_height="6dp" android:max="100" android:progress="0"
        android:progressTint="#14B884" android:progressBackgroundTint="#22332C" android:layout_marginTop="10dp"/>
    <TextView android:id="@+id/w_sub" android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:text="Tap to set up" android:textColor="#9CB3A9" android:textSize="12sp" android:layout_marginTop="8dp"/>
</LinearLayout>
''')
w(res + '/drawable/thrive_widget_bg.xml', '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#0D1714"/>
    <corners android:radius="24dp"/>
    <stroke android:width="1dp" android:color="#2A3D35"/>
</shape>
''')
w(res + '/xml/thrive_widget_info.xml', '''<?xml version="1.0" encoding="utf-8"?>
<appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android"
    android:minWidth="180dp" android:minHeight="110dp"
    android:updatePeriodMillis="1800000"
    android:initialLayout="@layout/thrive_widget"
    android:resizeMode="horizontal|vertical"
    android:widgetCategory="home_screen"
    android:description="@string/thrive_widget_desc"/>
''')
w(res + '/values/thrive_widget_strings.xml', '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="thrive_widget_desc">Shows what you can spend today</string>
    <string name="thrive_quick_desc">Your balance with a quick add button</string>
</resources>
''')
mf = base + '/AndroidManifest.xml'
s = open(mf, encoding='utf-8').read()
if 'ThriveWidgetProvider' not in s:
    rcv = '''
        <receiver android:name=".ThriveWidgetProvider" android:exported="true">
            <intent-filter><action android:name="android.appwidget.action.APPWIDGET_UPDATE"/></intent-filter>
            <meta-data android:name="android.appwidget.provider" android:resource="@xml/thrive_widget_info"/>
        </receiver>
'''
    rcv2 = '''
        <receiver android:name=".ThriveQuickWidgetProvider" android:exported="true">
            <intent-filter><action android:name="android.appwidget.action.APPWIDGET_UPDATE"/></intent-filter>
            <meta-data android:name="android.appwidget.provider" android:resource="@xml/thrive_quick_widget_info"/>
        </receiver>
'''
    s = s.replace('</application>', rcv + rcv2 + '    </application>', 1)
    open(mf, 'w', encoding='utf-8').write(s)
print('patched', mode)
