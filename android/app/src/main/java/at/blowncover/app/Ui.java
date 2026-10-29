package at.blowncover.app;

import android.content.Context;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.text.TextUtils;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

/** Native Bausteine im Design der Website (Farben, Schriften und Formen aus dem App-CSS). */
final class Ui {
    // :root aus index.html
    static final int BG = 0xFF0B0E12, PANEL = 0xFF141A21, PANEL2 = 0xFF1B232C, LINE = 0xFF2A343F,
            FG = 0xFFE9EEF3, MUT = 0xFF8D99A8, DANGER = 0xFFE5484D, OK = 0xFF3FB56A, PING = 0xFFFF8A1F,
            GHOST_LINE = 0xFF475262, LOG = 0xFFB8C2CD;

    /** Zustand eines Prüfpunkts: erfüllt, Pflicht fehlt, Empfehlung fehlt. */
    static final int ST_OK = 0, ST_NO = 1, ST_WARN = 2;

    private static Typeface fBody, fMed, fSemi, fDisp, fMono;

    private Ui() {}

    static void fonts(Context c) {
        if (fBody != null) return;
        try {
            fBody = c.getResources().getFont(R.font.barlow_regular);
            fMed = c.getResources().getFont(R.font.barlow_medium);
            fSemi = c.getResources().getFont(R.font.barlow_semibold);
            fDisp = c.getResources().getFont(R.font.barlow_condensed_bold);
            fMono = c.getResources().getFont(R.font.jetbrains_mono);
        } catch (Exception e) {
            fBody = fMed = Typeface.DEFAULT;
            fSemi = fDisp = Typeface.DEFAULT_BOLD;
            fMono = Typeface.MONOSPACE;
        }
    }

