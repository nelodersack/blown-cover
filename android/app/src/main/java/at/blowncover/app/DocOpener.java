package at.blowncover.app;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Handler;
import android.os.Looper;
import android.widget.Toast;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Locale;

/**
 * Spielanleitung (PDF) direkt in der PDF-Ansicht des Handys öffnen (seit v0.3.9, Konzept KONZEPT_PDF_in_App.md).
 * Die WebView kann keine PDF zeigen, und ein ACTION_VIEW auf blowncover.app landet wegen der App Links wieder in der App.
 * Darum: in den App-Cache laden (cache/docs) und über den LogProvider an die PDF-App geben.
 */
final class DocOpener {
    private static final long MAX = 20L * 1024 * 1024, FRESH = 24L * 3600 * 1000;
    private static volatile boolean busy = false;

    private DocOpener() {}

    static File dir(Context c) {
        return new File(c.getCacheDir(), "docs");
    }

    private static boolean okHost(String h) {
        return h != null && (h.equalsIgnoreCase("blowncover.app") || h.equalsIgnoreCase("www.blowncover.app"));
    }

    /** Dateiname aus der Adresse: nur blowncover.app/…/<name>.pdf, sonst null. */
    static String name(String url) {
        if (url == null) return null;
        Uri u = Uri.parse(url);
        if (!"https".equals(u.getScheme()) || !okHost(u.getHost())) return null;
        String n = u.getLastPathSegment();
        if (n == null || !n.toLowerCase(Locale.ROOT).endsWith(".pdf")) return null;
        n = n.replaceAll("[^A-Za-z0-9._-]", "_");
        return n.startsWith(".") ? null : n;
    }

    static void open(final Activity a, final String url) {
        final String n = name(url);
        if (n == null) {
            Diag.log(a, "PDF abgelehnt (nur blowncover.app/*.pdf): " + url);
            return;
        }
        final File f = new File(dir(a), n);
        if (f.exists() && System.currentTimeMillis() - f.lastModified() < FRESH) {
            Diag.log(a, "PDF aus dem Cache: " + n);
            view(a, f);
            return;
        }
        if (busy) return;
        busy = true;
        final Handler h = new Handler(Looper.getMainLooper());
        final Runnable hint = new Runnable() {
            @Override
            public void run() {
                if (busy) Toast.makeText(a, "Spielanleitung wird geladen …", Toast.LENGTH_SHORT).show();
            }
        };
        h.postDelayed(hint, 300);
        new Thread(new Runnable() {
            @Override
            public void run() {
                String err = null;
                try {
                    download(a, url, f);
                    Diag.log(a, "PDF geladen: " + n + " (" + f.length() / 1024 + " KB)");
                } catch (Exception e) {
                    err = e.getMessage() == null ? e.toString() : e.getMessage();
                }
                final String ee = err;
                h.post(new Runnable() {
                    @Override
                    public void run() {
                        busy = false;
                        h.removeCallbacks(hint);
                        if (ee == null) {
                            view(a, f);
                        } else if (f.exists()) {
                            Diag.log(a, "PDF laden fehlgeschlagen (" + ee + "), ältere Fassung wird geöffnet");
                            view(a, f);
                        } else {
                            Diag.log(a, "PDF laden FEHLER: " + ee);
                            Toast.makeText(a, "Spielanleitung konnte nicht geladen werden", Toast.LENGTH_LONG).show();
                        }
                    }
                });
            }
        }).start();
    }

    private static void download(Context c, String url, File out) throws Exception {
        File d = dir(c);
        if (!d.exists() && !d.mkdirs()) throw new Exception("Cache-Ordner nicht anlegbar");
        File tmp = new File(d, out.getName() + ".part");
        URL cur = new URL(url);
        HttpURLConnection con = null;
        boolean ok = false;
        for (int hop = 0; hop < 5; hop++) {
            if (!"https".equals(cur.getProtocol()) || !okHost(cur.getHost())) throw new Exception("unerwartetes Ziel " + cur.getHost());
            con = (HttpURLConnection) cur.openConnection();
            con.setInstanceFollowRedirects(false);
            con.setConnectTimeout(10000);
            con.setReadTimeout(20000);
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
        if (total > MAX) throw new Exception("Datei zu groß");
        InputStream in = con.getInputStream();
        FileOutputStream o = new FileOutputStream(tmp);
        long done = 0;
        byte[] head = new byte[4];
        try {
            byte[] buf = new byte[64 * 1024];
            int k;
            while ((k = in.read(buf)) > 0) {
                if (done < 4) System.arraycopy(buf, 0, head, (int) done, (int) Math.min(4 - done, k));
                o.write(buf, 0, k);
                done += k;
                if (done > MAX) throw new Exception("Datei zu groß");
            }
        } finally {
            o.close();
            in.close();
            con.disconnect();
        }
        if (total > 0 && done != total) throw new Exception("Download unvollständig");
        if (done < 4 || head[0] != '%' || head[1] != 'P' || head[2] != 'D' || head[3] != 'F') {
            tmp.delete();
            throw new Exception("keine PDF-Datei");
        }
        if (out.exists() && !out.delete()) throw new Exception("alte Datei nicht ersetzbar");
        if (!tmp.renameTo(out)) throw new Exception("Datei nicht speicherbar");
    }

    private static void view(Activity a, File f) {
        try {
            Uri u = Uri.parse("content://" + LogProvider.AUTH + "/" + Uri.encode(f.getName()));
            Intent i = new Intent(Intent.ACTION_VIEW);
            i.setDataAndType(u, "application/pdf");
            i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            a.startActivity(i);
        } catch (ActivityNotFoundException e) {
            Diag.log(a, "PDF: keine PDF-App installiert");
            Toast.makeText(a, "Keine App zum Anzeigen von PDFs gefunden", Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Diag.log(a, "PDF öffnen FEHLER: " + e);
            Toast.makeText(a, "Spielanleitung konnte nicht geöffnet werden", Toast.LENGTH_LONG).show();
        }
    }
}
