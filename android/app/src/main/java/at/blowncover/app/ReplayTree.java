package at.blowncover.app;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.UriPermission;
import android.database.Cursor;
import android.net.Uri;
import android.provider.DocumentsContract;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.LinearLayout;

import org.json.JSONObject;

import java.util.List;
import java.util.Locale;

/**
 * Einmalige Ordner-Freigabe (SAF) für „Dokumente/Blown Cover/Replays“ (seit v0.3.8).
 * MediaStore zeigt der App nur ihre eigenen Dateien; mit der Freigabe erscheinen auch von Hand kopierte Replays.
 */
final class ReplayTree {
    static final int REQ = 8;
    private static final String SP = "bc_replays", K_TREE = "tree", K_NO = "declined";
    private static final String EXT = "com.android.externalstorage.documents";
    /** In dieser Sitzung schon gefragt (Hinweis nicht bei jedem replays()-Aufruf). */
    static boolean askedNow = false;

    private ReplayTree() {}

    private static android.content.SharedPreferences sp(Context c) {
        return c.getSharedPreferences(SP, Context.MODE_PRIVATE);
    }

    /** Freigegebener Ordner, nur wenn die dauerhafte Leseberechtigung noch besteht. */
    static Uri tree(Context c) {
        String s = sp(c).getString(K_TREE, null);
        if (s == null) return null;
        Uri u = Uri.parse(s);
        List<UriPermission> ps = c.getContentResolver().getPersistedUriPermissions();
        for (UriPermission p : ps) if (p.isReadPermission() && u.equals(p.getUri())) return u;
        return null;
    }

    static boolean declined(Context c) {
        return sp(c).getBoolean(K_NO, false);
    }

    static void setDeclined(Context c, boolean v) {
        sp(c).edit().putBoolean(K_NO, v).apply();
    }

    static Intent pickIntent() {
        Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        i.putExtra(DocumentsContract.EXTRA_INITIAL_URI,
                DocumentsContract.buildDocumentUri(EXT, "primary:" + GameActivity.DIR + "/Replays"));
        return i;
    }

    /** Ergebnis der Ordnerauswahl; true = Freigabe gespeichert. */
    static boolean onResult(Context c, int res, Intent data) {
        Uri u = (res == Activity.RESULT_OK && data != null) ? data.getData() : null;
        if (u == null) {
            setDeclined(c, true);
            Diag.log(c, "Replay-Ordner: Freigabe abgelehnt");
            return false;
        }
        try {
            c.getContentResolver().takePersistableUriPermission(u, Intent.FLAG_GRANT_READ_URI_PERMISSION);
            sp(c).edit().putString(K_TREE, u.toString()).putBoolean(K_NO, false).apply();
            Diag.log(c, "Replay-Ordner freigegeben: " + DocumentsContract.getTreeDocumentId(u));
            return true;
        } catch (Exception e) {
            Diag.log(c, "Replay-Ordner: Freigabe FEHLER " + e);
            return false;
        }
    }

    /** Lesbarer Name des freigegebenen Ordners für die Diagnose. */
    static String label(Context c) {
        Uri t = tree(c);
        if (t == null) return declined(c) ? "nicht freigegeben (abgelehnt)" : "nicht freigegeben";
        String id = DocumentsContract.getTreeDocumentId(t);
        int k = id.indexOf(':');
        return "freigegeben: " + (k >= 0 ? id.substring(k + 1) : id);
    }

    /** *.json im freigegebenen Ordner (ohne Analysen), als {id,name,size,t,dir}; id = Document-URI. */
    static void list(Context c, List<JSONObject> out) {
        Uri t = tree(c);
        if (t == null) return;
        Cursor q = null;
        try {
            Uri ch = DocumentsContract.buildChildDocumentsUriUsingTree(t, DocumentsContract.getTreeDocumentId(t));
            q = c.getContentResolver().query(ch, new String[]{DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                    DocumentsContract.Document.COLUMN_DISPLAY_NAME, DocumentsContract.Document.COLUMN_SIZE,
                    DocumentsContract.Document.COLUMN_LAST_MODIFIED, DocumentsContract.Document.COLUMN_MIME_TYPE}, null, null, null);
            while (q != null && q.moveToNext()) {
                String n = q.getString(1);
                if (n == null || DocumentsContract.Document.MIME_TYPE_DIR.equals(q.getString(4))) continue;
                String l = n.toLowerCase(Locale.ROOT);
                if (!l.endsWith(".json") || l.startsWith("blowncover_analyse")) continue;
                JSONObject o = new JSONObject();
                o.put("id", DocumentsContract.buildDocumentUriUsingTree(t, q.getString(0)).toString());
                o.put("name", n);
                o.put("size", q.isNull(2) ? 0 : q.getLong(2));
                o.put("t", q.isNull(3) ? 0 : q.getLong(3));
                o.put("dir", "Replays");
                out.add(o);
            }
        } catch (Exception e) {
            Diag.log(c, "Replay-Ordner lesen FEHLER: " + e);
        } finally {
            if (q != null) q.close();
        }
    }

    /** Nur Dokumente innerhalb des freigegebenen Ordners dürfen über readReplay gelesen werden. */
    static boolean allowed(Context c, Uri u) {
        Uri t = tree(c);
        return t != null && u != null && EXT.equals(u.getAuthority()) && u.toString().startsWith(t.toString() + "/document/");
    }

    /** Hinweis im App-Design vor der Systemauswahl. */
    static void showHint(final Activity a, final FrameLayout frame, final Runnable onPick, final Runnable onLater) {
        final FrameLayout root = new FrameLayout(a);
        root.setBackgroundColor(0xBB000000);
        root.setClickable(true);
        int pad = Ui.dp(a, 16);
        root.setPadding(pad, pad, pad, pad);
        LinearLayout card = new LinearLayout(a);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setBackground(Ui.box(a, Ui.PANEL, Ui.LINE, 18));
        int cp = Ui.dp(a, 18);
        card.setPadding(cp, cp, cp, cp);
        card.setElevation(Ui.dp(a, 12));
        int w = Math.min(Ui.dp(a, 380), a.getResources().getDisplayMetrics().widthPixels - 2 * pad);
        root.addView(card, new FrameLayout.LayoutParams(w, ViewGroup.LayoutParams.WRAP_CONTENT, Gravity.CENTER));
        card.addView(Ui.dialogTitle(a, "Replay-Ordner freigeben"));
        card.addView(Ui.body(a, "Damit auch kopierte Replays erscheinen, wähle einmal den Ordner „Blown Cover/Replays“ und tippe „Zugriff erlauben“."), Ui.lp(a, 8));
        card.addView(Ui.small(a, "Später jederzeit in der Diagnose (App-Symbol lange drücken)."), Ui.lp(a, 6));
        card.addView(Ui.button(a, "Ordner wählen", true, false, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                frame.removeView(root);
                onPick.run();
            }
        }), Ui.lp(a, 14));
        card.addView(Ui.button(a, "Später", false, false, new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                frame.removeView(root);
                onLater.run();
            }
        }), Ui.lp(a, 8));
        frame.addView(root, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
    }
}
