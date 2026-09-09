---
name: video-editor
description: עורך וידאו מקומי מבוסס ffmpeg — חיבור סרטונים, חיתוך (trim), שינוי יחס מסך לפורמטי סושיאל (9:16/1:1/16:9/4:5), דחיסה ל-WhatsApp/web, הוצאת/החלפת אודיו, צריבת כתוביות (כולל עברית RTL), טקסט על הסרטון, שינוי מהירות, חילוץ thumbnail, ויצירת GIF. רץ מקומית עם האצת חומרה (videotoolbox). שימושי כשדודו אומר "ערוך סרטון", "חבר את הסרטונים", "חתוך את הוידאו", "הפוך לרילס", "דחוס סרטון", "תוציא אודיו מהוידאו", "תוסיף כתוביות", "צור GIF". פלט ל-`_infra/video_output/`.
user-invocable: true
---

# Video Editor — עריכת וידאו מקומית

## מה זה עושה
wrapper מודרני סביב **ffmpeg 8.1** עם פעולות נפוצות מוגדרות מראש, ברירות מחדל שפויות, ו-pipeline אחיד לקידוד. רץ 100% מקומית, ללא עלות API, ללא העלאה לענן.

האצת חומרה ב-Mac: **VideoToolbox** לפענוח, `libx264` לקידוד (איכות/גודל טובים יותר מ-h264_videotoolbox; אם דרוש מהיר מאוד אפשר להחליף).

## הסקריפט
[`video.py`](video.py) — CLI יחיד עם subcommands.

```bash
python3 ~/.claude/skills/video-editor/video.py <command> [args...]
```

תיקיית פלט מומלצת: `~/my-business/_media/output/`

## פעולות

### 1. `info` — מידע על קובץ
```bash
python3 ~/.claude/skills/video-editor/video.py info /path/to/video.mp4
```
מציג: משך, גודל, bitrate, רזולוציה, fps, codec של וידאו/אודיו.

### 2. `concat` — חיבור סרטונים
```bash
python3 ~/.claude/skills/video-editor/video.py concat \
  /path/to/out.mp4 \
  /path/to/clip1.mp4 /path/to/clip2.mov /path/to/clip3.mp4
```
- מנרמל אוטומטית רזולוציה (לפי הראשון), 30fps, AAC stereo 48kHz.
- מתמודד עם codec/sample-rate שונים — re-encode מלא.
- Padding שחור אם יחס שונה (לא מותח את התמונה).

### 3. `trim` — חיתוך טווח זמן
```bash
# חיתוך מדויק (re-encode):
python3 ~/.claude/skills/video-editor/video.py trim in.mp4 out.mp4 --start 00:00:10 --end 00:01:25

# חיתוך מהיר (stream copy — נצמד ל-keyframes):
python3 ~/.claude/skills/video-editor/video.py trim in.mp4 out.mp4 --start 00:00:10 --end 00:01:25 --copy
```
פורמטים נתמכים: `HH:MM:SS`, `MM:SS`, או שניות (`75.5`).

### 4. `resize` — שינוי יחס מסך (לסושיאל)
```bash
# Reels / Shorts / TikTok (9:16 portrait, 1080×1920)
python3 ~/.claude/skills/video-editor/video.py resize in.mp4 out.mp4 --aspect 9:16

# Instagram feed square
python3 ~/.claude/skills/video-editor/video.py resize in.mp4 out.mp4 --aspect 1:1

# Instagram portrait
python3 ~/.claude/skills/video-editor/video.py resize in.mp4 out.mp4 --aspect 4:5
```

**מצבים** (`--mode`):
- `crop` (ברירת מחדל) — חותך כדי למלא את היחס. הכי טוב כשהאובייקט במרכז.
- `pad` — שומר את כל הפריים, מוסיף פסים שחורים.
- `blur` — שומר את כל הפריים, מוסיף רקע מטושטש מהוידאו עצמו (טוב לרילס).

### 5. `compress` — דחיסה
```bash
# CRF (איכות יחסית — ברירת מחדל crf=28 ≈ קומפקטי לוואטסאפ):
python3 ~/.claude/skills/video-editor/video.py compress in.mp4 out.mp4 --crf 28

# יעד גודל ספציפי (two-pass):
python3 ~/.claude/skills/video-editor/video.py compress in.mp4 out.mp4 --target-mb 25
```
- **WhatsApp:** מתחת ל-16MB. השתמש ב-`--target-mb 15`.
- **שליחה במייל:** מתחת ל-25MB. `--target-mb 25`.
- **איכות גבוהה לדף נחיתה:** `--crf 22`.

### 6. `extract-audio` — חילוץ אודיו
```bash
python3 ~/.claude/skills/video-editor/video.py extract-audio in.mp4 out.mp3
# פלט mp3 / wav / m4a לפי סיומת
```
שימושי לפני העברה לסקיל `transcribe` (תמלול עברית).

### 7. `mute` — הסרת אודיו
```bash
python3 ~/.claude/skills/video-editor/video.py mute in.mp4 out.mp4
```
stream copy — מהיר ובלי איבוד איכות.

### 8. `replace-audio` — החלפת אודיו
```bash
python3 ~/.claude/skills/video-editor/video.py replace-audio video.mp4 voiceover.mp3 out.mp4
```
הוידאו נשאר בלי re-encode; אודיו הופך ל-AAC 192k. מסונכרן לסוף הקצר מבין השניים.

