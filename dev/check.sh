#!/bin/sh
# Schnellprüfung: JS-Syntax von index.html + alle Tests in dev/tests.
# Aufruf aus dem Repo: sh dev/check.sh            (alle Tests)
#                     sh dev/check.sh syntax     (nur Syntax)
#                     sh dev/check.sh replay     (nur Tests, deren Name "replay" enthält)
cd "$(dirname "$0")/.." || exit 1
python3 - <<'P' || exit 1
import re,subprocess,tempfile
h=open('index.html',encoding='utf-8').read()
js=max(re.findall(r'<script>(.*?)</script>',h,re.S),key=len)
f=tempfile.NamedTemporaryFile('w',suffix='.js',delete=False);f.write(js);f.close()
r=subprocess.run(['node','--check',f.name],capture_output=True,text=True)
print('Syntax OK' if r.returncode==0 else r.stderr);raise SystemExit(r.returncode)
P
[ "$1" = syntax ] && exit 0
fail=0
for t in dev/tests/*${1}*.py; do
  echo "== $(basename "$t" .py)"
  out=$(timeout 180 python3 "$t" 2>&1); echo "$out" | tail -n 12
  echo "$out" | grep -q "^errors: \[\]" || { echo "!! FEHLER in $t"; fail=1; }
done
exit $fail
