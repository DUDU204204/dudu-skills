---
name: reel-captions
description: יוצר ריל 9:16 עם כתוביות מעוצבות בעברית בשני סגנונות מוכחים — "clean" (הסגנון האלגנטי של רילי פייסבוק: לבן בולד ממורכז עם הילת-צל רכה, כרטיסים קצרים שמתחלפים מהר) ו-"kinetic" (סגנון קינטי: שורות שנערמות עם חצי-זהב ❯, צבע וגודל משתנה, PiP מעוגל). תומך בחיתוכי-רקע מרובים, מוזיקה מסונתזת, וזרימת auto+עריכה-ידנית של קובץ ASS. שימושי כשדודו אומר "תכין ריל עם כתוביות", "כתוביות קינטיות", "ריל בסגנון הפייסבוק", "תוסיף כתוביות מעוצבות לסרטון", "reel captions". מבוסס Reel Studio ב-`_infra/reel_studio/`.
user-invocable: true
---

# Reel Captions — רילים עם כתוביות מעוצבות (Reel Studio)

הכלי חי ב-`~/my-business/_infra/reel_studio/`. מודולים:
- `captions.py` — מנוע ה-ASS (libass). בונה את הכתוביות המעוצבות.
- `make_reel.py` — האורקסטרטור: אודיו → כתוביות → רקע → מיקס → צריבה.
- `azure_tts.py` — **מסלול TTS נכון**: Azure Speech SDK שמחזיר **word boundaries** (תזמוני-מילים מדויקים) + הגייה דרך לקסיקון IPA של ג'רוויס.
- `nikud.py` — ניקוד Dicta (legacy; **לא בשימוש במסלול TTS** — ראה אזהרה למטה).

## ⚠️ חוק קריטי לכתוביות TTS — לא לתמלל, לא לנקד
כש**ג'רוויס מקריין** (יש לנו את הסקריפט המדויק):
- **כתוביות = הטקסט המקורי + תזמוני Azure word-boundary** (`azure_tts.synth` מחזיר `[{word,start,end}]`). **אסור לתמלל בחזרה את האודיו** — whisper "שומע" את הקול המסונתז וממציא שגיאות כתיב (דודו→דבודו, שיווקי→שיעוקי). make_reel כבר עושה זאת אוטומטית במסלול `--text`.
- **הגייה = טקסט רגיל + לקסיקון IPA** של ג'רוויס (`jarvis_briefing/lexicon.json`, עריך דרך /lexicon). **אסור להזין ניקוד** — ניקוד עוקף את הלקסיקון וגורם ל-avri להגות יתר (זה מה ששיבש). מילה שנהגית לא נכון → להוסיף ערך IPA ללקסיקון, לא לנקד.
- מילים שנהגות עדיין שגוי? בדיקה אוטומטית: לתמלל את האודיו עם whisper כפרוקסי — אם whisper שומע את המילה הנכונה, ההגייה ברורה.

`--rate` שולט במהירות (1.0 רגיל, ~1.24 ≈ קצב ריל אנרגטי). התזמונים נשמרים מסונכרנים בכל rate.

## שני סגנונות (presets)

| preset | מתי | מאפיינים |
|--------|-----|----------|
| **clean** (ברירת מחדל) | קול אדם אמיתי על B-roll (כמו רילי הפייסבוק) | לבן Assistant ExtraBold, ממורכז, **הילת-צל רכה** (לא קופסה), כרטיסי 2-4 מילים שמתחלפים מהר |
| **kinetic** | עדות או ציטוט עם דובר על המסך | שורות שנערמות עם פייד, חצי-זהב ❯, צבע וגודל משתנה |

## שלוש פריסות (`--layout`)
- **fullbg** (ברירת מחדל ל-clean) — כתובית ישר מעל הקליפ. כמה `--video` = חיתוכי-סצנה רצופים שממלאים את האודיו.
- **blurbg** — מילוי מטושטש מאחורי קליפ ממורכז (ה-look המקורי של Reel Studio).
- **pip** (ברירת מחדל ל-kinetic) — כרטיס דובר מעוגל למעלה + רקע גרדיאנט כהה.

## זרימת עבודה: auto + עריכה ידנית (כפי שדודו ביקש)
1. **auto** — הכרטיסים נבנים אוטומטית. מסלול `--text` (TTS): מ-Azure word boundaries (מדויק, מהסקריפט). מסלול `--audio` (קול אמיתי): מ-whisper word-timestamps.
2. **עריכה** — מריצים עם `--ass-out cap.ass`, הכלי כותב קובץ ASS קריא ו**עוצר**. עורכים אותו (טקסט, תזמון, צבע, גדלים) ואז צורבים עם `--ass-in`.

