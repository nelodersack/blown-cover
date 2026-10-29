package at.blowncover.app;

import android.Manifest;
import android.app.Activity;
import android.app.NotificationManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.location.LocationManager;
import android.net.Uri;
import android.os.Build;
import android.os.PowerManager;
import android.provider.Settings;
import android.widget.Toast;

/** Bereitschafts-Prüfungen und die passenden Aktionen (Berechtigung anfragen, Einstellungen öffnen). */
final class Checks {
    static final int RC_LOC = 11, RC_NOT = 12;
    private static final String PREF_ASKED_LOC = "askedLoc", PREF_ASKED_NOT = "askedNot";

    private Checks() {}

    /** Genauer Standort erlaubt (Pflicht). */
    static boolean loc(Context c) {
        return c.checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED;
    }

    /** Nur ungefährer Standort erlaubt (reicht fürs Spiel nicht). */
    static boolean coarseOnly(Context c) {
        return !loc(c) && c.checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED;
    }

    /** GPS eingeschaltet (Pflicht). */
    static boolean gps(Context c) {
        try {
            LocationManager lm = (LocationManager) c.getSystemService(Context.LOCATION_SERVICE);
            return lm.isProviderEnabled(LocationManager.GPS_PROVIDER);
        } catch (Exception e) {
            return false;
        }
    }

    /** Benachrichtigungen erlaubt (empfohlen). */
    static boolean notif(Context c) {
        if (Build.VERSION.SDK_INT >= 33
                && c.checkSelfPermission("android.permission.POST_NOTIFICATIONS") != PackageManager.PERMISSION_GRANTED) return false;
        return c.getSystemService(NotificationManager.class).areNotificationsEnabled();
    }

    /** Von der Akku-Optimierung ausgenommen (empfohlen). */
    static boolean battery(Context c) {
        PowerManager pm = (PowerManager) c.getSystemService(Context.POWER_SERVICE);
        return pm.isIgnoringBatteryOptimizations(c.getPackageName());
    }

    static boolean required(Context c) {
        return loc(c) && gps(c);
    }

    static boolean all(Context c) {
        return required(c) && notif(c) && battery(c);
    }

    /** Fehlende Punkte als kurze Liste, z. B. „GPS, Akku“ (leer = alles bereit). */
    static String missing(Context c) {
        StringBuilder b = new StringBuilder();
        if (!loc(c)) b.append("Standort, ");
        if (!gps(c)) b.append("GPS, ");
        if (!notif(c)) b.append("Benachrichtigungen, ");
        if (!battery(c)) b.append("Akku, ");
        return b.length() == 0 ? "" : b.substring(0, b.length() - 2);
    }

    static void askLoc(Activity a) {
        // Hat der Nutzer schon zweimal abgelehnt, zeigt Android keinen Dialog mehr: dann App-Einstellungen öffnen.
        boolean asked = a.getSharedPreferences("bc", 0).getBoolean(PREF_ASKED_LOC, false);
        if (asked && !a.shouldShowRequestPermissionRationale(Manifest.permission.ACCESS_FINE_LOCATION) && !coarseOnly(a)) {
            appSettings(a, "Bitte unter „Berechtigungen → Standort“ den genauen Standort erlauben");
            return;
        }
        a.getSharedPreferences("bc", 0).edit().putBoolean(PREF_ASKED_LOC, true).apply();
        a.requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}, RC_LOC);
    }

    static void askGps(Activity a) {
        try {
            a.startActivity(new Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS));
        } catch (Exception e) {
            Toast.makeText(a, "Bitte GPS / Standort in den Schnelleinstellungen einschalten", Toast.LENGTH_LONG).show();
        }
    }

    static void askNotif(Activity a) {
        boolean asked = a.getSharedPreferences("bc", 0).getBoolean(PREF_ASKED_NOT, false);
        if (Build.VERSION.SDK_INT >= 33 && !(asked && !a.shouldShowRequestPermissionRationale("android.permission.POST_NOTIFICATIONS"))
                && a.checkSelfPermission("android.permission.POST_NOTIFICATIONS") != PackageManager.PERMISSION_GRANTED) {
            a.getSharedPreferences("bc", 0).edit().putBoolean(PREF_ASKED_NOT, true).apply();
            a.requestPermissions(new String[]{"android.permission.POST_NOTIFICATIONS"}, RC_NOT);
            return;
        }
        try {
            a.startActivity(new Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).putExtra(Settings.EXTRA_APP_PACKAGE, a.getPackageName()));
        } catch (Exception e) {
            appSettings(a, "Bitte Benachrichtigungen für Blown Cover erlauben");
        }
    }

    static void askBattery(Activity a) {
        try {
            a.startActivity(new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, Uri.parse("package:" + a.getPackageName())));
        } catch (Exception e) {
            try {
                a.startActivity(new Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS));
            } catch (Exception e2) {
                Toast.makeText(a, "Bitte in den Android-Einstellungen die Akku-Optimierung für Blown Cover ausschalten", Toast.LENGTH_LONG).show();
            }
        }
    }

    private static void appSettings(Activity a, String hint) {
        Toast.makeText(a, hint, Toast.LENGTH_LONG).show();
        try {
            a.startActivity(new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:" + a.getPackageName())));
        } catch (Exception ignored) {
        }
    }
}
