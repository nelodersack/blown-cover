package at.blowncover.app;

import android.app.Notification;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.ServiceInfo;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.BatteryManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.PowerManager;
import android.os.Process;
import android.os.SystemClock;

import java.util.Locale;

/**
 * Vordergrunddienst: liest das GPS weiter, auch bei ausgeschaltetem Display,
 * und hält die CPU wach. Die Fixes gehen über {@link #sink} in die Website.
 */
public class LocationService extends Service implements LocationListener {
    /** Nur den Dienst beenden (Startbildschirm, Website). */
    static final String ACT_STOP = "at.blowncover.app.STOP";
    /** Alles beenden: Spielansicht schließen, Dienst stoppen, App-Prozess beenden (Benachrichtigung). */
    static final String ACT_QUIT = "at.blowncover.app.QUIT";
    /** Wie lange der Dienst nach dem Wegwischen während eines laufenden Spiels auf die Rückkehr wartet. */
    private static final long ORPHAN_MS = 5L * 60 * 1000;

    interface Sink {
        void onLoc(Location l);

        void onState(int code, String msg);
    }

    static volatile Sink sink;
    static volatile Location last;
    static volatile long lastAt;
    static volatile boolean running;
    static volatile int fixes;
    /** Die Spielansicht meldet gerade die Lobby ab (App wartet damit mit dem Beenden, höchstens 9 s). */
    static volatile boolean leavingLobby;
    /** Spielstatus laut Website (G.status), von der Spielansicht regelmäßig abgefragt. */
    static volatile String game;

    private LocationManager lm;
    private PowerManager.WakeLock wl;
    private BroadcastReceiver rcv;
    private final Handler h = new Handler(Looper.getMainLooper());
    private long lastLog;
    /** Letzter echter GPS-Fix (elapsedRealtime) – Netzwerk-Fixes zählen nur, wenn das GPS so lange schweigt. */
    private long lastGpsAt;
    private static final long NET_AFTER_MS = 5000;
    private boolean usingNet;
    private boolean killOnDestroy;
    private boolean orphaned;
    private long quitDeadline;

    /** Beenden, sobald das Verlassen der Lobby durch ist (oder spätestens nach 9 s). */
    private final Runnable doQuit = new Runnable() {
        @Override
        public void run() {
            if (leavingLobby && SystemClock.elapsedRealtime() < quitDeadline) {
                h.postDelayed(this, 250);
                return;
            }
            quit();
        }
    };

    private void quitSoon() {
        quitDeadline = SystemClock.elapsedRealtime() + 9000;
        h.removeCallbacks(doQuit);
        // Kurz warten, damit die Spielansicht ihr onDestroy (Lobby verlassen) noch ausführen kann.
        h.postDelayed(doQuit, 300);
        Notif.updateService(this, "Wird beendet …");
    }

    /** Nach dem Wegwischen im laufenden Spiel: Ist die Spielansicht nicht zurück, alles beenden. */
    private final Runnable orphanEnd = new Runnable() {
        @Override
        public void run() {
            if (GameActivity.alive) return;
            Diag.log(LocationService.this, "Nicht ins Spiel zurückgekehrt – App beendet");
            quit();
        }
    };

