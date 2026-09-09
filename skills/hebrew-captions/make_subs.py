#!/usr/bin/env python3
"""מחולל כתוביות ASS לשיעור ערוך — סגנון רילס: קלפים קצרים, RTL תקין, בלי צל.

לקחים (2026-07-16, מהרילסים):
- Spacing=0 חובה (ריווח-אותיות חיובי הופך RTL ב-libass).
- RTL: קלפים קצרים בעברית + Spacing=0 + fribidi אוטומטי = פיסוק תקין. בלי עטיפת RLE/PDF.
- בלי צל (Shadow=0). הילת-בורדר רכה (blur) במקום קו שחור צפוף.
- קלפים קצרים (עד ~5 מילים / ~32 תווים) שמתחלפים, כמו כתוביות רילס.

edited_time = source_time - cut_start + intro_dur. מסנן לטווח החיתוך.
שימוש: make_subs.py <transcript.json> <cut_start> <cut_end|end> <intro_dur> <out.ass>
        [max_words=5] [max_chars=32] [fontsize=64] [marginv=90]
"""
import json
import os
import re
import sys

FONT = "Assistant ExtraBold"

# מילון תיקונים גלובלי לכל התמלולים (שגיאות ASR חוזרות). מוחל על טקסט הסגמנט לפני פיצול.
_FIXES_PATH = os.path.join(os.path.dirname(__file__), "caption_fixes.json")
FIXES = json.load(open(_FIXES_PATH)) if os.path.exists(_FIXES_PATH) else {}


def apply_fixes(text):
    for wrong, right in FIXES.items():
        text = text.replace(wrong, right)
    return text


def ts(t):
    t = max(t, 0)
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def split_cards(text, start, end, max_words, max_chars):
    """מפצל טקסט סגמנט לקלפים קצרים; מחלק את הזמן פרופורציונלית לאורך."""
    text = re.sub(r"\s+", " ", text.strip())
    words = text.split()
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        joined = " ".join(cur)
        ends_punct = bool(re.search(r"[.,?!:]$", w))
        if len(cur) >= max_words or len(joined) >= max_chars or (ends_punct and len(cur) >= 3):
            chunks.append(joined); cur = []
    if cur:
        chunks.append(" ".join(cur))
    if not chunks:
        return []
    total = sum(len(c) for c in chunks) or 1
    out, t = [], start
    span = end - start
    for c in chunks:
        d = span * len(c) / total
        out.append((t, t + d, c)); t += d
    return out


def main():
    a = sys.argv
    tj, cs, ce, intro, out = a[1:6]
    max_words = int(a[6]) if len(a) > 6 else 5
    max_chars = int(a[7]) if len(a) > 7 else 32
    fs = int(a[8]) if len(a) > 8 else 64
    mv = int(a[9]) if len(a) > 9 else 90

    cut_start = float(cs)
    cut_end = 1e9 if ce == "end" else float(ce)
    intro_dur = float(intro)
    offset = intro_dur - cut_start

    data = json.load(open(tj))
    segs = data if isinstance(data, list) else data.get("segments", [])

    # סגנון: לבן, בלי צל (Shadow=0), הילה רכה מוזרקת פר-שורה (\blur). BorderStyle=1.
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{FONT},{fs},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,0,2,120,120,{mv},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    # הילה רכה: bord רך + blur, בלי shadow (\shad0). מוזרק בתחילת כל שורה.
    halo = r"{\bord3\blur6\shad0}"
    # ⚠️ RTL: עוטפים כל קלף ב-RLE(U+202B)..PDF(U+202C) — בלי זה הפיסוק (נקודה/פסיק) יוצא
    # בצד ימין במקום שמאל. אומת 2026-07-16 מול טקסט עם מספרים, פסיקים, נקודות.
    RLE, PDF = "‫", "‬"
    lines = []
    for s in segs:
        st, en = float(s["start"]), float(s["end"])
        if en <= cut_start or st >= cut_end:
            continue
        st = max(st, cut_start); en = min(en, cut_end)
        for a0, b0, txt in split_cards(apply_fixes(s["text"]), st, en, max_words, max_chars):
            if not txt.strip():
                continue
            lines.append(f"Dialogue: 0,{ts(a0 + offset)},{ts(b0 + offset)},Sub,,0,0,0,,{halo}{RLE}{txt}{PDF}")

    open(out, "w").write(head + "\n".join(lines) + "\n")
    print(f"wrote {out} — {len(lines)} cards (offset {offset:+.1f}s, font {fs}, marginV {mv})")


if __name__ == "__main__":
    main()
