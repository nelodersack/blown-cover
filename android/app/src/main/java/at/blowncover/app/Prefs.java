package at.blowncover.app;

import android.content.Context;

/** Adresse, die die App lädt: immer die Live-Seite (sie enthält die App-Anbindung). */
final class Prefs {
    static final String LIVE = "https://nelodersack.github.io/blown-cover/";

    /** Versionsname aus dem installierten Paket (build.gradle: versionName). */
    static String ver(Context c) {
        try {
            return c.getPackageManager().getPackageInfo(c.getPackageName(), 0).versionName;
        } catch (Exception e) {
            return "?";
        }
    }

    private Prefs() {}

    static String url(Context c) {
        return LIVE;
    }

    // Darstellung (seit v0.3.0, Schalter in der Diagnose): Standard wie im Chrome-Browser.
    // preRaster = Seite auch außerhalb des sichtbaren Bereichs vorzeichnen; maxHz = höchste Bildrate erzwingen (z. B. 120 Hz).
    static boolean preRaster(Context c) {
        return sp(c).getBoolean("preRaster", false);
    }

    static boolean maxHz(Context c) {
        return sp(c).getBoolean("maxHz", false);
    }

    static void set(Context c, String k, boolean v) {
        sp(c).edit().putBoolean(k, v).apply();
    }

    private static android.content.SharedPreferences sp(Context c) {
        return c.getSharedPreferences("bc_render", Context.MODE_PRIVATE);
    }
}
