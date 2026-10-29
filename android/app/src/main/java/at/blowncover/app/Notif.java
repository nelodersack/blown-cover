package at.blowncover.app;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.graphics.drawable.Icon;

/** Benachrichtigungen: dauerhafte Dienst-Anzeige und Spielmeldungen. */
final class Notif {
    static final String CH_SVC = "svc";
    static final String CH_EV = "ev";
    static final int ID_SVC = 1;
    private static int evCount = 0;

    private Notif() {}

    static void channels(Context c) {
        NotificationManager nm = c.getSystemService(NotificationManager.class);
        NotificationChannel s = new NotificationChannel(CH_SVC, "Spiel läuft", NotificationManager.IMPORTANCE_LOW);
        s.setShowBadge(false);
        nm.createNotificationChannel(s);
        NotificationChannel e = new NotificationChannel(CH_EV, "Spielmeldungen", NotificationManager.IMPORTANCE_HIGH);
        e.enableVibration(true);
        e.setVibrationPattern(new long[]{0, 250, 120, 250});
        nm.createNotificationChannel(e);
    }

    private static PendingIntent openGame(Context c) {
        Intent i = new Intent(c, GameActivity.class);
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        return PendingIntent.getActivity(c, 0, i, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
    }

    static Notification service(Context c, String text) {
        Intent stop = new Intent(c, LocationService.class).setAction(LocationService.ACT_QUIT);
        PendingIntent ps = PendingIntent.getService(c, 1, stop, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
        Notification.Action stopAct = new Notification.Action.Builder(
                Icon.createWithResource(c, R.drawable.ic_stat), "Beenden", ps).build();
        return new Notification.Builder(c, CH_SVC)
                .setSmallIcon(R.drawable.ic_stat)
                .setContentTitle("Blown Cover läuft")
                .setContentText(text)
                .setOngoing(true)
                .setCategory(Notification.CATEGORY_SERVICE)
                .setContentIntent(openGame(c))
                .addAction(stopAct)
                .build();
    }

    static void updateService(Context c, String text) {
        try {
            c.getSystemService(NotificationManager.class).notify(ID_SVC, service(c, text));
        } catch (Exception ignored) {
        }
    }

    /** Entfernt alle Benachrichtigungen der App. */
    static void clearAll(Context c) {
        c.getSystemService(NotificationManager.class).cancelAll();
    }

    /** Verlauf der letzten Spielmeldungen (neueste zuerst), angezeigt in einer einzigen Benachrichtigung. */
    private static final java.util.LinkedList<String> history = new java.util.LinkedList<>();
    private static final int ID_EV = 100;
    private static final int KEEP = 5;

    /**
     * Spielmeldung (Ping, Fang, Aufgabe ...). Es gibt immer nur EINE Meldungs-Benachrichtigung:
     * Jede neue ersetzt die alte (mit Ton/Vibration) und zeigt die letzten 5 Meldungen als Verlauf.
     */
    static synchronized void event(Context c, String title, String text) {
        try {
            channels(c);
            String time = new java.text.SimpleDateFormat("HH:mm:ss", java.util.Locale.GERMANY).format(new java.util.Date());
            history.addFirst(time + "  " + text);
            while (history.size() > KEEP) history.removeLast();
            Notification.Builder b = new Notification.Builder(c, CH_EV)
                    .setSmallIcon(R.drawable.ic_stat)
                    .setContentTitle(title)
                    .setContentText(text)
                    .setAutoCancel(true)
                    .setOnlyAlertOnce(false)
                    .setShowWhen(true)
                    .setCategory(Notification.CATEGORY_EVENT)
                    .setContentIntent(openGame(c));
            if (history.size() > 1) {
                Notification.InboxStyle st = new Notification.InboxStyle().setBigContentTitle(title);
                for (String h : history) st.addLine(h);
                b.setStyle(st);
            } else {
                b.setStyle(new Notification.BigTextStyle().bigText(text));
            }
            c.getSystemService(NotificationManager.class).notify(ID_EV, b.build());
        } catch (Exception e) {
            Diag.log(c, "Meldung fehlgeschlagen: " + e);
        }
    }

    /** Spielansicht geöffnet: Die Meldungen sind gesehen, der Verlauf beginnt von vorn. */
    static synchronized void clearHistory() {
        history.clear();
    }
}
