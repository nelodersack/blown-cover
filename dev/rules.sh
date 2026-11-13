#!/bin/sh
# Regelprüfung ohne Firebase: wertet database.rules.json (Zweig db-rules oder Datei als 1. Argument) offline aus (npm-Paket targaryen).
#   1. feste Fälle (dev/rules/faelle.js): Auslosen, Zombie, Fang starten, Kick, Host, Einstellungen
#   2. alle Schreibvorgänge, die die App in den Tests macht (dev/tests, Protokoll über WLOG) – dauert so lange wie sh dev/check.sh
# Aufruf: sh dev/rules.sh [datei.json] [schnell]     (schnell = nur die festen Fälle)
cd "$(dirname "$0")/.." || exit 1
R="$1"; if [ -z "$R" ] || [ "$R" = schnell ]; then R=dev/out/database.rules.json; mkdir -p dev/out; { git fetch -q origin db-rules 2>/dev/null && git show FETCH_HEAD:database.rules.json > "$R"; } || git show db-rules:database.rules.json > "$R" || exit 1; fi
[ -d dev/rules/node_modules/targaryen ] || (cd dev/rules && npm i --no-save --silent targaryen >/dev/null 2>&1) || { echo "targaryen ließ sich nicht installieren"; exit 1; }
node dev/rules/faelle.js "$R" || exit 1
[ "$1" = schnell ] || [ "$2" = schnell ] && exit 0
rm -rf dev/out/wlog; WLOG="$PWD/dev/out/wlog" sh dev/check.sh >/dev/null 2>&1
node dev/rules/replay.js "$R" dev/out/wlog
