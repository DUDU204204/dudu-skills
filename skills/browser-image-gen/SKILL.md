---
name: browser-image-gen
description: יצירת תמונות דרך ChatGPT Plus או Gemini Pro של דודו, באמצעות שליטה ב-Chrome הקיים (CDP). שימושי כשרוצים איכות גבוהה מהאיכות של ה-API, או להימנע מחיוב נוסף (כל יצירה על המנוי הקיים). תומך בעברית RTL. כלל אצבע — ChatGPT לטקסט בעברית/אנגלית בתוך תמונה, Gemini Nano Banana 2 לסגנונות אומנותיים וסצנות מורכבות.
---

# Browser Image Generation — ChatGPT + Gemini

## מתי להשתמש
- דודו אומר "תייצר תמונה דרך הדפדפן" / "דרך ChatGPT" / "דרך Gemini" / "דרך המנוי שלי"
- צריך איכות גבוהה יותר ממה שה-API מוציא
- רוצים להימנע מחיוב לארנק OpenAI (כל קריאת gpt-image-2 דרך API עולה)
- צריך לעבוד עם סגנון ספציפי שעובד יותר טוב באחד המנועים

## כלל אצבע: איזה מנוע בוחרים

| משימה | מנוע |
|--------|------|
| טקסט בעברית בתוך תמונה (אינפוגרפיקה, פוסטר, באנר) | **ChatGPT** |
| פוטוריאליזם / פרצופים | **ChatGPT** |
| סגנון אומנותי/קונספטואלי (HUD, איירון מן, ויקטוריאני…) | **Gemini (Nano Banana 2)** |
| סצנות עם הרבה אלמנטים ויחסים מרחביים | **שניהם — בדוק** |
| עריכת תמונה קיימת | **Gemini** (יש לו edit מעולה) |

## פרומפט — סגנון תמיד נכלל
דודו זיהה שבלי הגדרת סגנון התוצאה דומה לברירת המחדל. **תמיד לכלול בפרומפט הפניה לסגנון ויזואלי** — "JARVIS HUD מאיירון מן", "editorial poster", "isometric illustration", "Wes Anderson palette", "cyberpunk neon", "flat 2D infographic", וכו'.

## הזרימה (ChatGPT)

```python
# 1. פתיחת tab חדש (לא דורסים tab קיים של דודו!)
new_tab("https://chatgpt.com/")
wait_for_load()

# 2. צילום מסך לוידוא — לוודא שמחובר ("David Nahum / Plus" בפינה תחתונה שמאלית)
capture_screenshot("/tmp/chatgpt_check.png")

# 3. קליק על תיבת הקלט (לרוב ~y=355 במרכז)
click_at_xy(820, 355)

# 4. הקלדת פרומפט עם הוראה ברורה ליצור תמונה + סגנון
type_text("צור תמונה בסגנון X של ...")

# 5. שליחה — קליק על כפתור send (החץ הכחול)
# הכפתור בערך ב-(1177, 580) אחרי שהפרומפט הוקלד
click_at_xy(1177, 580)

# 6. המתנה — ChatGPT עובד 60-120 שניות (reasoning + generation)
time.sleep(60)
# צילום מסך לבדיקה. אם רואים "Thinking" / "Generating" — עוד דקה.

# 7. חילוץ URL של התמונה מה-DOM
urls = js("""
  return Array.from(document.querySelectorAll('img'))
    .map(img => ({src: img.src, w: img.naturalWidth, h: img.naturalHeight, alt: img.alt}))
    .filter(o => o.w > 400 && o.alt && o.alt.includes('Generated'));
""")
# התמונה תהיה ב-backend-api/estuary/content URL

# 8. הורדה דרך session cookies (חובה — לא ניתן לקרוא ל-curl/wget)
result = js(f"""
  return fetch({url!r}).then(r => r.blob()).then(blob =>
    new Promise(res => {{
      const r = new FileReader();
      r.onloadend = () => res({{type: blob.type, size: blob.size, b64: r.result.split(',')[1]}});
      r.readAsDataURL(blob);
    }})
  );
""")
data = base64.b64decode(result["b64"])
# שמירה ל-~/my-business/_media/generated/
```

## הזרימה (ChatGPT על ה-VPS — CDP גולמי, אומת 2026-07-28)

על ה-VPS אין browser-harness — עובדים ישירות מול הכרום המקומי (`127.0.0.1:9222`) עם
**`cdp_gpt.py` שנמצא כאן בתיקיית הסקיל** (צנרת websocket ללא תלויות, הועתקה מ-ypay.py):

```python
import sys; sys.path.insert(0, "~/.claude/skills/browser-image-gen")
from cdp_gpt import CDP, find_tab, open_tab
tab = find_tab("about:blank") or open_tab("about:blank")
c = CDP(tab)
c.cmd("Page.navigate", {"url": "https://chatgpt.com/"}); c.front()
```

השלבים שעבדו מקצה-לקצה (דוגמה: סטיילינג תמונת מוצר):
1. **Cloudflare Turnstile** ("רק רגע...") — נפתר בקליק `Input.dispatchMouseEvent` על
   קואורדינטות ה-checkbox (קליק ברמת compositor; קליק JS על האלמנט לא עובד).
2. **צירוף תמונת רפרנס** — `c.upload('input[type=file]', path)` (`DOM.setFileInputFiles`;
   יש 3 inputs בדף, הראשון עובד). כלומר **image-to-image דרך הדפדפן עובד ב-ChatGPT**.
