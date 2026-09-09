---
name: transcribe
description: מתמלל קובץ אודיו/וידאו לעברית דרך המודל המקומי ivrit-ai/whisper-large-v3-turbo-ct2 (faster-whisper). שימושי כשדודו אומר "תמלל את הקובץ", "תמלול להקלטה", "תוציא לי טקסט מההקלטה", או כשסקיל אחר צריך תמלול (ניוזלטר, פאנלים, ראיונות). חינם, רץ מקומית, עברית מצוינת, לא יוצא החוצה.
user-invocable: true
---

# Transcribe — תמלול מקומי בעברית

## מה זה עושה
ממיר קובץ אודיו/וידאו (`ogg`, `opus`, `mp3`, `m4a`, `wav`, `mp4`, וכו') לטקסט בעברית. רץ מקומית על CPU של ה-Mac, בלי לשלוח שום דבר החוצה.

## איפה להריץ — מק (עיקרי) או VPS (גיבוי)
- **מק (עיקרי, מהיר יותר):** i7 12-threads. `python3` הגלובלי עם faster-whisper מותקן. לקבצים ארוכים (30+ דק') — תמיד המק אם הוא דלוק (`mac ping`).
- **VPS (גיבוי, מ-2026-08-12):** venv ייעודי — `~/.venvs/transcribe/bin/python`. 4 ליבות בלבד (איטי יותר, ~זמן אמת) וחולק CPU עם כל השירותים — מתאים לקבצים קצרים או כשהמק לא זמין:
  ```bash
  ~/.venvs/transcribe/bin/python ~/.claude/skills/transcribe/transcribe.py <file> --out /tmp/t.txt
  ```
  המודל כבר ב-cache על שתי המכונות (`_infra/ivrit-ai-model/`). אומת חי על ה-VPS (ctranslate2 4.8.1, Python 3.14).

## המודל
- **Repo:** `ivrit-ai/whisper-large-v3-turbo-ct2` (Whisper turbo שעבר fine-tune על עברית)
- **Cache:** `~/my-business/_infra/ivrit-ai-model/` (כבר מורד)
- **Runtime:** `faster-whisper` (CTranslate2) — מותקן גלובלית ב-Python 3.9

## איך לקרוא לזה
הסקריפט הוא [`transcribe.py`](transcribe.py) באותה תיקייה.

```bash
python3 ~/.claude/skills/transcribe/transcribe.py <audio_path> [--out text.txt] [--srt subs.srt] [--json segments.json]
```

- מדפיס את הטקסט המלא ל-stdout (מוכן ל-pipe/capture).
- לוג התקדמות יוצא ל-stderr (`--quiet` כדי לשתק).
- ברירות מחדל: `language=he`, `compute_type=int8`, `vad_filter=True`, `beam_size=5`.

## דפוס שימוש סטנדרטי
```bash
TRANSCRIPT=$(python3 ~/.claude/skills/transcribe/transcribe.py "/path/to/file.ogg" --quiet)
```
לקבצים ארוכים (מעל 10 דקות): שמור לקובץ במקום `$()` כדי להימנע מ-buffer גדול:
```bash
python3 ~/.claude/skills/transcribe/transcribe.py "/path/to/file.mp3" --out /tmp/transcript.txt
```

## ביצועים (על ה-Mac הזה, CPU בלבד)
- טעינת מודל ראשונה בסשן: ~7 שניות.
- תמלול: פי ~2-3 מהר מזמן אמת (10 דקות אודיו ≈ 3-5 דקות תמלול).
- אם רוצים לראות התקדמות בזמן אמת, לא להשתמש ב-`--quiet`.

## מתי להשתמש בזה במקום OpenAI API
**תמיד**, עבור:
- הקלטות של לקוחות (פרטיות)
- עברית (המודל הזה מדויק יותר מ-`whisper-1` של OpenAI לעברית)
- קבצים ארוכים (אין מגבלת 25MB)

**Fallback ל-OpenAI Whisper API** רק אם:
- ה-Mac לא זמין / הסקריפט נכשל
- צריך תמלול מהיר מאוד ואין זמן למודל מקומי לעלות

## סקילים שקוראים לזה
- סקיל הניוזלטר שלך — תמלול הקלטת וואטסאפ

## התמודדות עם מצבי קצה

### הקובץ לא קיים
הסקריפט יוצא עם `exit 2` והודעת שגיאה ל-stderr. בדוק את הנתיב.

### התמלול ריק
בדרך כלל אומר שההקלטה ריקה/שקטה. הרץ בלי `--quiet` כדי לראות אם ה-VAD סינן הכל. אפשר להוריד `vad_filter` ידנית על ידי עריכת הסקריפט.

### הקלטה ארוכה מאוד (מעל שעה)
עדיין יעבוד, אבל יקח זמן. שקול `--compute-type int8_float16` (אם המכונה תומכת) או פשוט להריץ ברקע ולחזור.

### המודל לא נטען
אם משנים את ה-cache, ודא ש-`HF_HOME=~/my-business/_infra/ivrit-ai-model` — הסקריפט מגדיר את זה אוטומטית.

## מה הסקיל הזה לא עושה
- לא עושה diarization (מי אמר מה). faster-whisper לא תומך בזה מהקופסה.
- לא מתרגם. פלט תמיד בשפת המקור (ברירת מחדל: עברית).
- לא מנקה/מעבד את הטקסט (סימני פיסוק, פסקאות) — זה תפקיד של שלב הכתיבה אחרי.
