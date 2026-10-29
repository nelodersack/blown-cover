package at.blowncover.app;

import android.content.Context;
import android.content.SharedPreferences;

/** Einstellungen: welche Adresse die App lädt. */
final class Prefs {
    static final String LIVE = "https://nelodersack.github.io/blown-cover/";
    static final String TEST = "https://nelodersack.github.io/blown-cover/index_app.html";

    static final String VER = "0.1.0";

    private Prefs() {}

    private static SharedPreferences p(Context c) {
        return c.getSharedPreferences("bc", Context.MODE_PRIVATE);
    }

    static String mode(Context c) {
        return p(c).getString("mode", "live");
    }

    static void setMode(Context c, String m) {
        p(c).edit().putString("mode", m).apply();
    }

    static String custom(Context c) {
        return p(c).getString("custom", "");
    }

    static void setCustom(Context c, String u) {
        p(c).edit().putString("custom", u).apply();
    }

    static String url(Context c) {
        String m = mode(c);
        if ("test".equals(m)) return TEST;
        if ("custom".equals(m)) {
            String u = custom(c).trim();
            if (u.startsWith("https://")) return u;
        }
        return LIVE;
    }
}
