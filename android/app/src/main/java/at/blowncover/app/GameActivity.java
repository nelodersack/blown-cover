package at.blowncover.app;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.location.Location;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.view.Display;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.FrameLayout;
import android.webkit.ConsoleMessage;
import android.webkit.GeolocationPermissions;
import android.webkit.JavascriptInterface;
import android.webkit.RenderProcessGoneDetail;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import org.json.JSONObject;
import org.json.JSONTokener;

import java.lang.ref.WeakReference;
import java.util.Locale;

/** Zeigt die Website in einem eingebetteten Browser und reicht Standort und Meldungen durch. */
public class GameActivity extends Activity {
    /** true, solange eine Spielansicht existiert (für den Dienst). */
    static volatile boolean alive;
    private static WeakReference<GameActivity> current = new WeakReference<>(null);

    /** Schließt die Spielansicht samt Aufgabe (für „Beenden“ in der Benachrichtigung). */
    static void closeAll() {
        final GameActivity a = current.get();
        if (a == null) return;
        a.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                a.finishAndRemoveTask();
            }
        });
    }

    private WebView web;
    private long loadStart;
    private String loadedUrl;
    private FrameLayout frame;
    private ReadyDialog ready;
    /** Hat der Spieler in dieser Sitzung schon auf „Spielen“ getippt (bzw. war alles bereit)? */
    private boolean playing;
    static final String EXTRA_READY = "showReady";
    private final Handler h = new Handler(Looper.getMainLooper());
    private long probeSent, probeGot;

    private final Runnable probeLoop = new Runnable() {
        @Override
        public void run() {
            probe();
            h.postDelayed(this, 30000);
        }
    };

    private final LocationService.Sink mySink = new LocationService.Sink() {
        @Override
        public void onLoc(Location l) {
            // Immer durchreichen: Die Seite schaltet ihre Anbindung erst später ein (beim Betreten der Lobby),
            // der Ausdruck prüft selbst, ob window.bcNativePos schon existiert.
            if (web == null) return;
            String js = String.format(Locale.US,
                    "window.bcNativePos&&window.bcNativePos(%.7f,%.7f,%.1f,%d)",
                    l.getLatitude(), l.getLongitude(), l.getAccuracy(), l.getTime());
            web.evaluateJavascript(js, null);
        }

        @Override
        public void onState(int code, String msg) {
            if (web == null) return;
            web.evaluateJavascript("window.bcNativeErr&&window.bcNativeErr(" + code + "," + JSONObject.quote(msg) + ")", null);
        }
    };

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        alive = true;
        current = new WeakReference<>(this);
        maxRefreshRate();
        web = new AwakeWebView(this);
        frame = new FrameLayout(this);
        frame.setBackgroundColor(Ui.BG);
        frame.addView(web, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        setContentView(frame);
        logWebViewVersion();

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setGeolocationEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setUserAgentString(s.getUserAgentString() + " BlownCoverApp/1");
        // Flüssigere Darstellung: Inhalt auch außerhalb des sichtbaren Bereichs vorzeichnen.
        s.setOffscreenPreRaster(true);
        // Darstellungsprozess der Seite auch im Hintergrund als wichtig markieren (wird seltener beendet).
        web.setRendererPriorityPolicy(WebView.RENDERER_PRIORITY_IMPORTANT, false);
        WebView.setWebContentsDebuggingEnabled(true);

        web.addJavascriptInterface(new Bridge(), "BlownNative");

        web.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView v, String url, Bitmap icon) {
                loadStart = SystemClock.elapsedRealtime();
                Diag.log(GameActivity.this, "Seite lädt: " + url);
            }

            @Override
            public void onPageFinished(WebView v, String url) {
                // Ohne vorheriges „Seite lädt“ meldet WebView beim Neuladen noch die alte Seite: dann nichts messen.
                if (loadStart == 0) return;
                long ms = SystemClock.elapsedRealtime() - loadStart;
                loadStart = 0;
                Diag.log(GameActivity.this, String.format(Locale.GERMANY, "Seite fertig nach %.1f s", ms / 1000.0));
                checkPage();
            }

            @Override
            public void onReceivedError(WebView v, WebResourceRequest r, WebResourceError e) {
                if (r.isForMainFrame()) {
                    Diag.log(GameActivity.this, "Seitenfehler: " + e.getErrorCode() + " " + e.getDescription());
                }
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
                Uri u = r.getUrl();
                String own = Uri.parse(Prefs.url(GameActivity.this)).getHost();
                if (u.getHost() != null && own != null && !u.getHost().equals(own)
                        && ("http".equals(u.getScheme()) || "https".equals(u.getScheme()))) {
                    try {
                        startActivity(new Intent(Intent.ACTION_VIEW, u));
                    } catch (Exception ignored) {
                    }
                    return true;
                }
                return false;
            }

            @Override
            public boolean onRenderProcessGone(WebView v, RenderProcessGoneDetail d) {
                Diag.log(GameActivity.this, "WebView-Prozess beendet (abgestürzt=" + d.didCrash() + ") – starte Seite neu");
                h.post(new Runnable() {
                    @Override
                    public void run() {
                        recreate();
                    }
                });
                return true;
            }
        });

        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onGeolocationPermissionsShowPrompt(String origin, GeolocationPermissions.Callback cb) {
                cb.invoke(origin, true, false);
            }

            @Override
            public boolean onConsoleMessage(ConsoleMessage m) {
                if (m.messageLevel() == ConsoleMessage.MessageLevel.ERROR) {
                    String t = m.message();
                    if (t != null && t.length() > 160) t = t.substring(0, 160);
                    Diag.log(GameActivity.this, "JS-Fehler: " + t);
                }
                return true;
            }
        });

        LocationService.sink = mySink;
        loadedUrl = Prefs.url(this);
        Diag.log(this, "App v" + Prefs.ver(this) + " · Spiel öffnen: " + loadedUrl);
        web.loadUrl(loadedUrl);
        h.postDelayed(probeLoop, 30000);

        // Start direkt ins Spiel; nur wenn etwas fehlt, vorher „Bereit machen“.
        if (Checks.all(this) && !getIntent().getBooleanExtra(EXTRA_READY, false)) startPlaying();
        else showReady();
    }

    private void showReady() {
        if (ready == null) {
            ready = new ReadyDialog(this, new ReadyDialog.Listener() {
                @Override
                public void onPlay() {
                    startPlaying();
                }
            });
        }
        ready.refresh();
        if (ready.root.getParent() == null) {
            frame.addView(ready.root, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
            String m = Checks.missing(this);
            Diag.log(this, "Bereit machen: fehlt " + (m.isEmpty() ? "nichts" : m));
        }
    }

    private void hideReady() {
        if (ready != null && ready.root.getParent() != null) frame.removeView(ready.root);
    }

    /** Pflichtpunkte erfüllt: Dialog schließen, Hintergrunddienst starten. */
    private void startPlaying() {
        hideReady();
        if (!playing) {
            String m = Checks.missing(this);
            Diag.log(this, "Spielen" + (m.isEmpty() ? " (alles bereit)" : " (fehlt noch: " + m + ")"));
        }
        playing = true;
        ensureService();
    }

    @Override
    protected void onNewIntent(Intent i) {
        super.onNewIntent(i);
        setIntent(i);
        if (i.getBooleanExtra(EXTRA_READY, false)) showReady();
    }

    @Override
    public void onRequestPermissionsResult(int code, String[] perms, int[] res) {
        super.onRequestPermissionsResult(code, perms, res);
        afterChecksChanged();
    }

    /** Nach Rückkehr aus Einstellungen/Berechtigungsdialog: Dialog auffrischen, bei „alles grün“ direkt los. */
    private void afterChecksChanged() {
        if (ready == null || !ready.showing()) {
            // Pflicht verloren (z. B. GPS ausgeschaltet)? Dann Dialog wieder zeigen.
            if (!Checks.required(this)) {
                playing = false;
                showReady();
            }
            return;
        }
        ready.refresh();
        if (Checks.all(this)) startPlaying();
    }

    /** Nach dem Laden: Ladezeiten der Seite (Netz, Aufbau) ins Protokoll. */
    private void checkPage() {
        if (web == null) return;
        String js = "(function(){try{var n=performance.getEntriesByType('navigation')[0]||{};var r=performance.getEntriesByType('resource');"
                + "var c=0;for(var i=0;i<r.length;i++){if(r[i].transferSize===0&&r[i].decodedBodySize>0)c++}"
                + "return JSON.stringify({antwort:Math.round(n.responseStart||0),"
                + "aufgebaut:Math.round(n.domContentLoadedEventEnd||0),geladen:Math.round(n.loadEventEnd||0),dateien:r.length,ausCache:c})}"
                + "catch(e){return 'err '+e}})()";
        web.evaluateJavascript(js, new android.webkit.ValueCallback<String>() {
            @Override
            public void onReceiveValue(String v) {
                try {
                    Object o = new JSONTokener(v).nextValue();
                    JSONObject j = new JSONObject(String.valueOf(o));
                    Diag.log(GameActivity.this, "Seitenzeiten (ms): " + j);
                } catch (Exception e) {
                    Diag.log(GameActivity.this, "Seitenzeiten: " + v);
                }
            }
        });
    }

    /** Höchste Bildwiederholrate bei gleicher Auflösung anfordern (z. B. 120 Hz statt 60 Hz bei Samsung). */
    private void maxRefreshRate() {
        try {
            Display d = getWindowManager().getDefaultDisplay();
            Display.Mode cur = d.getMode(), best = cur;
            for (Display.Mode m : d.getSupportedModes()) {
                if (m.getPhysicalWidth() == cur.getPhysicalWidth() && m.getPhysicalHeight() == cur.getPhysicalHeight()
                        && m.getRefreshRate() > best.getRefreshRate()) best = m;
            }
            WindowManager.LayoutParams lp = getWindow().getAttributes();
            lp.preferredDisplayModeId = best.getModeId();
            getWindow().setAttributes(lp);
            Diag.log(this, String.format(Locale.GERMANY, "Bildrate: angefordert %.0f Hz (vorher %.0f Hz, %dx%d)",
                    best.getRefreshRate(), cur.getRefreshRate(), cur.getPhysicalWidth(), cur.getPhysicalHeight()));
        } catch (Exception e) {
            Diag.log(this, "Bildrate FEHLER: " + e);
        }
    }

    private void logWebViewVersion() {
        try {
            PackageInfo p = WebView.getCurrentWebViewPackage();
            if (p != null) Diag.log(this, "WebView: " + p.packageName + " " + p.versionName);
        } catch (Exception ignored) {
        }
    }

    /** Dienst sicherstellen (z. B. bei Rückkehr über die Benachrichtigung). */
    private void ensureService() {
        boolean loc = checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                || checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED;
        if (!loc) return;
        try {
            startForegroundService(new Intent(this, LocationService.class));
        } catch (Exception e) {
            Diag.log(this, "Dienststart FEHLER: " + e);
        }
    }

    /** Fragt die Seite alle 30 s, ob sie noch lebt – so sieht man, ob sie bei Display-aus weiterläuft. */
    private void probe() {
        probe(false);
    }

    private void probe(final boolean quiet) {
        if (web == null) return;
        if (probeSent > probeGot) Diag.log(this, "Seite antwortet NICHT (letzte Abfrage unbeantwortet)");
        probeSent = SystemClock.elapsedRealtime();
        final long mine = probeSent;
        String js = "(function(){try{return JSON.stringify({hidden:document.hidden,status:(typeof G!=='undefined'&&G)?G.status:null,"
                + "pos:(typeof pos!=='undefined'&&pos)?1:0,fixAge:(typeof lastFix!=='undefined'&&lastFix)?Math.round((Date.now()-lastFix)/1000):null})}"
                + "catch(e){return 'err '+e}})()";
        web.evaluateJavascript(js, new android.webkit.ValueCallback<String>() {
            @Override
            public void onReceiveValue(String v) {
                probeGot = mine;
                if (!quiet) Diag.log(GameActivity.this, "Seite: " + v);
                try {
                    Object o = new JSONTokener(v).nextValue();
                    JSONObject j = new JSONObject(String.valueOf(o));
                    LocationService.game = j.isNull("status") ? null : j.optString("status");
                } catch (Exception ignored) {
                }
            }
        });
    }

    @Override
    protected void onStart() {
        super.onStart();
        Diag.log(this, "Spielansicht sichtbar");
        setPageHidden(false);
        Notif.clearHistory();
    }

    /** Teilt der Seite mit, ob die Spielansicht verdeckt ist (die WebView selbst bleibt für den Browser „sichtbar“). */
    private void setPageHidden(boolean hidden) {
        if (web == null) return;
        web.evaluateJavascript("window.bcSetHidden?window.bcSetHidden(" + hidden + "):(window.bcHidden=" + hidden + ")", null);
    }

    /**
     * WebView, die dem Browser immer „Fenster sichtbar“ meldet. Sonst friert Chromium die Seite ein,
     * sobald Display aus / App im Hintergrund ist (Zeitgeber, Spielschleife und Meldungen stehen dann still).
     */
    static class AwakeWebView extends WebView {
        AwakeWebView(Context c) {
            super(c);
        }

        @Override
        protected void onWindowVisibilityChanged(int visibility) {
            super.onWindowVisibilityChanged(View.VISIBLE);
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
        web.resumeTimers();
        afterChecksChanged();
        // Seitenwahl im Diagnose-Bildschirm geändert? Dann die neue Seite laden.
        String u = Prefs.url(this);
        if (loadedUrl != null && !u.equals(loadedUrl)) {
            loadedUrl = u;
            Diag.log(this, "Seite gewechselt: " + u);
            web.loadUrl(u);
        }
    }

    @Override
    protected void onStop() {
        // Bewusst KEIN web.onPause()/pauseTimers(): die Seite soll im Hintergrund weiterlaufen.
        Diag.log(this, "Spielansicht nicht mehr sichtbar (Display aus oder andere App)");
        web.resumeTimers();
        setPageHidden(true);
        // Spielstatus sofort auffrischen: entscheidet, was beim Wegwischen passiert.
        probe(true);
        super.onStop();
    }

    @Override
    public void onBackPressed() {
        moveTaskToBack(true);
    }

    @Override
    protected void onDestroy() {
        alive = false;
        if (current.get() == this) current = new WeakReference<>(null);
        h.removeCallbacks(probeLoop);
        if (LocationService.sink == mySink) LocationService.sink = null;
        if (web != null) {
            web.destroy();
            web = null;
        }
        Diag.log(this, "Spielansicht beendet");
        super.onDestroy();
    }

    /** Schnittstelle für die Website: window.BlownNative */
    private class Bridge {
        @JavascriptInterface
        public String info() {
            return "{\"app\":1,\"ver\":\"" + Prefs.ver(GameActivity.this) + "\"}";
        }

        @JavascriptInterface
        public void notify(String title, String text) {
            Notif.event(GameActivity.this, title == null ? "Blown Cover" : title, text == null ? "" : text);
        }

        @JavascriptInterface
        public String lastPos() {
            Location l = LocationService.last;
            if (l == null) return "";
            return String.format(Locale.US, "{\"lat\":%.7f,\"lng\":%.7f,\"acc\":%.1f,\"t\":%d}",
                    l.getLatitude(), l.getLongitude(), l.getAccuracy(), l.getTime());
        }

        @JavascriptInterface
        public void keepAwake(final boolean on) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    if (on) getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
                    else getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
                }
            });
        }

        @JavascriptInterface
        public void log(String s) {
            Diag.log(GameActivity.this, "Web: " + s);
        }

        @JavascriptInterface
        public void stopTracking() {
            startService(new Intent(GameActivity.this, LocationService.class).setAction(LocationService.ACT_STOP));
        }
    }
}