    private final Runnable beat = new Runnable() {
        @Override
        public void run() {
            heartbeat();
            h.postDelayed(this, 30000);
        }
    };

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        Notif.channels(this);
    }

    @Override
    public int onStartCommand(Intent in, int flags, int startId) {
        if (in != null && ACT_QUIT.equals(in.getAction())) {
            Diag.log(this, "Beenden (Benachrichtigung)");
            GameActivity.closeAll();
            quitSoon();
            return START_NOT_STICKY;
        }
        if (in != null && ACT_STOP.equals(in.getAction())) {
            Diag.log(this, "Dienst: beendet (Knopf)");
            stopSelf();
            return START_NOT_STICKY;
        }
        if (!running) begin();
        if (orphaned) {
            orphaned = false;
            h.removeCallbacks(orphanEnd);
            Diag.log(this, "Zurück im Spiel");
            Notif.updateService(this, "Standort wird übermittelt");
        }
        // Kein automatischer Neustart durch Android: Ohne Spielansicht hätte der Dienst keinen Zweck.
        return START_NOT_STICKY;
    }

    /** Alles beenden: Standort, Wake Lock, Benachrichtigungen und den App-Prozess. */
    private void quit() {
        killOnDestroy = true;
        try {
            Notif.clearAll(this);
        } catch (Exception ignored) {
        }
        stopForeground(STOP_FOREGROUND_REMOVE);
        stopSelf();
    }

    private void begin() {
        running = true;
        fixes = 0;
        try {
            Notification n = Notif.service(this, "Standort wird übermittelt");
            if (Build.VERSION.SDK_INT >= 29) {
                startForeground(Notif.ID_SVC, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION);
            } else {
                startForeground(Notif.ID_SVC, n);
            }
        } catch (Exception e) {
            Diag.log(this, "startForeground FEHLER: " + e);
            running = false;
            stopSelf();
            return;
        }
        PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
        try {
            wl = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "BlownCover:loc");
            wl.acquire(6L * 60 * 60 * 1000);
        } catch (Exception e) {
            Diag.log(this, "WakeLock FEHLER: " + e);
        }
        lm = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
        try {
            lm.requestLocationUpdates(LocationManager.GPS_PROVIDER, 2000L, 0f, this, Looper.getMainLooper());
            // Ersatz: Ortung über WLAN/Mobilfunk (ungenauer, reißt aber in Durchgängen/Gebäuden nicht ab).
            try {
                if (lm.getAllProviders().contains(LocationManager.NETWORK_PROVIDER)) {
                    lm.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 2000L, 0f, this, Looper.getMainLooper());
                    Diag.log(this, "Netzwerk-Ortung als Ersatz bereit");
                }
            } catch (Exception e) {
                Diag.log(this, "Netzwerk-Ortung nicht verfügbar: " + e.getMessage());
            }
        } catch (SecurityException e) {
            Diag.log(this, "GPS: keine Berechtigung");
            Sink s = sink;
            if (s != null) s.onState(1, "Standort nicht erlaubt");
        } catch (Exception e) {
            Diag.log(this, "GPS FEHLER: " + e);
        }
        rcv = new BroadcastReceiver() {
            @Override
            public void onReceive(Context c, Intent i) {
                String a = i.getAction();
                if (a == null) return;
                if (Intent.ACTION_SCREEN_OFF.equals(a)) Diag.log(c, "Display AUS");
                else if (Intent.ACTION_SCREEN_ON.equals(a)) Diag.log(c, "Display AN");
                else if (PowerManager.ACTION_POWER_SAVE_MODE_CHANGED.equals(a)) {
                    PowerManager p = (PowerManager) c.getSystemService(Context.POWER_SERVICE);
                    Diag.log(c, "Energiesparmodus: " + (p.isPowerSaveMode() ? "AN" : "aus"));
                } else if (PowerManager.ACTION_DEVICE_IDLE_MODE_CHANGED.equals(a)) {
                    PowerManager p = (PowerManager) c.getSystemService(Context.POWER_SERVICE);
                    Diag.log(c, "Doze: " + (p.isDeviceIdleMode() ? "AN" : "aus"));
                }
            }
        };
        IntentFilter f = new IntentFilter();
        f.addAction(Intent.ACTION_SCREEN_ON);
        f.addAction(Intent.ACTION_SCREEN_OFF);
        f.addAction(PowerManager.ACTION_POWER_SAVE_MODE_CHANGED);
        f.addAction(PowerManager.ACTION_DEVICE_IDLE_MODE_CHANGED);
        try {
            if (Build.VERSION.SDK_INT >= 33) registerReceiver(rcv, f, Context.RECEIVER_NOT_EXPORTED);
            else registerReceiver(rcv, f);
        } catch (Exception e) {
            Diag.log(this, "Receiver FEHLER: " + e);
        }
        h.postDelayed(beat, 30000);
        Diag.log(this, "Dienst: gestartet (Android " + Build.VERSION.SDK_INT + ", " + Build.MANUFACTURER + " " + Build.MODEL + ")");
    }

    private void heartbeat() {
        try {
            PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
            Intent b = registerReceiver(null, new IntentFilter(Intent.ACTION_BATTERY_CHANGED));
            int pct = -1;
            if (b != null) {
                int lv = b.getIntExtra(BatteryManager.EXTRA_LEVEL, -1);
                int sc = b.getIntExtra(BatteryManager.EXTRA_SCALE, 100);
                if (lv >= 0 && sc > 0) pct = lv * 100 / sc;
            }
            long age = lastAt == 0 ? -1 : (SystemClock.elapsedRealtime() - lastAt) / 1000;
            Diag.log(this, String.format(Locale.GERMANY,
                    "♥ Fixes=%d letzter Fix vor %s s · Display %s · Akku %d%% · Doze %s · Sparmodus %s · Akku-Ausnahme %s",
                    fixes, age < 0 ? "–" : String.valueOf(age),
                    pm.isInteractive() ? "an" : "AUS", pct,
                    pm.isDeviceIdleMode() ? "JA" : "nein",
                    pm.isPowerSaveMode() ? "JA" : "nein",
                    pm.isIgnoringBatteryOptimizations(getPackageName()) ? "ja" : "NEIN"));
            if (orphan()) return;
            if (age >= 20) Notif.updateService(this, "Warte auf GPS (letzter Fix vor " + age + " s)");
            else if (age >= 0) Notif.updateService(this, "Standort wird übermittelt");
        } catch (Exception ignored) {
        }
    }

    @Override
    public void onLocationChanged(Location l) {
        long el = SystemClock.elapsedRealtime();
        boolean gps = LocationManager.GPS_PROVIDER.equals(l.getProvider());
        if (gps) {
            lastGpsAt = el;
            if (usingNet) {
                usingNet = false;
                Diag.log(this, "GPS wieder da – Netzwerk-Ortung pausiert");
            }
        } else {
            // Netzwerk-Fix nur, wenn das GPS gerade schweigt, und nur frische Werte (keine zwischengespeicherten).
            if (el - lastGpsAt < NET_AFTER_MS) return;
            long ageMs = (SystemClock.elapsedRealtimeNanos() - l.getElapsedRealtimeNanos()) / 1000000L;
            if (ageMs > 15000) return;
            if (!usingNet) {
                usingNet = true;
                Diag.log(this, String.format(Locale.US, "Kein GPS seit %d s – Netzwerk-Ortung springt ein (±%.0f m)",
                        lastGpsAt == 0 ? -1 : (el - lastGpsAt) / 1000, l.getAccuracy()));
            }
        }
        last = l;
        lastAt = el;
        fixes++;
        long now = System.currentTimeMillis();
        if (now - lastLog >= 10000) {
            lastLog = now;
            Diag.log(this, String.format(Locale.US, "Fix #%d %.5f, %.5f (±%.0f m)%s", fixes, l.getLatitude(), l.getLongitude(), l.getAccuracy(), gps ? "" : " Netz"));
        }
        Sink s = sink;
        if (s != null) {
            try {
                s.onLoc(l);
            } catch (Exception ignored) {
            }
        }
    }

    @Override
    public void onProviderEnabled(String provider) {
        if (!LocationManager.GPS_PROVIDER.equals(provider)) return;
        Diag.log(this, "GPS an");
        Sink s = sink;
        if (s != null) s.onState(0, "GPS an");
    }

    @Override
    public void onProviderDisabled(String provider) {
        if (!LocationManager.GPS_PROVIDER.equals(provider)) return;
        Diag.log(this, "GPS AUS");
        Sink s = sink;
        if (s != null) s.onState(2, "GPS aus");
    }

    @Override
    public void onStatusChanged(String provider, int status, Bundle extras) {
    }

    /** true, solange die App weggewischt ist, aber ein Spiel läuft (Dienst wartet auf Rückkehr). */
    private boolean orphan() {
        return orphaned && !GameActivity.alive;
    }

    @Override
    public void onTaskRemoved(Intent rootIntent) {
        if ("running".equals(game)) {
            Diag.log(this, "App weggewischt – Spiel läuft, Dienst wartet bis zu 5 min auf Rückkehr");
            Notif.updateService(this, "Spiel läuft noch – tippe hier, um zurückzukehren");
            Notif.event(this, "Du bist noch im Spiel",
                    "Die App wurde geschlossen, dein Standort geht gerade nicht ans Spiel. Tippe hier, um zurückzukehren. "
                            + "Ohne Rückkehr beendet sich die App in 5 Minuten.");
            orphaned = true;
            h.removeCallbacks(orphanEnd);
            h.postDelayed(orphanEnd, ORPHAN_MS);
        } else {
            Diag.log(this, "App weggewischt – kein laufendes Spiel (" + game + "), alles beendet");
            quitSoon();
        }
        super.onTaskRemoved(rootIntent);
    }

    @Override
    public void onDestroy() {
        h.removeCallbacks(beat);
        h.removeCallbacks(orphanEnd);
        h.removeCallbacks(doQuit);
        try {
            if (lm != null) lm.removeUpdates(this);
        } catch (Exception ignored) {
        }
        try {
            if (rcv != null) unregisterReceiver(rcv);
        } catch (Exception ignored) {
        }
        try {
            if (wl != null && wl.isHeld()) wl.release();
        } catch (Exception ignored) {
        }
        running = false;
        last = null;
        Diag.log(this, "Dienst: gestoppt" + (killOnDestroy ? ", App beendet" : ""));
        super.onDestroy();
        // Beim Beenden auch den Prozess schließen: kein eingebetteter Browser, kein Standortzugriff bleibt übrig.
        if (killOnDestroy) Process.killProcess(Process.myPid());
    }
}
