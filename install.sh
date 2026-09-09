#!/usr/bin/env bash
# install.sh - מעתיק את הסקילים ל-~/.claude/skills/ (לא דורס סקיל קיים בלי לשאול)
set -uo pipefail
cd "$(dirname "$0")"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$DEST"
echo "יעד: $DEST"
echo
installed=0; skipped=0
for d in skills/*/; do
  name=$(basename "$d")
  if [ -e "$DEST/$name" ]; then
    printf "  קיים אצלך: %-22s לדרוס? [y/N] " "$name"
    read -r ans </dev/tty || ans=n
    case "$ans" in [yY]*) cp -R "$d" "$DEST/" && echo "    נדרס" && installed=$((installed+1)) ;;
                   *) echo "    דולג" ; skipped=$((skipped+1)) ;; esac
  else
    cp -R "$d" "$DEST/" && printf "  ✓ %s\n" "$name" && installed=$((installed+1))
  fi
done
cat <<MSG

הותקנו: $installed · דולגו: $skipped

הצעד הבא: פתח שיחה חדשה בקלוד קוד וכתוב "/" - הסקילים אמורים להופיע.
חלקם דורשים כלי חיצוני (ffmpeg, מודל תמלול, מפתח API) - ראה את טבלת "מה צריך בשביל מה" ב-README.
MSG