## פקודות

```bash
cd ~/my-business/_infra/reel_studio

# ריל בסגנון פייסבוק (clean) — קול אמיתי, B-roll, מוזיקה, חיתוכי-סצנה:
python3 make_reel.py --video clipA.mp4 clipB.mp4 clipC.mp4 --audio voice.mp3 \
  --layout fullbg --captions clean --music \
  --attribution "שם הדובר · תפקיד" --out reel.mp4

# סגנון kinetic עם PiP (כרטיס דובר מעוגל):
python3 make_reel.py --video talking_head.mp4 --audio talking_head.mp4 \
  --layout pip --captions kinetic --out quote.mp4

# קודם לכתוב כתוביות לעריכה, ואז לצרוב:
python3 make_reel.py --video clip.mp4 --audio voice.mp3 --ass-out cap.ass
#   ...עורכים את cap.ass...
python3 make_reel.py --video clip.mp4 --audio voice.mp3 --ass-in cap.ass --out reel.mp4

# קריינות ג'רוויס (TTS) — טקסט רגיל, הגייה דרך לקסיקון IPA, כתוביות מ-word boundaries:
python3 make_reel.py --video clip.mp4 --text narration_he.txt --rate 1.24 --music --out reel.mp4
```

דגלים: `--no-captions`, `--voice azure:avri`, `--music-vol 2.6`.
פלט מומלץ: `_infra/video_output/`.

## בניית kinetic מורכב (שורות נערמות)
ה-auto מייצר clean. ל-kinetic בונים cues מפורשים ב-Python וקוראים ל-`captions.build_ass(cues, preset="kinetic", ...)`. כל cue:
`{"start","end","text","style":"Hdr|Hdr2|Role|Big","y":1230,"chevron":True,"color":"gold","fade":[140,0]}`.
ראו דוגמה מלאה בתחתית `captions.py` (שחזור ציטוט לדוגמה).

## צבע/גודל = כרטיס שלם בלבד (חוק קריטי)
צביעה/הגדלה של **מילה בודדת באמצע שורה אסורה** — override באמצע run עברי מפצל את ה-bidi והופך סדר מילים. תמיד צובעים/מגדילים **כרטיס שלם** (`"color":"accent"`, `"size":96`, או `style:"Big"`). כרטיסי 2-4 מילים הופכים את זה לטבעי. ב-FB הכתוביות לבנות לגמרי — צבע הוא להדגשה נקודתית.

## גוצ'ות מוכחות (2026-06-22)
- **Spacing=0 חובה** — כל ריווח-אותיות חיובי הופך glyphs של RTL ב-libass. אסור לגעת בשדה ה-Spacing ב-styles.
- **פונט** — `Assistant ExtraBold` (מותגי, כבד, תואם FB) עובד **רק** עם Spacing=0. fallback בטוח: `Noto Sans Hebrew`. הותקנו ב-`~/.local/share/fonts/`.
- **בלי עטיפת RLE/PDF** — libass+fribidi מזהים עברית אוטומטית; עטיפה ידנית הופכת את הטקסט.
- **צבע inline בפורמט `&HBBGGRR&`** (עם & סוגר), לא פורמט ה-8-ספרות של ה-style — אחרת ה-tag נשבר.
- **הגייה (TTS)** — דרך לקסיקון IPA של ג'רוויס (`jarvis_briefing/lexicon.json`, /lexicon). **טקסט רגיל, לא ניקוד** (ראו החוק הקריטי למעלה). מילה שגויה → `<phoneme>` IPA חדש. באג שתוקן: `apply_lexicon` עבר ל-pass יחיד (regex) כדי שערכים חופפים (מייל⊂מיילים) לא ייצרו `<phoneme>` מקוננים. (`nikud.py`/Dicta = legacy, לא בשימוש.)

## Outro מטריקס + מוח J.A.R.V.I.S (`matrix_rain.py`)
ל-outro ממותג: `python3 matrix_rain.py /tmp/matrix.mp4 6` מייצר גשם-מטריקס ירוק (PIL, ספרות/סימנים — לא עברית, הפונט החד-רוחב חסר). מרכיבים מעליו את מסך המוח האמיתי (`jarvis_briefing/static/jarvis-neural-brain.mp4`, ה-NEURAL MAP) ב-**overlay ממורכז** (לא screen-blend — הרקע הכחלחל של המוח נותן גוון סגול). הגשם ממלא את הפסים למעלה/למטה. + כותרת drawtext J.A.R.V.I.S + מוזיקה מסונתזת (make_music) עם afade. מחברים לריל הראשי ב-`concat` filter. דוגמה מלאה: היסטוריית הריל של ג'רוויס 2026-06-22.

