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
}
