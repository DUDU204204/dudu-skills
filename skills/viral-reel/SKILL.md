---
name: viral-reel
description: מפיק ריל מכירתי/תוכן ויראלי 9:16 בעברית מקצה-לקצה לפי מודל 2026 — קריינות (TTS), רקע תמונה עם Ken Burns, כתוביות קינטיות, hook title-card, פס-דופק (waveform) שמגיב לקול, וכרטיסי b-roll ממותגים שממחישים את הטקסט (וואטסאפ, גרף, מספר ענק, תקרת זכוכית). שימושי כשדודו אומר "תפיק ריל תוכן", "ריל שיווקי עם הוק", "תהפוך את התובנה הזו לריל", "סרטון מכירתי לסושיאל", "viral reel". שונה מ-reel-captions (שמכתב קליפ/קול-אדם קיים) — כאן בונים ריל שלם מסקריפט + תמונות.
user-invocable: true
---

# Viral Reel — ריל מכירתי 9:16 מקצה-לקצה (Reel Studio VO)

מפיק ריל תוכן/מכירה בעברית מ**סקריפט + תמונות**, לפי מודל הרילים הוויראליים של 2026.
משלים את `reel-captions` (שמכתב קליפ וידאו עם קול-אדם אמיתי). כאן אין צילום של דובר —
בונים ריל "טקסט-על-מסך" חי: קריינות, רקע-תמונה בתנועה, כתוביות קינטיות, פס-דופק, וכרטיסי b-roll.

הכלי חי ב-`~/my-business/_infra/reel_studio/`:
- **`reel_vo.py`** — האורקסטרטור החדש (image/VO). TTS → רקע Ken Burns + scrim → waveform → כתוביות → מיקס → צריבה.
- **`broll_cards.py`** — מחולל כרטיסי b-roll ממותגים (PIL+raqm RTL): מספר-ענק, גרף, וואטסאפ, תקרת-זכוכית, רכבת-הרים, ציטוט, plaque "מצטיין החודש".
- מנועים שמשתמשים בהם מ-reel-captions: `azure_tts.py` (קול avri + word-boundaries), `captions.py` (ASS).

דוגמה עובדת מלאה: תיקיית `projects/<שם-הפרויקט>/` עם ה-JSON, הנכסים והפלט.

---

## ⭐ המודל (2026, מתוך מחקר — ראה גם הערות אמינות בסוף)

**קנבס 1080×1920, 30fps, 30–45ש, RTL. הקריינות front-loaded, ההוק חייב לעצור גלילה ב-1–3ש.**

### Beat sheet (ריל ~38–44ש)
| ביט | זמן | מה | ויזואל |
|---|---|---|---|
| **HOOK** | 0–3ש | המשפט הכי מפתיע + hook title-card 5–8 מילים (96–112px, שליש עליון) + open loop | פנים/דובר זום-אין |
| **Stakes** | 3–8ש | מציב את הכאב | פנים אחר / כרטיס |
| **Body micro-doses** | 8–28ש | תובנה במנות, cutaway **כל 3–5ש** שממחיש את הנאמר | כרטיסים + פנים לסירוגין |
| **Payoff** | 28–38ש | סוגר את ה-open loop | פנים, ישיר |
| **CTA רך + loop-back** | 38–44ש | "עקוב, חלק 2 בדרך" / keyword-trigger. משפט שמתחבר חזרה להוק | פנים |

### Hook patterns (בחר אחד)
contrarian ("השקר הכי גדול ב..."), loss-aversion ("תפסיק ל... אם אתה רוצה..."), confessional ("3 שנים הייתי תקוע, ככה יצאתי"), "הטעות מס' 1 ש...", curiosity-gap **ספציפי** (לא "סודות הצלחה"), open-loop number ("3 דברים, השלישי הפתיע"). ספציפי > רחב. אנושי > מצוחצח.

