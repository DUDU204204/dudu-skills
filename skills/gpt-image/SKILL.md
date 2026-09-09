---
name: gpt-image
description: יוצר תמונות דרך GPT-Image-2 (OpenAI) — המודל החדש (השיק 2026-04-21, מבוסס GPT-5.4), המוביל בעולם ב-3 דברים: (1) רנדור טקסט בתוך תמונה כולל עברית (~99% דיוק תווים), (2) prompt adherence מורכב עם הרבה אלמנטים, (3) פוטוריאליזם של אנשים/פרצופים. תומך עד 4K (3840×2160), פי 2 מהיר מקודמו. שימושי כשדודו אומר "תייצר תמונה ב-GPT", "GPT image", "תמונה עם טקסט בעברית", "תמונה עם הרבה דיוק", "infographic", "פוסטר", "תמונה פוטוריאליסטית של אדם". יחסי רוחב 1:1/3:2/2:3/16:9/9:16, איכות low/medium/high/auto, ושומר ב-`_infra/nano_banana_output/`. **שונה מ-nano-banana** — איטי יותר (15-40 שניות), יקר יותר, אבל הרבה יותר חזק בטקסט ובסצנות מורכבות.
user-invocable: true
---

# GPT-Image-2 — יצירת תמונות דרך OpenAI

## מה זה עושה
מייצר תמונה מפרומפט טקסטואלי (עברית או אנגלית) דרך **GPT-Image-2** — הדגל החדש של OpenAI ליצירת תמונות (השיק 2026-04-21, מחליף את gpt-image-1 ואת DALL-E 3).

## המודל
- **Model ID:** `gpt-image-2`
- **Snapshot:** `gpt-image-2-2026-04-21`
- **Backbone:** GPT-5.4 — שימוש בצינור reasoning של ChatGPT לפני יצירה (חושב על הפרומפט, מתקן את עצמו)
- **Endpoint:** `https://api.openai.com/v1/images/generations`
- **רזולוציה מקסימלית:** 3840×2160 (4K)
- **API key:** נקרא אוטומטית מ-`~/workspaces/_infra/telegram-agent/.env` (אותו key של Whisper לתמלול)

## איך לקרוא לזה
הסקריפט הוא [`gpt_image.py`](gpt_image.py) באותה תיקייה.

```bash
python3 ~/.claude/skills/gpt-image/gpt_image.py "תיאור התמונה"
```

### דוגמאות
```bash
# ברירת מחדל — 1:1, איכות high, שמירה אוטומטית
python3 ~/.claude/skills/gpt-image/gpt_image.py "פוסטר בעברית עם הכותרת 'שם המותג'"

# יחס רוחב 16:9 ל-hero
python3 ~/.claude/skills/gpt-image/gpt_image.py "infographic explaining sales funnel" --aspect 16:9

# 4K לדפוס / hero ענק
python3 ~/.claude/skills/gpt-image/gpt_image.py "editorial poster" --aspect 16:9 --4k

# איכות נמוכה (זול ומהיר) לדראפט
python3 ~/.claude/skills/gpt-image/gpt_image.py "concept sketch" --quality low

# פלט ספציפי
python3 ~/.claude/skills/gpt-image/gpt_image.py "logo concept" --out /tmp/logo.png
```

## ארגומנטים
- `--aspect` — `1:1` (default) | `3:2` | `2:3` | `16:9` | `9:16`
- `--size` — override ישיר (כל גודל חוקי, כפולות של 16, קצה ארוך ≤3840)
- `--quality` — `low` | `medium` | `high` (default) | `auto`
- `--4k` — מוציא ברזולוציה הגבוהה ביותר התואמת ל-aspect (לדפוס/print-ready)
- `--out` — נתיב פלט מלא (אחרת נשמר ב-`~/workspaces/_infra/nano_banana_output/`)

## עלות (משוערת)
| Quality | מחיר משוער לתמונה |
|---------|---------------------|
| `low`   | ~$0.01-0.03 |
| `medium`| ~$0.04-0.07 |
| `high`  | ~$0.10-0.19 |
| `4K`    | תוספת על quality |

**חשוב:** ה-API נפרד לחלוטין ממנוי ChatGPT Plus/Pro. כל תמונה מחויבת מהארנק של platform.openai.com.

