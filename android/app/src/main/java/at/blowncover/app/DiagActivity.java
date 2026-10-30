package at.blowncover.app;

import android.app.Activity;
import android.content.ClipData;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.util.Locale;

/** Diagnose (erreichbar über langes Drücken aufs App-Icon): Status, Protokoll, Log teilen, Seitenwahl für Tests. */
public class DiagActivity extends Activity {
    private final Handler h = new Handler(Looper.getMainLooper());
    private Ui.Item svc, rdy;
    private TextView log;
    private ScrollView logScroll;
    private final Runnable tick = new Runnable() {
        @Override
        public void run() {
            refresh();
            h.postDelayed(this, 2000);
        }
    };

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Ui.BG);
        int p = Ui.dp(this, 16);
        root.setPadding(p, Ui.dp(this, 22), p, p);
        setContentView(root);

        root.addView(Ui.screenTitle(this, "Diagnose"));
        root.addView(Ui.text(this, "App v" + Prefs.ver(this) + " · " + Build.MANUFACTURER + " " + Build.MODEL
                + " · Android " + Build.VERSION.RELEASE, 13, Ui.MUT, null), Ui.lp(this, 6));
        ((TextView) root.getChildAt(1)).setTypeface(Ui.body(this, "").getTypeface());

        svc = new Ui.Item(this, "Dienst", "", null, null);
        rdy = new Ui.Item(this, "Standort · GPS · Benachrichtigungen · Akku", "", "Beheben", new View.OnClickListener() {
            public void onClick(View v) {
                startActivity(new Intent(DiagActivity.this, GameActivity.class).putExtra(GameActivity.EXTRA_READY, true));
                finish();
            }
        });
        rdy.title.setSingleLine(false);
        root.addView(svc.row, Ui.lp(this, 12));
        root.addView(rdy.row, Ui.lp(this, 6));

        root.addView(Ui.label(this, "Protokoll"), Ui.lp(this, 14));
        logScroll = new ScrollView(this);
        logScroll.setBackground(Ui.box(this, Ui.PANEL, Ui.LINE, 12));
        int lp = Ui.dp(this, 10);
        logScroll.setPadding(lp, lp, lp, lp);
        log = Ui.mono(this, "");
        log.setTextIsSelectable(true);
        logScroll.addView(log);
        LinearLayout.LayoutParams ll = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f);
        ll.topMargin = Ui.dp(this, 8);
        root.addView(logScroll, ll);

        root.addView(Ui.button(this, "Log teilen (Datei)", true, false, new View.OnClickListener() {
            public void onClick(View v) {
                share();
            }
        }), Ui.lp(this, 12));

        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        Button stop = Ui.button(this, "Dienst beenden", false, false, new View.OnClickListener() {
            public void onClick(View v) {
                startService(new Intent(DiagActivity.this, LocationService.class).setAction(LocationService.ACT_STOP));
                h.postDelayed(new Runnable() {
                    public void run() {
                        refresh();
                    }
                }, 400);
            }
        });
        Button back = Ui.button(this, "Zurück zum Spiel", false, false, new View.OnClickListener() {
            public void onClick(View v) {
                startActivity(new Intent(DiagActivity.this, GameActivity.class));
                finish();
            }
        });
        LinearLayout.LayoutParams half = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
        half.rightMargin = Ui.dp(this, 8);
        row.addView(stop, half);
        row.addView(back, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
        root.addView(row, Ui.lp(this, 8));

    }

    private void share() {
        try {
            Uri u = LogProvider.snapshot(this);
            Intent i = new Intent(Intent.ACTION_SEND);
            i.setType("text/plain");
            i.putExtra(Intent.EXTRA_STREAM, u);
            i.putExtra(Intent.EXTRA_SUBJECT, "Blown Cover Diagnose");
            i.setClipData(ClipData.newRawUri("Blown Cover Log", u));
            i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            Intent ch = Intent.createChooser(i, "Log teilen");
            ch.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            startActivity(ch);
        } catch (Exception e) {
            Diag.log(this, "Log teilen FEHLER: " + e);
            Toast.makeText(this, "Log konnte nicht geteilt werden", Toast.LENGTH_LONG).show();
        }
    }

    private void refresh() {
        boolean run = LocationService.running;
        long age = LocationService.lastAt == 0 ? -1 : (SystemClock.elapsedRealtime() - LocationService.lastAt) / 1000;
        svc.title.setText(run ? "Dienst läuft" : "Dienst gestoppt");
        svc.set(this, run ? Ui.ST_OK : Ui.ST_WARN, run
                ? String.format(Locale.GERMANY, "%d Fixes · letzter vor %s s", LocationService.fixes, age < 0 ? "–" : String.valueOf(age))
                : "startet mit dem Spiel");
        String m = Checks.missing(this);
        rdy.set(this, m.isEmpty() ? Ui.ST_OK : Checks.required(this) ? Ui.ST_WARN : Ui.ST_NO, m.isEmpty() ? "alles bereit" : "fehlt: " + m);

        boolean atBottom = !logScroll.canScrollVertically(1);
        log.setText(Diag.tail(this, 200));
        if (atBottom) logScroll.post(new Runnable() {
            public void run() {
                logScroll.fullScroll(View.FOCUS_DOWN);
            }
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        h.post(tick);
        logScroll.post(new Runnable() {
            public void run() {
                logScroll.fullScroll(View.FOCUS_DOWN);
            }
        });
    }

    @Override
    protected void onPause() {
        h.removeCallbacks(tick);
        super.onPause();
    }
}