### Layer stack (z מלמטה למעלה)
`z0` רקע Ken Burns (zoom 3–6% / 4–6ש) · `z1` grade ריאליסטי (בלי teal) · `z2` כרטיסי b-roll · `z3` scrim גרדיאנט עליון+תחתון · `z4` **waveform pulse — accent דק בלבד** (~70% opacity, מתחת לכתוביות, מגיב ל-RMS של הקול) · `z5` כתוביות קינטיות (lower-middle third, y≈1480) · `z6` hook title-card (0–3ש, שליש עליון).

### חוקי כתוביות
לבן Assistant ExtraBold + הילת-צל, כרטיסי 2–4 מילים, **מילת-מפתח אחת** בצבע-מותג (accent), sync למילה. בלי ניקוד, בלי לפצל ביטוי. גודל גוף ~86px, hook ~104–112px.

### קצב / אודיו / CTA
שינוי ויזואלי כל 1.5–2ש, חיתוך כל 2–4ש (clean, לא hyper). מוזיקה underscore נמוכה ומדאקת, whoosh עדין רק על מעברים גדולים. CTA רך + loop-back (לא hard-sell).

### ⚠️ על ה-waveform (כן את זה ביקש דודו — אבל במשורה)
ה-waveform/pulse הוא קונבנציה של **audiogram**, לא של talking-head. לכן כאן הוא **accent דק** בתחתית שמגיב ל-RMS של הקול, לא הגיבור. דק, צבע-מותג, נמוך. (אם רוצים אותו בולט — זו החלטה אסתטית מודעת, לא best-practice.)

---

## זרימת עבודה (4 צעדים)

```bash
cd ~/my-business/_infra/reel_studio
P=projects/<name>

# 1) סקריפט — כתוב את הקריינות. כלל זהב: מספרים שנאמרים = מילים ("שמונת אלפים"),
#    כי הכתוביות נבנות מהמילים המדוברות. מספרים ויזואליים (8,000 ₪) הולכים לכרטיסים.
$EDITOR $P/scripts/reelX.txt

# 2) Synth — TTS + הדפסת משך ותזמוני-מילים מדויקים (לפי זה מתזמנים סצנות)
python3 reel_vo.py $P/reelX.json --synth    # rate ~1.2 ≈ קצב ריל אנרגטי; יעד 38–44ש

# 3) כרטיסי b-roll — הוסף/ערוך פונקציית reelX() ב-broll_cards.py, ואז:
python3 broll_cards.py reelX $P/broll

# 4) Render — אחרי שמילאת scenes[] עם זמנים מה-synth (חיתוך כל 2–5ש)
python3 reel_vo.py $P/reelX.json --render
# פלט: $P/out/<name>.mp4
```

### מבנה ה-spec (`reelX.json`)
```json
{
  "name": "...", "script": "scripts/reelX.txt", "voice_out": "reelX_voice.mp3",
  "rate": 1.2,
  "hook": {"text": "ההוק", "until": 2.7, "y": 560, "size": 112},
  "accent_keywords": ["מילה1","מילה2"],
  "caption_y": 1490, "waveform": true, "music": true, "whoosh": true,
  "scenes": [
    {"src":"assets/face.png","focus":[0.50,0.40],"zoom":"in","dark":0.66,"start":0.0,"end":3.96},
    {"img":"broll/card.jpg","zoom":"in","start":3.96,"end":7.5}
  ]
}
```
- **scene photo:** `src` + `focus`[fx,fy] (נקודת-מיקוד בתמונת-המקור, נשמרת ממורכזת תחת הזום) + `zoom` in/out/none + `dark` (0.55–0.7).
- **scene card:** `img` (PNG 1080×1920 מ-broll_cards).
- חיתוך כל 2–5ש, לסירוגין פנים/כרטיס. הסצנה האחרונה נחתכת אוטומטית למשך הקריינות.

---