    static int dp(Context c, float v) {
        return Math.round(TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, c.getResources().getDisplayMetrics()));
    }

    static GradientDrawable box(Context c, int fill, int stroke, float radiusDp) {
        GradientDrawable g = new GradientDrawable();
        g.setColor(fill);
        g.setCornerRadius(dp(c, radiusDp));
        if (stroke != 0) g.setStroke(dp(c, 1), stroke);
        return g;
    }

    static TextView text(Context c, String t, float sp, int color, Typeface tf) {
        fonts(c);
        TextView v = new TextView(c);
        v.setText(t);
        v.setTextSize(TypedValue.COMPLEX_UNIT_SP, sp);
        v.setTextColor(color);
        v.setTypeface(tf);
        v.setIncludeFontPadding(false);
        v.setLineSpacing(0, 1.4f);
        return v;
    }

    static TextView body(Context c, String t) {
        fonts(c);
        return text(c, t, 14, MUT, fBody);
    }

    static TextView small(Context c, String t) {
        fonts(c);
        TextView v = text(c, t, 12, MUT, fBody);
        v.setLineSpacing(0, 1.3f);
        return v;
    }

    /** .dbx h3: 22px Barlow Condensed 700 */
    static TextView dialogTitle(Context c, String t) {
        fonts(c);
        TextView v = text(c, t, 22, FG, fDisp);
        v.setLetterSpacing(0.02f);
        return v;
    }

    /** Großer Bildschirmtitel (Barlow Condensed). */
    static TextView screenTitle(Context c, String t) {
        fonts(c);
        TextView v = text(c, t, 28, FG, fDisp);
        v.setLetterSpacing(0.02f);
        return v;
    }

    /** h3: 12px Barlow 700, Versalien, Sperrung .09em, gedämpft. */
    static TextView label(Context c, String t) {
        fonts(c);
        TextView v = text(c, t.toUpperCase(java.util.Locale.GERMANY), 12, MUT, fSemi);
        v.setLetterSpacing(0.09f);
        return v;
    }

    static TextView mono(Context c, String t) {
        fonts(c);
        TextView v = text(c, t, 10.5f, LOG, fMono);
        v.setLineSpacing(0, 1.5f);
        return v;
    }

    /** button (hell), button.g (Umriss), mit .s für den kleinen Zeilenknopf. */
    static Button button(Context c, String t, boolean primary, boolean smallSize, View.OnClickListener l) {
        fonts(c);
        Button b = new Button(c);
        b.setText(t);
        b.setAllCaps(false);
        b.setTypeface(fSemi);
        b.setTextSize(TypedValue.COMPLEX_UNIT_SP, smallSize ? 13 : 15);
        b.setStateListAnimator(null);
        b.setElevation(0);
        b.setGravity(Gravity.CENTER);
        int h = dp(c, smallSize ? 34 : 46);
        b.setMinHeight(h);
        b.setMinimumHeight(h);
        b.setMinWidth(0);
        b.setMinimumWidth(0);
        b.setPadding(dp(c, smallSize ? 11 : 14), 0, dp(c, smallSize ? 11 : 14), 0);
        style(c, b, primary, smallSize, true);
        b.setOnClickListener(l);
        return b;
    }

    static void style(Context c, Button b, boolean primary, boolean smallSize, boolean enabled) {
        float r = smallSize ? 9 : 12;
        b.setEnabled(enabled);
        if (!enabled) {
            b.setBackground(box(c, PANEL2, LINE, r));
            b.setTextColor(MUT);
        } else if (primary) {
            b.setBackground(box(c, FG, 0, r));
            b.setTextColor(BG);
        } else {
            GradientDrawable g = box(c, 0x00000000, GHOST_LINE, r);
            b.setBackground(g);
            b.setTextColor(FG);
        }
    }

    /** Runder Status-Punkt (✓ / !) mit getönter Fläche. */
    static TextView dot(Context c, int state) {
        fonts(c);
        TextView d = text(c, "", 13, FG, fSemi);
        d.setGravity(Gravity.CENTER);
        setDot(c, d, state);
        return d;
    }

    static void setDot(Context c, TextView d, int state) {
        int col = state == ST_OK ? OK : state == ST_NO ? DANGER : PING;
        d.setText(state == ST_OK ? "✓" : "!");
        d.setTextColor(col);
        GradientDrawable g = new GradientDrawable();
        g.setShape(GradientDrawable.OVAL);
        g.setColor((col & 0x00FFFFFF) | 0x26000000);
        d.setBackground(g);
    }

    /** Eine Zeile der Checkliste (.it): Punkt, Titel + Unterzeile, optional kleiner Knopf rechts. */
    static final class Item {
        final LinearLayout row;
        final TextView dot, title, sub;
        final Button action;

        Item(Context c, String t, String s, String actionText, View.OnClickListener l) {
            row = new LinearLayout(c);
            row.setOrientation(LinearLayout.HORIZONTAL);
            row.setGravity(Gravity.CENTER_VERTICAL);
            row.setPadding(dp(c, 10), dp(c, 9), dp(c, 10), dp(c, 9));
            row.setBackground(box(c, PANEL2, LINE, 12));
            dot = dot(c, ST_OK);
            int ds = dp(c, 22);
            LinearLayout.LayoutParams dl = new LinearLayout.LayoutParams(ds, ds);
            dl.rightMargin = dp(c, 10);
            row.addView(dot, dl);
            LinearLayout tx = new LinearLayout(c);
            tx.setOrientation(LinearLayout.VERTICAL);
            title = text(c, t, 14, FG, fSemi);
            sub = small(c, s);
            tx.addView(title);
            LinearLayout.LayoutParams sl = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            sl.topMargin = dp(c, 2);
            tx.addView(sub, sl);
            row.addView(tx, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
            if (actionText != null) {
                action = button(c, actionText, true, true, l);
                LinearLayout.LayoutParams al = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
                al.leftMargin = dp(c, 8);
                row.addView(action, al);
            } else {
                action = null;
            }
            title.setEllipsize(TextUtils.TruncateAt.END);
        }

        void set(Context c, int state, String subText) {
            setDot(c, dot, state);
            if (subText != null) sub.setText(subText);
            if (action != null) action.setVisibility(state == ST_OK ? View.GONE : View.VISIBLE);
        }
    }

    static LinearLayout.LayoutParams lp(Context c, int topDp) {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        p.topMargin = dp(c, topDp);
        return p;
    }
}