## מה חדש ב-gpt-image-2 מול gpt-image-1
- **רנדור טקסט** — ~99% דיוק תווים בלטינית, CJK, הינדי, בנגלית (gpt-image-1 היה ~85-90%)
- **רזולוציה** — עד 4K (3840×2160), gpt-image-1 הגיע ל-1536×1024
- **מהירות** — פי 2 מהיר
- **Reasoning** — חושב על הפרומפט לפני יצירה, יכול לחפש רפרנסים, ומבצע self-check
- **n** — תומך ב-1-8 תמונות בקריאה אחת (היה 1 בלבד)
- **לא תומך** ב-`background: "transparent"` (gpt-image-1 כן)

## מתי להשתמש בסקיל הזה (ולא ב-nano-banana)

### GPT-Image **מנצח** ב:
- **טקסט בתוך תמונה** — עברית, לוגואים, infographics, פוסטרים, תפריטים
- **Prompt adherence** — סצנות עם 5+ אלמנטים ויחסים מרחביים
- **פוטוריאליזם של אנשים** — פרצופים, ידיים, פרופורציות
- **תמונות מוצר עם פירוט** — packaging, mockups עם טקסט אמיתי
- **דפוס / print-ready** — 4K מספיק ל-A3+

### Nano-Banana **מנצח** ב:
- **מהירות** — ~3 שניות מול 15-40
- **עלות** — $0.04 קבוע
- **עריכה איטרטיבית** — שמירת קומפוזיציה בין שינויים
- **Character consistency** על פני מספר תמונות
- **ויזואלים מהירים** לפוסטים יומיים

### כלל אצבע
- כתבה / דף נחיתה עם טקסט בעברית בתוך התמונה → **GPT-Image-2**
- תמונת מוצר פוטוריאליסטית → **GPT-Image-2**
- Infographic / מדריך ויזואלי → **GPT-Image-2**
- חומר דפוס (כרזה, פלייר, A3+) → **GPT-Image-2 --4k**
- ויזואל מהיר לפוסט / סטורי → **Nano-Banana**
- איטרציות על אותה תמונה → **Nano-Banana**

## מתי *לא* להשתמש
- **עריכת תמונה קיימת** — הסקריפט הנוכחי הוא text-to-image בלבד. אם דודו ירצה image-to-image, צריך להרחיב לקריאה ל-`/v1/images/edits`.
- **תמונות בכמויות** (10+ תמונות באותה הרצה) — זה יקר. לדראפטים מסיביים, להשתמש ב-`--quality low` או ב-nano-banana.
- **לוגו פרודקשן-רדי** — טוב לקונספט, פחות לגרסה סופית.
- **רקע שקוף** — gpt-image-2 לא תומך. אם צריך — gpt-image-1 או nano-banana.

## טיפים לפרומפטים
- **ספציפיות** — "פוסטר A4 על רקע כחול נייבי, כותרת בעברית 'שם המותג' בגופן בולט בלבן באמצע, סאב-טייטל קטן יותר 'תת-כותרת'" עדיף על "פוסטר ליזמי החופש".
- **מיקום טקסט** — אפשר לציין במפורש: "title at top center", "subtitle below in smaller font".
- **סגנון** — `editorial photography`, `flat illustration`, `3D render`, `cinematic`, `studio product shot`.
- **שפת הטקסט בתמונה** — לכתוב בעברית את הטקסט המדויק שצריך להופיע, בתוך הפרומפט באנגלית. למשל: `Hebrew text "יזמי החופש" at the top`.

## העלאה ל-Drive (אופציונלי)
```bash
python3 ~/workspaces/_infra/upload_to_drive.py <image_path> --folder-id <DRIVE_FOLDER_ID>
```

## מה הסקיל לא עושה (כרגע)
- **עריכת תמונה קיימת** (image-to-image, inpainting, outpainting) — להרחיב לפי צורך.
- **batch generation** — אם יצוץ צורך, אוסיף `--count N` (gpt-image-2 תומך עד 8).
- **העלאה אוטומטית ל-Drive** — ידני כרגע.
- **streaming של partial images** — אפשר להוסיף לפי צורך.