3. פוקוס על `#prompt-textarea` + `Input.insertText` → קליק `[data-testid="send-button"]` →
   ~2 דקות → חילוץ ה-img מה-DOM והורדה עם fetch מתוך הדף (estuary URL דורש cookies, כרגיל).
4. **"Something went wrong" + Retry בצ'אט ≠ כישלון** — התמונה לפעמים כן נוצרה; לבדוק img
   ב-DOM לפני שמריצים סבב חוזר.

### 🔤 המתכון לעברית מושלמת בתוך תמונה
כשצריך טקסט עברי מדויק אות-באות (סימניות, פוסטרים, חומרי לימוד):
**להעלות את הנכס הקיים כתמונת רפרנס (image-to-image) + לכלול בפרומפט את רשימת הטקסטים
המדויקת, שורה-שורה.** בלי רפרנס ChatGPT משבש/ממציא אותיות. אחרי היצירה — **לאמת בחיתוכי
זום (crop) על כל אזור טקסט** לפני מסירה, לא להסתפק במבט על התמונה המלאה.

## הזרימה (Gemini)

```python
# 1. URL חובה ל-u/1 — שם יושב המנוי הפרו של you@example-business.co.il
new_tab("https://gemini.google.com/u/1/app")
wait_for_load()

# 2. צילום מסך לוודא "Pro" + שם המשתמש בפינה התחתונה
#   ⚠️ אם u/1 לא נכון (נדיר — קורה אחרי disconnect/reconnect), לנסות u/0 או u/2

# 3. קליק על תיבת הקלט (~y=390 במרכז)
click_at_xy(550, 390)

# 4. הקלדה — Gemini מבין עברית מצוין
type_text(prompt)

# 5. שליחה — כפתור send לפעמים לא נמצא ב-aria-label. ה-fallback האמין:
js("""
  const ta = document.querySelector('rich-textarea div[contenteditable="true"]')
          || document.querySelector('[contenteditable="true"]');
  ta.focus();
  ta.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', code:'Enter', which:13, keyCode:13, bubbles:true}));
""")

# 6. המתנה — Gemini Nano Banana 2 מהיר יותר (~30-45 שניות)
time.sleep(40)

# 7. חילוץ — התמונה ב-Gemini היא **blob: URL**, לא URL רגיל
img_info = js("""
  return Array.from(document.querySelectorAll('img'))
    .filter(i => i.src.startsWith('blob:') && i.naturalWidth > 400)
    .map(i => ({src: i.src, w: i.naturalWidth, h: i.naturalHeight}))[0];
""")

# 8. הורדה — fetch על blob: URL נכשל ב-Gemini (CORS). השתמש ב-CANVAS:
result = js("""
  const img = Array.from(document.querySelectorAll('img'))
    .find(i => i.src.startsWith('blob:') && i.naturalWidth > 400);
  const canvas = document.createElement('canvas');
  canvas.width = img.naturalWidth;
  canvas.height = img.naturalHeight;
  canvas.getContext('2d').drawImage(img, 0, 0);
  return {b64: canvas.toDataURL('image/png').split(',')[1]};
""")
data = base64.b64decode(result["b64"])
```

## Gotchas נצבעו בדם

0. **חובה להביא את הטאב לחזית (`Page.bringToFront`) לפני שליחה ובזמן ההמתנה!** נתגלה 2026-07-08:
   Gemini (וכנראה גם ChatGPT לפעמים) לא מזרים תשובה לטאב ברקע — הבקשה נשלחת וה"..." נתקע לנצח.
   טאב בחזית → תשובה תוך שניות. זו הייתה הסיבה לכל ה"Gemini לא מגיב" של אותו יום.

1. **לעולם `new_tab`, אף פעם לא `goto_url`** — Chrome שלו פתוח על עבודה. `goto_url` ידרוס. `new_tab` פותח טאב חדש לצדדים.
2. **`Run as a promise`** — בקריאות `js(...)` עם `await` ברמה העליונה — לא נתמך. להחליף ב-`.then()` chain (ראה דוגמאות).
3. **ChatGPT image URL** מגיע מ-`backend-api/estuary/content` עם signed URL. דורש cookies של הסשן הנוכחי — לכן fetch מתוך הדפדפן, לא curl.
4. **Gemini image URL** הוא תמיד `blob:` (יצירה לוקאלית). `fetch` עליו עלול להיכשל ב-CORS — להשתמש ב-canvas+`toDataURL`.
5. **u/1** — דודו מחזיק כמה חשבונות גוגל בכרום. Pro של `you@example-business.co.il` יושב על `u/1` לרוב. ראה [[gemini-account-u1]].
6. **המתנה מספיקה** — ChatGPT עם reasoning יכול לקחת 2 דקות. אל תתייאש מהר. מסך עם "Thinking" + ספינר = עדיין עובד.
7. **שמירה תמיד ל-** `~/my-business/_media/generated/` עם שם `YYYY-MM-DD_<source>_<topic>.png`.

## מה הסקיל לא עושה (כרגע)
- **אין אוטומציה אמיתית של "צור N תמונות שונות באותו פרומפט"** — דורש לוגיקה של regenerate
- ~~אין image-to-image~~ — **ב-ChatGPT עובד** (ראה זרימת ה-VPS: `DOM.setFileInputFiles`). ב-Gemini טרם מומש
- **שביר ל-UI changes** — אם OpenAI/Google משנים את הממשק, נשבר עד שמתקנים

## קישורים
- [[browser-harness]] — הסקיל הבסיסי לשליטה ב-Chrome
- [[gemini-account-u1]] — חשבון Pro של דודו
- [[api-keys]] — מפתחות API חלופיים אם רוצים API ישיר