### 9. `burn-subs` — צריבת כתוביות לוידאו (כולל עברית)
```bash
python3 ~/.claude/skills/video-editor/video.py burn-subs video.mp4 subs.srt out.mp4
python3 ~/.claude/skills/video-editor/video.py burn-subs video.mp4 he.srt out.mp4 --font-size 32 --rtl
```
- צובר את הכתוביות לתוך הפיקסלים (לא softsubs). שימושי לרילס/TikTok שלא מציגים SRT.
- עברית עובדת — libass תומך RTL ו-Bidi אוטומטית.

**יצירת SRT מההקלטה** — קודם תמלל דרך סקיל `transcribe` עם `--srt`:
```bash
python3 ~/.claude/skills/transcribe/transcribe.py video.mp4 --srt subs.srt
```

### 10. `text` — טקסט קבוע על הסרטון
```bash
python3 ~/.claude/skills/video-editor/video.py text in.mp4 out.mp4 \
  --text "הצטרפו לקורס" --pos bottom --size 64
```
מיקומים: `top` / `center` / `bottom`. רקע שחור שקוף ל-readability.

### 11. `speed` — שינוי מהירות
```bash
# x2 מהיר
python3 ~/.claude/skills/video-editor/video.py speed in.mp4 out.mp4 --factor 2.0

# חצי מהירות (slo-mo)
python3 ~/.claude/skills/video-editor/video.py speed in.mp4 out.mp4 --factor 0.5
```
האודיו משנה מהירות באותה פרופורציה (atempo, מטפל אוטומטית בגורמים מחוץ ל-0.5–2.0 על ידי שרשור).

### 12. `thumbnail` — תמונת שער
```bash
python3 ~/.claude/skills/video-editor/video.py thumbnail in.mp4 cover.jpg --time 00:00:05
```

### 13. `gif` — המרה ל-GIF
```bash
python3 ~/.claude/skills/video-editor/video.py gif in.mp4 out.gif \
  --start 00:00:10 --duration 4 --fps 12 --width 480
```
משתמש ב-palette generation דו-שלבי (איכות הרבה יותר טובה מהמרה ישירה).

## דפוסי שימוש נפוצים

### "תהפוך את הסרטון הזה לרילס לאינסטגרם"
```bash
OUT=~/my-business/_media/output/reel.mp4
python3 ~/.claude/skills/video-editor/video.py resize input.mp4 "$OUT" --aspect 9:16 --mode blur
```
`blur` מוסיף רקע מטושטש — נראה הכי טוב לסרטונים אופקיים שלא צולמו לסושיאל.

### "תכין הקלטה לוואטסאפ — קצרה ודחוסה"
```bash
TMP=/tmp/trim.mp4; OUT=~/my-business/_media/output/wa.mp4
python3 ~/.claude/skills/video-editor/video.py trim input.mp4 "$TMP" --start 00:00:00 --end 00:00:30
python3 ~/.claude/skills/video-editor/video.py compress "$TMP" "$OUT" --target-mb 14
```

### "תחבר 3 קליפים, תוסיף כותרת, ותוציא ב-9:16"
```bash
OUT_DIR=~/my-business/_media/output
python3 ~/.claude/skills/video-editor/video.py concat $OUT_DIR/joined.mp4 a.mp4 b.mp4 c.mp4
python3 ~/.claude/skills/video-editor/video.py text  $OUT_DIR/joined.mp4 $OUT_DIR/titled.mp4 --text "פרק חדש" --pos top --size 56
python3 ~/.claude/skills/video-editor/video.py resize $OUT_DIR/titled.mp4 $OUT_DIR/reel.mp4 --aspect 9:16 --mode blur
```

### "תמלל ותצרוב כתוביות לסרטון"
```bash
SRT=/tmp/subs.srt; OUT=~/my-business/_media/output/with_subs.mp4
python3 ~/.claude/skills/transcribe/transcribe.py input.mp4 --srt "$SRT" --quiet
python3 ~/.claude/skills/video-editor/video.py burn-subs input.mp4 "$SRT" "$OUT" --font-size 30
```

## ביצועים

- **קידוד SW (libx264, preset=medium, CRF 20):** ~3-5x זמן אמת על M-series Mac.
- **קידוד מהיר (videotoolbox):** ~10-15x זמן אמת אבל קבצים גדולים יותר ב-30-50% לאותה איכות. החלף `SWENC` ל-`HWENC` ב-`video.py` אם מדובר במאסה גדולה של קבצים.
- **`--copy` ב-trim/mute:** מיידי (אין re-encoding).

## מתי **לא** להשתמש בזה
- **עריכה לא-לינארית (timeline):** השתמש ב-Final Cut / DaVinci / Premiere. הסקיל הזה לפעולות חד-פעמיות.
- **Color grading מתקדם / VFX:** לא הכלי המתאים.
- **קומפוזיציה רב-שכבתית (picture-in-picture, transitions מורכבים):** efamiliar עם ffmpeg ידני שיתאים יותר.

## איך להוסיף פעולות חדשות
ערוך את [`video.py`](video.py):
1. כתוב פונקציה `op_xxx(args)` שמרכיבה פקודת ffmpeg ומריצה `run(cmd)`.
2. הוסף parser ל-`main()` עם `sp.add_parser("xxx")`.
3. עדכן את SKILL.md עם דוגמה.

ה-pattern של כל פעולה אחיד: בנה רשימת `cmd` עם flags ברירת מחדל קבועים (`-c:v SWENC`, `-preset medium`, `-crf 20`, `-movflags +faststart` ל-streaming).
