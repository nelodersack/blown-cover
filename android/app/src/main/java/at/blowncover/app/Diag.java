package at.blowncover.app;

import android.content.Context;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/** Einfaches Diagnose-Protokoll (Datei im App-Speicher), damit sich Probleme nachvollziehen lassen. */
final class Diag {
    private static final String FILE = "diag.log";
    private static final int MAX_BYTES = 300 * 1024;
    private static final SimpleDateFormat FMT = new SimpleDateFormat("dd.MM. HH:mm:ss", Locale.GERMANY);

    private Diag() {}

    static synchronized void log(Context c, String msg) {
        try {
            String line = FMT.format(new Date()) + "  " + msg + "\n";
            File f = new File(c.getFilesDir(), FILE);
            if (f.length() > MAX_BYTES) {
                String tail = tail(c, 800);
                FileOutputStream o = new FileOutputStream(f, false);
                o.write(tail.getBytes("UTF-8"));
                o.close();
            }
            FileOutputStream o = new FileOutputStream(f, true);
            o.write(line.getBytes("UTF-8"));
            o.close();
        } catch (Exception ignored) {
        }
    }

    static synchronized String tail(Context c, int lines) {
        try {
            File f = new File(c.getFilesDir(), FILE);
            if (!f.exists()) return "";
            FileInputStream in = new FileInputStream(f);
            ByteArrayOutputStream bo = new ByteArrayOutputStream();
            byte[] buf = new byte[8192];
            int n;
            while ((n = in.read(buf)) > 0) bo.write(buf, 0, n);
            in.close();
            String all = bo.toString("UTF-8");
            String[] parts = all.split("\n");
            List<String> out = new ArrayList<>();
            int from = Math.max(0, parts.length - lines);
            for (int i = from; i < parts.length; i++) out.add(parts[i]);
            StringBuilder sb = new StringBuilder();
            for (String s : out) sb.append(s).append('\n');
            return sb.toString();
        } catch (Exception e) {
            return "";
        }
    }

    /** Das gesamte Protokoll (für „Log teilen“ als Datei). */
    static synchronized String all(Context c) {
        return tail(c, Integer.MAX_VALUE);
    }

    static synchronized void clear(Context c) {
        try {
            new File(c.getFilesDir(), FILE).delete();
        } catch (Exception ignored) {
        }
    }
}
