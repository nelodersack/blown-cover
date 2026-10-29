package at.blowncover.app;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.net.Uri;
import android.os.Build;
import android.os.ParcelFileDescriptor;
import android.provider.OpenableColumns;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/** Stellt das Diagnose-Protokoll als Datei zum Teilen bereit (nur lesend, nur per erteilter Freigabe). */
public class LogProvider extends ContentProvider {
    static final String AUTH = "at.blowncover.app.logs";

    /** Schreibt eine Momentaufnahme des Protokolls und liefert ihre Teilen-Adresse. */
    static Uri snapshot(Context c) throws Exception {
        File dir = new File(c.getCacheDir(), "logs");
        if (!dir.exists() && !dir.mkdirs()) throw new Exception("Ordner nicht anlegbar");
        File[] old = dir.listFiles();
        if (old != null) for (File f : old) //noinspection ResultOfMethodCallIgnored
            f.delete();
        String name = "BlownCover_Log_" + new SimpleDateFormat("yyyyMMdd-HHmm", Locale.GERMANY).format(new Date()) + ".txt";
        String head = "Blown Cover App v" + Prefs.ver(c) + " · " + Build.MANUFACTURER + " " + Build.MODEL
                + " · Android " + Build.VERSION.SDK_INT + "\n\n";
        FileOutputStream o = new FileOutputStream(new File(dir, name));
        o.write(head.getBytes("UTF-8"));
        o.write(Diag.all(c).getBytes("UTF-8"));
        o.close();
        return Uri.parse("content://" + AUTH + "/" + Uri.encode(name));
    }

    private File file(Uri u) throws FileNotFoundException {
        String n = u.getLastPathSegment();
        if (n == null || n.contains("/") || n.contains("..")) throw new FileNotFoundException();
        File f = new File(new File(getContext().getCacheDir(), "logs"), n);
        if (!f.exists()) throw new FileNotFoundException();
        return f;
    }

    @Override
    public boolean onCreate() {
        return true;
    }

    @Override
    public String getType(Uri uri) {
        return "text/plain";
    }

    @Override
    public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
        if (mode != null && !mode.equals("r")) throw new FileNotFoundException("nur lesend");
        return ParcelFileDescriptor.open(file(uri), ParcelFileDescriptor.MODE_READ_ONLY);
    }

    @Override
    public Cursor query(Uri uri, String[] projection, String sel, String[] args, String sort) {
        File f;
        try {
            f = file(uri);
        } catch (FileNotFoundException e) {
            return null;
        }
        String[] cols = {OpenableColumns.DISPLAY_NAME, OpenableColumns.SIZE};
        MatrixCursor c = new MatrixCursor(cols, 1);
        c.addRow(new Object[]{f.getName(), f.length()});
        return c;
    }

    @Override
    public Uri insert(Uri uri, ContentValues v) {
        return null;
    }

    @Override
    public int delete(Uri uri, String s, String[] a) {
        return 0;
    }

    @Override
    public int update(Uri uri, ContentValues v, String s, String[] a) {
        return 0;
    }
}
