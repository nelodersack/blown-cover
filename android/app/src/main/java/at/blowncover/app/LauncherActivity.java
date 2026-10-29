package at.blowncover.app;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.location.LocationManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.PowerManager;
import android.provider.Settings;
import android.text.Editable;
import android.text.InputType;
import android.text.TextWatcher;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

/** Startbildschirm: Bereitschaft prüfen, Adresse wählen, Spiel öffnen, Diagnose ansehen. */
public class LauncherActivity extends Activity {
    private static final int RC_LOC = 11, RC_NOT = 12;
    private static final int FG = 0xFFE9EEF3, MUT = 0xFF8D99A8, OK = 0xFF3FB56A, BAD = 0xFFE5484D;

    private TextView stLoc, stNot, stBat, stGps, stSvc, diag;
    private Button bLoc, bNot, bBat, bGps;
    private boolean openAfter;
    private final Handler h = new Handler(Looper.getMainLooper());
    private final Runnable tick = new Runnable() {
        @Override
        public void run() {
            refresh();
            h.postDelayed(this, 2000);
        }
    };

    private int dp(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }

    private TextView tv(String t, int sp, int color, boolean bold) {
        TextView v = new TextView(this);
        v.setText(t);
        v.setTextSize(sp);
        v.setTextColor(color);
        if (bold) v.setTypeface(Typeface.DEFAULT_BOLD);
        return v;
    }

    private Button btn(String t, boolean primary, View.OnClickListener l) {
        Button b = new Button(this);
        b.setText(t);
        b.setAllCaps(false);
        b.setTextColor(primary ? 0xFF0B0E12 : FG);
        GradientDrawable g = new GradientDrawable();
        g.setCornerRadius(dp(12));
        g.setColor(primary ? FG : 0xFF1B232C);
        if (!primary) g.setStroke(dp(1), 0xFF475262);
        b.setBackground(g);
        b.setMinHeight(dp(46));
        b.setMinimumHeight(dp(46));
        b.setOnClickListener(l);
        return b;
    }

    private LinearLayout.LayoutParams lp(int topDp) {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        p.topMargin = dp(topDp);
        return p;
    }

    private LinearLayout item(String label, TextView state, Button b) {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        TextView l = tv(label, 16, FG, false);
        row.addView(l, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
        row.addView(state);
        box.addView(row, lp(0));
        if (b != null) box.addView(b, lp(6));
        return box;
    }

    @Override
    protected void onCreate(Bundle sb) {
        super.onCreate(sb);
        ScrollView sv = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(20), dp(24), dp(20), dp(32));
        sv.addView(root);
        setContentView(sv);

        root.addView(tv("Blown Cover", 30, FG, true));
        root.addView(tv("App v" + Prefs.ver(this) + " · Hülle für die Website", 13, MUT, false), lp(2));

        root.addView(tv("BEREITSCHAFT", 12, MUT, true), lp(24));
        stLoc = tv("", 15, FG, true);
        bLoc = btn("Standort erlauben", false, new View.OnClickListener() {
            public void onClick(View v) {
                askLoc(false);
            }
        });
        root.addView(item("Standort", stLoc, bLoc), lp(10));
        stGps = tv("", 15, FG, true);
        bGps = btn("GPS einschalten", false, new View.OnClickListener() {
            public void onClick(View v) {
                startActivity(new Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS));
            }
        });
        root.addView(item("GPS", stGps, bGps), lp(10));
        stNot = tv("", 15, FG, true);
        bNot = btn("Benachrichtigungen erlauben", false, new View.OnClickListener() {
            public void onClick(View v) {
                askNot();
            }
        });
        root.addView(item("Benachrichtigungen", stNot, bNot), lp(10));
        stBat = tv("", 15, FG, true);
        bBat = btn("Akku-Optimierung ausschalten", false, new View.OnClickListener() {
            public void onClick(View v) {
                askBat();
            }
        });
        root.addView(item("Akku-Ausnahme", stBat, bBat), lp(10));
        stSvc = tv("", 15, FG, true);
        root.addView(item("Hintergrunddienst", stSvc, null), lp(10));

        Button go = btn("Spiel öffnen", true, new View.OnClickListener() {
            public void onClick(View v) {
                openGame();
            }
        });
        root.addView(go, lp(22));
        root.addView(btn("Dienst beenden", false, new View.OnClickListener() {
            public void onClick(View v) {
                startService(new Intent(LauncherActivity.this, LocationService.class).setAction(LocationService.ACT_STOP));
            }
        }), lp(8));