## כרטיסי b-roll (`broll_cards.py`)
פונקציות מוכנות: `card_big_number` (מספר-ענק + strike), `card_stamp`, `card_graph` (גרף עמודות עם פסגה), `card_whatsapp` (טלפון + בועות), `card_ceiling` (תקרת-זכוכית), `card_zigzag` (רכבת-הרים), `card_quote` (משפט ממורכז + שורת-accent), `card_plaque` ("מצטיין החודש" סביב תמונה אמיתית).
מוסיפים reel חדש כפונקציית `reelX(dir)` שקוראת להן. פלטה: navy כהה, accent כחול `#3DB3F2`, gold `#F2B33D`, danger `#FF5A5F`.

---

## גוצ'ות מוכחות (חובה)
- **פונט מספרים בכרטיסים:** Assistant/Noto-Hebrew הם **תת-קבוצה עברית בלי ספרות/פיסוק לטיני** → ספרות יוצאות ריבועים. `broll_cards.num()` משתמש ב-**DejaVuSans-Bold** לכל מספר/שעה. טקסט עברי בכרטיס — בלי `. , ? !` (אין להם glyph ב-Assistant). הכתוביות בסרטון בסדר (libass עושה fallback) — אבל גם שם עדיף מספרים-כמילים.
- **rate ~1.2** — קריינות ב-1.0 ארוכה מדי; 1.2 ≈ קצב ריל. אם >45ש — לקצץ סקריפט.
- **focus-locked Ken Burns** — `fill_cover` ממרכז את נקודת-המיקוד לפני הזום, אחרת פנים נשמטות מהפריים בזום-לראשית. אם פנים נחתכות — לכוון `focus`.
- **waveform = WAV** — showwaves על MP3 נתקע; reel_vo ממיר קודם ל-WAV.
- **אימות תמיד** — לחלץ 4–6 פריימים מהפלט ולוודא RTL/מיקוד/קריאות (`ffmpeg -ss T -i out.mp4 -frames:v 1 f.jpg`).
- **הקול הוא קריינות TTS, לא הדובר עצמו.** לרילים שבהם אתה מדבר באמת — מצלמים ומשתמשים ב-`reel-captions`. כאן זה reels טקסט-על-מסך עם הפנים שלו כעוגן.

## אמינות הראיות (מהמחקר)
חזק: חלון hook 1–3ש, אורך 30–45ש, כתוביות word-by-word לבן+stroke, cut כל 2–4ש, pattern-interrupt כל 3–5ש, grade בלי teal, CTA רך ממיר. בינוני/דעה: ה-waveform כ-accent (קונבנציית audiogram), ספי-px מדויקים, "+85% watch-time" מ-pattern interrupts (claim שיווקי).

## 🏆 עדכון פרימיום 2026-07-08
- מוזיקה: ל-reel מכירתי/talking-head השתמש ב-`--music-style minimal` (make_reel) או ספריית
  `_infra/reel_studio/music/`. ה-matrix הדרמטי נשמר לתוכן אפי בלבד.
- מאסטר -14LUFS אוטומטי ב-compose.
- מפרט הקצב/כתוביות/b-roll שנמדד מרפרנסים שנמדדו: `_infra/reel_studio/producer_notes.md`.

## 🥇 עדכון 2026-07-09 — הבלטות word-sync (לרילס מדיבור אמיתי)
כשהחומר הוא דיבור מוקלט (לא TTS): רנדר בלי כתוביות → `caption_final.py` (תמלול ivrit-ai
של האודיו הסופי) עם `--highlight t1-t2` על 2-3 משפטי המפתח — סטאק מילה-מילה בסגנון
פרימיום (בסיס לבן, פאנץ' זהב/אדום ענק, קונטור שחור, פופ). אין כרטיסי-טקסט מתחרים
בכתוביות. הדוקטרינה המלאה בסקיל `reel-captions` וב-producer_notes.md.
