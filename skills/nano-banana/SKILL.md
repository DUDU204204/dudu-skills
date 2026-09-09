---
name: nano-banana
description: יוצר תמונות דרך Gemini 2.5 Flash Image (Nano Banana) — המודל המתקדם של Google ליצירת תמונות. שימושי כשדודו אומר "תייצר תמונה", "צור תמונה של", "תמונה ל-X", "עיצוב ויזואל", "תמונה לפוסט/כתבה/דף נחיתה", "Nano Banana", "banana image", "generate image", "create image". תומך בפרומפטים בעברית ובאנגלית, יחסי רוחב שונים (1:1, 16:9, 9:16, 4:3 וכו'), ושומר מקומית ב-`_infra/nano_banana_output/`. 1024px, מהיר, באיכות גבוהה.
user-invocable: true
---

# Nano Banana — יצירת תמונות דרך Gemini 2.5 Flash Image

## מה זה עושה
מייצר תמונה מפרומפט טקסטואלי (עברית או אנגלית) דרך **Gemini 2.5 Flash Image** — המודל הרשמי של Google הידוע כ-"Nano Banana". GA, רזולוציה 1024px, מהיר מאוד.

## המודל
- **Model ID:** `gemini-2.5-flash-image`
- **Endpoint:** `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent`
- **API key:** נקרא אוטומטית מ-`~/.claude/settings.json` (שדה `mcpServers.gemini-transcription.env.GEMINI_API_KEY`)

## איך לקרוא לזה
הסקריפט הוא [`nano_banana.py`](nano_banana.py) באותה תיקייה.

```bash
python3 ~/.claude/skills/nano-banana/nano_banana.py "תיאור התמונה"
```

### דוגמאות
```bash
# ברירת מחדל — 1:1, שמירה אוטומטית ב-_infra/nano_banana_output/
python3 ~/.claude/skills/nano-banana/nano_banana.py "בננה עם משקפי שמש על רקע צהוב"

# יחס רוחב אחר
python3 ~/.claude/skills/nano-banana/nano_banana.py "hero image for landing page" --aspect 16:9

# פלט ספציפי
python3 ~/.claude/skills/nano-banana/nano_banana.py "logo" --out /tmp/logo.png --aspect 1:1

# לסטורי/ריל
python3 ~/.claude/skills/nano-banana/nano_banana.py "dramatic portrait" --aspect 9:16
```

## יחסי רוחב נתמכים
`1:1` (ברירת מחדל), `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`

## איפה הפלט נשמר
- **ברירת מחדל:** `~/workspaces/_infra/nano_banana_output/YYYY-MM-DD_HHMMSS_<slug>.png`
- **עם `--out`:** בדיוק בנתיב שניתן.

## מתי להשתמש בסקיל הזה
- תמונות לכתבות שיווקיות / פוסטים / ניוזלטרים
- Hero images לדפי נחיתה
- אילוסטרציות למוצרי מידע ופאנלים
- Mockups, concept art, ויזואלים מהירים
- כשדודו מבקש "תמונה של X" — בלי לשאול איזה כלי, פשוט להריץ את זה

## מתי *לא* להשתמש
- **עריכת תמונה קיימת** (image-to-image, inpainting) — Nano Banana תומך בזה אבל הסקריפט הנוכחי הוא text-to-image בלבד. אם דודו יבקש "שנה את התמונה הזאת ל-X" — לדווח שצריך להרחיב את הסקריפט.
- **תמונות עם טקסט בעברית בתוך התמונה** — Gemini לא מצטיין בטקסט בעברית בתוך התמונה. עדיף להוסיף את הטקסט בדיעבד (Canva, Photoshop).
- **לוגואים פרודקשן-רדי** — טוב לקונספט, פחות לגרסה סופית.

## טיפים לפרומפטים טובים
- **ספציפיות מנצחת כלליות:** "a ripe yellow banana wearing gold aviator sunglasses, studio photo, soft lighting, vibrant yellow background" עדיף על "banana with sunglasses".
- **סגנון:** ציין סגנון בבירור — `photorealistic`, `illustration`, `flat design`, `3d render`, `watercolor`, `cinematic`.
- **תאורה ומצלמה:** `soft diffused light`, `golden hour`, `studio lighting`, `wide angle`, `close-up`, `shallow depth of field`.
- **הקשר:** "for a landing page hero", "for Instagram story" — לפעמים עוזר.

## העלאה ל-Drive (אופציונלי)
אחרי יצירה, אפשר להעלות ל-Drive דרך הסקריפט הקיים:
```bash
python3 ~/workspaces/_infra/upload_to_drive.py <image_path> --folder-id <DRIVE_FOLDER_ID>
```
(ראו `reference_api_keys.md` בזיכרון — הסקריפט כבר יודע להתחבר.)

## מה הסקיל הזה לא עושה (כרגע)
- **עריכת תמונה קיימת** — להוסיף אם יצוץ צורך.
- **batch generation** (כמה תמונות בהרצה אחת) — אם יהיה מקרה שימוש, אוסיף `--count N`.
- **העלאה אוטומטית ל-Drive** — כרגע ידני, אבל קל להוסיף.

## עלות
Gemini 2.5 Flash Image נמצא במחיר זול לתמונה (סדר גודל של $0.04 לתמונה, נכון ל-2026). לשימוש רגיל — זניח.
