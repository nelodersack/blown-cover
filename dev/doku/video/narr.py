# Sprechertext je Szene: Liste von (Untertitel, Sprechfassung)
S = {
 1: ["Willkommen bei Blown Cover.", "Ein Versteckspiel in echt. Draußen, mit dem Handy."],
 2: ["Einer erstellt das Spiel und schickt den Link in die Gruppe.", "Wer ihn öffnet, gibt seinen Namen ein und ist drin.", "Ohne Link geht es mit dem Code."],
 3: ["Zwei Seiten. Die Hunter jagen, die Hider verschwinden.", "Der Host legt Zone und Dauer fest und startet die Operation."],
 4: ["Jeder erhält sein Briefing.", "Die Hider haben jetzt fünf Minuten Vorsprung. Die Hunter warten."],
 5: ["Der rote Kreis ist euer Einsatzgebiet.", "Er wird regelmäßig kleiner, der gestrichelte Kreis zeigt, wohin.", "Wer als Hider hinausgeht, ist für die Hunter sofort live sichtbar."],
 6: ["Alle drei Minuten kommt ein Ping.", "Die Hunter sehen, wo jeder Hider in diesem Moment stand.", "Nur in diesem Moment. Danach ist die Spur kalt."],
 7: ["Hider können Aufgaben erledigen. Zum Beispiel das Safehouse.", "Nur zwei Plätze.", "Wer zuerst eincheckt, bekommt drei Minuten Immunität.", "Eingesetzt taucht man bei keinem Ping auf. Fangen geht trotzdem."],
 8: ["Gefangen ist, wen der Hunter berührt und in der App meldet.", "Der Hider bestätigt.", "Tom ist draußen und schaut ab jetzt zu."],
 9: ["Für jeden Fang gibt es einen Bonus.", "Anna wählt den Extra-Ping und ortet sofort alle Hider.", "Fast alle. Lena ist noch immun."],
 10: ["Die Hunter gewinnen, wenn alle Hider gefangen sind.", "Die Hider, wenn die Zeit abläuft.", "Einsatz beginnt auf blowncover.app."],
}
PH = [("Blown Cover", "Blohn Kaver"), ("Hunter", "Hanter"), ("Hider", "Haider"), ("Safehouse", "Seifhaus"),
      ("Briefing", "Brieefing"), ("blowncover.app", "blohnkaver punkt äpp"), ("Extra-Ping", "Extra Ping"), ("Host", "Hohst")]
def speak(t):
    for a, b in PH: t = t.replace(a, b)
    return t