        root.addView(tv("ADRESSE", 12, MUT, true), lp(28));
        final RadioGroup rg = new RadioGroup(this);
        final RadioButton rLive = rb("Live-Seite (normal)"), rTest = rb("Testseite (index_app.html)"), rCustom = rb("Eigene Adresse");
        rg.addView(rLive);
        rg.addView(rTest);
        rg.addView(rCustom);
        String m = Prefs.mode(this);
        if ("test".equals(m)) rTest.setChecked(true);
        else if ("custom".equals(m)) rCustom.setChecked(true);
        else rLive.setChecked(true);
        root.addView(rg, lp(6));
        final EditText ec = new EditText(this);
        ec.setHint("https://…");
        ec.setHintTextColor(MUT);
        ec.setTextColor(FG);
        ec.setInputType(InputType.TYPE_TEXT_VARIATION_URI);
        ec.setSingleLine(true);
        ec.setText(Prefs.custom(this));
        ec.addTextChangedListener(new TextWatcher() {
            public void beforeTextChanged(CharSequence s, int a, int b, int c) {
            }

            public void onTextChanged(CharSequence s, int a, int b, int c) {
            }

            public void afterTextChanged(Editable e) {
                Prefs.setCustom(LauncherActivity.this, e.toString());
            }
        });
        root.addView(ec, lp(4));
        rg.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {
            public void onCheckedChanged(RadioGroup g, int id) {
                Prefs.setMode(LauncherActivity.this, id == rTest.getId() ? "test" : id == rCustom.getId() ? "custom" : "live");
            }
        });

        root.addView(tv("DIAGNOSE", 12, MUT, true), lp(28));
        diag = tv("", 11, MUT, false);
        diag.setTypeface(Typeface.MONOSPACE);
        diag.setTextIsSelectable(true);
        root.addView(diag, lp(6));
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        Button share = btn("Log teilen", false, new View.OnClickListener() {
            public void onClick(View v) {
                Intent i = new Intent(Intent.ACTION_SEND);
                i.setType("text/plain");
                i.putExtra(Intent.EXTRA_SUBJECT, "Blown Cover Diagnose");
                i.putExtra(Intent.EXTRA_TEXT, "Blown Cover App v" + Prefs.ver(LauncherActivity.this) + " · " + Build.MANUFACTURER + " " + Build.MODEL
                        + " · Android " + Build.VERSION.SDK_INT + "\n\n" + Diag.tail(LauncherActivity.this, 300));
                startActivity(Intent.createChooser(i, "Log teilen"));
            }
        });
        Button clr = btn("Log löschen", false, new View.OnClickListener() {
            public void onClick(View v) {
                Diag.clear(LauncherActivity.this);
                refresh();
            }
        });
        LinearLayout.LayoutParams half = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
        half.rightMargin = dp(6);
        row.addView(share, half);
        row.addView(clr, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
        root.addView(row, lp(10));
    }

    private RadioButton rb(String t) {
        RadioButton r = new RadioButton(this);
        r.setText(t);
        r.setTextColor(FG);
        r.setId(View.generateViewId());
        return r;
    }

    private boolean hasLoc() {
        return checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED;
    }

    private boolean needNot() {
        return Build.VERSION.SDK_INT >= 33;
    }

    private boolean hasNot() {
        return !needNot() || checkSelfPermission("android.permission.POST_NOTIFICATIONS") == PackageManager.PERMISSION_GRANTED;
    }

    private boolean batOk() {
        PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
        return pm.isIgnoringBatteryOptimizations(getPackageName());
    }

    private boolean gpsOn() {
        LocationManager lm = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
        return lm.isProviderEnabled(LocationManager.GPS_PROVIDER);
    }

    private void askLoc(boolean thenOpen) {
        openAfter = thenOpen;
        requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}, RC_LOC);
    }

    private void askNot() {
        requestPermissions(new String[]{"android.permission.POST_NOTIFICATIONS"}, RC_NOT);
    }

    private void askBat() {
        try {
            startActivity(new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, Uri.parse("package:" + getPackageName())));
        } catch (Exception e) {
            try {
                startActivity(new Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS));
            } catch (Exception e2) {
                Toast.makeText(this, "Bitte in den Android-Einstellungen die Akku-Optimierung für Blown Cover ausschalten", Toast.LENGTH_LONG).show();
            }
        }
    }

    private void openGame() {
        if (!hasLoc()) {
            askLoc(true);
            return;
        }
        if (needNot() && !hasNot()) {
            openAfter = true;
            askNot();
            return;
        }
        startForegroundService(new Intent(this, LocationService.class));
        startActivity(new Intent(this, GameActivity.class));
    }

    @Override
    public void onRequestPermissionsResult(int code, String[] perms, int[] res) {
        super.onRequestPermissionsResult(code, perms, res);
        refresh();
        if (!openAfter) return;
        if (code == RC_LOC) {
            if (hasLoc()) openGame();
            else openAfter = false;
        } else if (code == RC_NOT) {
            openAfter = false;
            // Auch ohne Benachrichtigungs-Erlaubnis starten (der Dienst läuft trotzdem, nur ohne sichtbare Meldungen)
            if (hasLoc()) {
                startForegroundService(new Intent(this, LocationService.class));
                startActivity(new Intent(this, GameActivity.class));
            }
        }
    }

    private void set(TextView t, boolean ok, String yes, String no, Button b) {
        t.setText(ok ? "✓ " + yes : "✗ " + no);
        t.setTextColor(ok ? OK : BAD);
        if (b != null) b.setVisibility(ok ? View.GONE : View.VISIBLE);
    }

    private void refresh() {
        set(stLoc, hasLoc(), "erlaubt", "fehlt", bLoc);
        set(stGps, gpsOn(), "an", "aus", bGps);
        if (needNot()) set(stNot, hasNot(), "erlaubt", "fehlt", bNot);
        else set(stNot, true, "nicht nötig", "", bNot);
        set(stBat, batOk(), "ausgenommen", "nicht ausgenommen", bBat);
        set(stSvc, LocationService.running, "läuft (" + LocationService.fixes + " Fixes)", "gestoppt", null);
        if (!LocationService.running) stSvc.setTextColor(MUT);
        diag.setText(Diag.tail(this, 40));
    }

    @Override
    protected void onResume() {
        super.onResume();
        h.post(tick);
    }

    @Override
    protected void onPause() {
        h.removeCallbacks(tick);
        super.onPause();
    }
}
