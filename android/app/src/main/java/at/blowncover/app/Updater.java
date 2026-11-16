package at.blowncover.app;

import android.app.Activity;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.net.Uri;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.widget.Toast;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * App-Update ohne externen Browser (seit v0.3.4): BlownNative.update(url) lädt die APK aus den GitHub-Releases
 * in den App-Cache und öffnet den Android-Installer („Aktualisieren?“). Gleicher Signaturschlüssel → Daten bleiben.
 */
final class Updater {
    static final String FILE = "BlownCover-update.apk";
    private static final String CH = "upd";
    private static final int ID = 300;
    private static volatile boolean busy = false;
    /** Fertig geladene APK, die noch auf die Erlaubnis „Apps aus dieser Quelle installieren“ wartet. */
    private static File pending = null;

    private Updater() {}

    static File dir(Context c) {
        return new File(c.getCacheDir(), "update");
    }

    /** Nur Release-Adressen dieses Repos (Start) bzw. GitHubs Download-Server (nach Weiterleitung). */
    static boolean okStart(Uri u) {
        return u != null && "https".equals(u.getScheme()) && "github.com".equalsIgnoreCase(u.getHost())
                && u.getPath() != null && u.getPath().startsWith("/nelodersack/blown-cover/releases/")
                && !u.getPath().contains("..");
    }

    static boolean okHop(URL u) {
        if (u == null || !"https".equals(u.getProtocol())) return false;
        String h = u.getHost().toLowerCase(java.util.Locale.ROOT);
        return h.equals("github.com") || h.equals("objects.githubusercontent.com") || h.endsWith(".githubusercontent.com");
    }

    static void start(final Activity a, String url) {
        final Uri u = url == null ? null : Uri.parse(url);
        if (!okStart(u)) {
            Diag.log(a, "Update abgelehnt (fremde Adresse): " + url);
            return;
        }
        if (busy) {
            toast(a, "Update wird schon geladen …");
            return;
        }
        busy = true;
        Diag.log(a, "Update: Download startet " + url);
        toast(a, "Update wird geladen …");
        final Context app = a.getApplicationContext();
        new Thread(new Runnable() {
            @Override
            public void run() {
                File f = null;
                String err = null;
                try {
                    f = download(app, u.toString());
                    PackageInfo pi = app.getPackageManager().getPackageArchiveInfo(f.getAbsolutePath(), 0);
                    if (pi == null) throw new Exception("Datei ist keine gültige App");
                    if (!app.getPackageName().equals(pi.packageName)) throw new Exception("falsches Paket " + pi.packageName);
                    long have = app.getPackageManager().getPackageInfo(app.getPackageName(), 0).getLongVersionCode();
                    if (pi.getLongVersionCode() <= have) {
                        err = "Diese Version ist schon installiert (v" + pi.versionName + ")";
                    } else {
                        Diag.log(app, "Update: v" + pi.versionName + " geladen (" + f.length() / 1024 + " KB)");
                    }
                } catch (Exception e) {
                    err = "Update fehlgeschlagen: " + (e.getMessage() == null ? e.toString() : e.getMessage());
                }
                final File ff = f;
                final String ee = err;
                new Handler(Looper.getMainLooper()).post(new Runnable() {
                    @Override
                    public void run() {
                        busy = false;
                        progress(app, -1);
                        if (ee != null) {
                            Diag.log(app, ee);
                            toast(app, ee);
                            return;
                        }
                        install(a, ff);
                    }
                });
            }
        }).start();
    }