## אימות
תמיד לחלץ פריים אחרי הצריבה ולוודא RTL תקין (לא הפוך):
`ffmpeg -ss 2 -i reel.mp4 -frames:v 1 check.jpg` ואז לקרוא את התמונה.

## 🏆 מצב פרימיום (rollin-grade) — עדכון 2026-07-08
ארבע יכולות חדשות ב-make_reel.py (המפרט המלא: `_infra/reel_studio/producer_notes.md`):
1. **דיוק כתוביות:** `--ref-transcript ref.txt` — טקסט-האמת של הקטע (למשל מתמלול Timeless).
   משמש גם כ-whisper prompt וגם ליישור difflib שמתקן איות בלי לשבור סנכרון. **חובה כשיש תמלול.**
2. **מוזיקה:** `--music-style minimal` = פולס מודרני עדין (ברירת המחדל הנכונה לרילס מכירות/talking-head).
   `matrix` = הסינת' הדרמטי הישן (ג'רוויס). קבצים אמיתיים: לשים ב-`_infra/reel_studio/music/<style>/`.
3. **b-roll פרימיום:** `--insert card.png@12.5-15` (חוזר על עצמו) — כרטיס מלא-פריים עם זום-דחיפה,
   הקול ממשיך מתחת. את הכרטיסים בונים עם `broll_cards.py` (מספר-ענק/וואטסאפ/גרף/ציטוט ממותגים).
4. **מאסטר עוצמה:** compose מנרמל אוטומטית ל–14LUFS (רמת פיד).

### מבנה hook-first (חובה לרילס מפגישות)
משפט הפאנץ' הכי חזק = פתיחה, גם אם הוא מאמצע הקטע:
```bash
video.py trim src.mp4 hook.mp4 --start 00:12:31 --end 00:12:34     # משפט הפאנץ'
video.py trim src.mp4 body.mp4 --start 00:11:50 --end 00:12:31     # הקטע מההתחלה
printf "file 'hook.mp4'\nfile 'body.mp4'\n" > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -crf 20 -c:a aac combined.mp4
ffmpeg -i combined.mp4 -vn -c:a aac voice.m4a
make_reel.py --video combined.mp4 --audio voice.m4a --captions clean \
  --music --music-style minimal --ref-transcript ref.txt \
  --insert card1.png@14-17 --out reel.mp4
```
כללי קצב: אסור שוט סטטי >6ש; כרטיס b-roll כל 8-12ש (לא בתוך ההוק); 30-45ש סה"כ.

## 🥇 כתוביות-אחרונות + הבלטות word-sync (הדוקטרינה שהתגבשה ב-v8/v9, 2026-07)
**לרילס מדיבור אמיתי (לא TTS)** — הכיתוב נעשה על הסרטון הגמור, לא תוך כדי הרכבה:
1. מרכיבים את הווידאו **בלי כתוביות** (`--no-captions` / להשמיט את שלב הצריבה).
2. `caption_final.py FINAL.mp4 OUT.mp4` — מחלץ את האודיו הסופי, מתמלל עם ivrit-ai
   (ברירת מחדל `--mode transcribe`; ref רק לתיקון איות), וצורב. מה שנשמע = מה שכתוב.
3. **הבלטות במקום כרטיסי-טקסט:** `--highlight t1-t2` על 2-3 משפטי מפתח — סטאק שורות
   של 2 מילים שנבנה מילה-מילה ברגע האמירה: שורות בסיס לבנות (fs 88/100), שורת פאנץ'
   אחרונה גדולה (עד fs138) בזהב `#C9A227` (או `t1-t2:red` לאדום `#E5484D`), קונטור שחור
   כבד, פופ-כניסה עדין, סקרים שקוף-חלקית. הסגנון = רפרנס Hakol Podcast שדודו אישר.
   הכתוביות הרגילות מוסתרות שם אוטומטית. לעולם לא כחול.
4. `--avoid t1-t2` — הסתרת כתוביות בחלון של אינסרט גרפי עם טקסט (באנר/פוסטר).
5. `--break-after T` — קו-שבירה קשיח בין כרטיסים (כשצריך שכרטיס יסתיים בדיוק במילה).
6. איטרציות בלי תמלול חוזר: `--dump-words words.json` ← לתקן ידנית ← `--words-json words.json`.
7. אינסרט תמונה מומחש מאחורי הבלטה (למשל עץ-דולרים מאחורי "להצמיח את העץ") = שילוב מנצח:
   `apply_inserts` על המאסטר ללא-כתוביות, ואז caption_final עם ההבלטה על אותו חלון.
