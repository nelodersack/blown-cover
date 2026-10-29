package at.blowncover.app;

import android.app.Activity;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;

/**
 * „Bereit machen“: Dialog im App-Design über der Spielansicht. Erscheint nur, wenn etwas fehlt.
 * Rot = Pflicht (Standort, GPS) sperrt „Spielen“; Orange = empfohlen (Benachrichtigungen, Akku).
 */
final class ReadyDialog {
    interface Listener {
        void onPlay();
    }

    final FrameLayout root;
    private final Activity a;
    private final Ui.Item loc, gps, not, bat;
    private final Button play;
    private final TextView hint;

    ReadyDialog(final Activity act, final Listener l) {
        a = act;
        root = new FrameLayout(a);
        root.setBackgroundColor(0xBB000000); // #000b
        root.setClickable(true);            // Spiel darunter nicht bedienbar
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

        card.addView(Ui.dialogTitle(a, "Bereit machen"));
        TextView p = Ui.body(a, "");
        p.setText(android.text.Html.fromHtml("Damit dein Standort auch bei <font color='#E9EEF3'><b>ausgeschaltetem Display</b></font> ans Spiel geht, braucht die App noch Folgendes:", 0));
        card.addView(p, Ui.lp(a, 8));

        loc = new Ui.Item(a, "Standort", "", "Erlauben", new View.OnClickListener() {
            public void onClick(View v) {
                Checks.askLoc(a);
            }
        });
        gps = new Ui.Item(a, "GPS", "", "Einschalten", new View.OnClickListener() {
            public void onClick(View v) {
                Checks.askGps(a);
            }
        });
        not = new Ui.Item(a, "Benachrichtigungen", "", "Erlauben", new View.OnClickListener() {
            public void onClick(View v) {
                Checks.askNotif(a);
            }
        });
        bat = new Ui.Item(a, "Akku-Optimierung", "", "Ausnehmen", new View.OnClickListener() {
            public void onClick(View v) {
                Checks.askBattery(a);
            }
        });
        card.addView(loc.row, Ui.lp(a, 14));
        card.addView(gps.row, Ui.lp(a, 6));
        card.addView(not.row, Ui.lp(a, 6));
        card.addView(bat.row, Ui.lp(a, 6));

        play = Ui.button(a, "Spielen", true, false, new View.OnClickListener() {
            public void onClick(View v) {
                if (Checks.required(a)) l.onPlay();
            }
        });
        card.addView(play, Ui.lp(a, 16));
        hint = Ui.small(a, "");
        hint.setGravity(Gravity.CENTER);
        card.addView(hint, Ui.lp(a, 6));
        refresh();
    }

    void refresh() {
        boolean okLoc = Checks.loc(a), okGps = Checks.gps(a), okNot = Checks.notif(a), okBat = Checks.battery(a);
        loc.set(a, okLoc ? Ui.ST_OK : Ui.ST_NO, okLoc ? "erlaubt" : Checks.coarseOnly(a) ? "nur ungefähr – genauer Standort nötig" : "nicht erlaubt");
        gps.set(a, okGps ? Ui.ST_OK : Ui.ST_NO, okGps ? "eingeschaltet" : "ist ausgeschaltet");
        not.set(a, okNot ? Ui.ST_OK : Ui.ST_WARN, okNot ? "erlaubt" : "für Pings bei Display aus");
        bat.set(a, okBat ? Ui.ST_OK : Ui.ST_WARN, okBat ? "ausgenommen" : "sonst kann Android die App beenden");
        boolean req = okLoc && okGps;
        Ui.style(a, play, true, false, req);
        String h = !okLoc && !okGps ? "Standort und GPS sind nötig" : !okLoc ? "Standort-Erlaubnis ist nötig" : !okGps ? "GPS muss an sein" : "";
        hint.setText(h);
        hint.setVisibility(h.isEmpty() ? View.GONE : View.VISIBLE);
    }

    boolean showing() {
        return root.getParent() != null && root.getVisibility() == View.VISIBLE;
    }
}