    private static File download(Context c, String url) throws Exception {
        File d = dir(c);
        if (!d.exists() && !d.mkdirs()) throw new Exception("Cache-Ordner nicht anlegbar");
        File tmp = new File(d, FILE + ".part"), out = new File(d, FILE);
        URL cur = new URL(url);
        HttpURLConnection con = null;
        boolean ok = false;
        // Weiterleitungen selbst verfolgen, damit jedes Ziel geprüft wird (github.com → *.githubusercontent.com).
        for (int hop = 0; hop < 6; hop++) {
            if (!okHop(cur)) throw new Exception("unerwartetes Download-Ziel " + cur.getHost());
            con = (HttpURLConnection) cur.openConnection();
            con.setInstanceFollowRedirects(false);
            con.setConnectTimeout(15000);
            con.setReadTimeout(30000);
            con.setRequestProperty("Accept", "application/octet-stream");
            int code = con.getResponseCode();
            if (code >= 300 && code < 400) {
                String loc = con.getHeaderField("Location");
                con.disconnect();
                if (loc == null) throw new Exception("Weiterleitung ohne Ziel");
                cur = new URL(cur, loc);
                continue;
            }
            if (code != 200) throw new Exception("Server antwortet " + code);
            ok = true;
            break;
        }
        if (!ok) throw new Exception("zu viele Weiterleitungen");
        long total = con.getContentLengthLong();
        InputStream in = con.getInputStream();
        FileOutputStream o = new FileOutputStream(tmp);
        byte[] buf = new byte[64 * 1024];
        long done = 0;
        int lastPct = -1;
        try {
            int n;
            while ((n = in.read(buf)) > 0) {
                o.write(buf, 0, n);
                done += n;
                if (total > 0) {
                    int pct = (int) (done * 100 / total);
                    if (pct / 5 != lastPct / 5) {
                        lastPct = pct;
                        progress(c, pct);
                    }
                }
            }
        } finally {
            o.close();
            in.close();
            con.disconnect();
        }
        if (total > 0 && done != total) throw new Exception("Download unvollständig (" + done + " von " + total + " Bytes)");
        if (done < 100 * 1024) throw new Exception("Download zu klein (" + done + " Bytes)");
        if (out.exists() && !out.delete()) throw new Exception("alte Datei nicht löschbar");
        if (!tmp.renameTo(out)) throw new Exception("Datei nicht speicherbar");
        return out;
    }

    /** Installer öffnen; fehlt die Erlaubnis, zuerst die Einstellungsseite (weiter in resume()). */
    static void install(Activity a, File f) {
        if (Build.VERSION.SDK_INT >= 26 && !a.getPackageManager().canRequestPackageInstalls()) {
            pending = f;
            Diag.log(a, "Update: Erlaubnis „Apps aus dieser Quelle installieren“ fehlt → Einstellungen");
            toast(a, "Bitte „Apps aus dieser Quelle installieren“ erlauben und zurückkehren");
            try {
                a.startActivity(new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                        Uri.parse("package:" + a.getPackageName())));
            } catch (Exception e) {
                Diag.log(a, "Update: Einstellungsseite nicht zu öffnen: " + e);
                toast(a, "Einstellung nicht zu öffnen – in den App-Infos erlauben");
            }
            return;
        }
        pending = null;
        try {
            Uri u = Uri.parse("content://" + LogProvider.AUTH + "/" + Uri.encode(f.getName()));
            Intent i = new Intent(Intent.ACTION_VIEW);
            i.setDataAndType(u, "application/vnd.android.package-archive");
            i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
            a.startActivity(i);
            Diag.log(a, "Update: Installer geöffnet");
        } catch (Exception e) {
            Diag.log(a, "Update: Installer nicht zu öffnen: " + e);
            toast(a, "Installer nicht zu öffnen: " + e.getMessage());
        }
    }

    /** Aus GameActivity.onResume: nach der Einstellungsseite weitermachen. */
    static void resume(Activity a) {
        File f = pending;
        if (f == null) return;
        if (Build.VERSION.SDK_INT >= 26 && !a.getPackageManager().canRequestPackageInstalls()) {
            pending = null;
            Diag.log(a, "Update: Erlaubnis nicht erteilt");
            toast(a, "Update abgebrochen: Installieren nicht erlaubt");
            return;
        }
        if (f.exists()) install(a, f);
        else pending = null;
    }

    private static void progress(Context c, int pct) {
        try {
            NotificationManager nm = c.getSystemService(NotificationManager.class);
            if (pct < 0) {
                nm.cancel(ID);
                return;
            }
            nm.createNotificationChannel(new NotificationChannel(CH, "App-Update", NotificationManager.IMPORTANCE_LOW));
            android.app.Notification n = new android.app.Notification.Builder(c, CH)
                    .setSmallIcon(android.R.drawable.stat_sys_download)
                    .setContentTitle("Blown Cover wird aktualisiert")
                    .setContentText(pct + " %")
                    .setProgress(100, pct, false)
                    .setOngoing(true)
                    .setOnlyAlertOnce(true)
                    .build();
            nm.notify(ID, n);
        } catch (Exception ignored) {
            // ohne Benachrichtigungs-Erlaubnis einfach ohne Fortschritt
        }
    }

    private static void toast(final Context c, final String s) {
        new Handler(Looper.getMainLooper()).post(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(c.getApplicationContext(), s, Toast.LENGTH_LONG).show();
            }
        });
    }
}
