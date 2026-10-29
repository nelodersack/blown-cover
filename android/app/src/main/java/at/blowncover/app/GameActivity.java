package at.blowncover.app;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.location.Location;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.view.WindowManager;
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

import java.util.Locale;

/** Zeigt die Website in einem eingebetteten Browser und reicht Standort und Meldungen durch. */
public class GameActivity extends Activity {
    private WebView web;
    private final Handler h = new Handler(Looper.getMainLooper());
    private long probeSent, probeGot;

    private final Runnable alive = new Runnable() {
        @Override
        public void run() {
            probe();
            h.postDelayed(this, 30000);
        }
    };

    private final LocationService.Sink mySink = new LocationService.Sink() {
        @Override
        public void onLoc(Location l) {
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
        web = new WebView(this);
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setGeolocationEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setUserAgentString(s.getUserAgentString() + " BlownCoverApp/1");
        WebView.setWebContentsDebuggingEnabled(true);

        web.addJavascriptInterface(new Bridge(), "BlownNative");

        web.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView v, String url, Bitmap icon) {
                Diag.log(GameActivity.this, "Seite lädt: " + url);
            }

            @Override
            public void onPageFinished(WebView v, String url) {
                Diag.log(GameActivity.this, "Seite fertig");
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
        String url = Prefs.url(this);
        Diag.log(this, "Spiel öffnen: " + url);
        web.loadUrl(url);
        h.postDelayed(alive, 30000);
    }

    /** Fragt die Seite alle 30 s, ob sie noch lebt – so sieht man, ob sie bei Display-aus weiterläuft. */
    private void probe() {
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
                Diag.log(GameActivity.this, "Seite: " + v);
            }
        });
    }

    @Override
    protected void onStart() {
        super.onStart();
        Diag.log(this, "Spielansicht sichtbar");
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
        web.resumeTimers();
    }

    @Override
    protected void onStop() {
        // Bewusst KEIN web.onPause()/pauseTimers(): die Seite soll im Hintergrund weiterlaufen.
        Diag.log(this, "Spielansicht nicht mehr sichtbar (Display aus oder andere App)");
        web.resumeTimers();
        super.onStop();
    }

    @Override
    public void onBackPressed() {
        moveTaskToBack(true);
    }

    @Override
    protected void onDestroy() {
        h.removeCallbacks(alive);
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
            return "{\"app\":1,\"ver\":\"" + Prefs.VER + "\"}";
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
