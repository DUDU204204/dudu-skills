#!/usr/bin/env python3
"""
Nano Banana (Gemini 2.5 Flash Image) — יצירת תמונות דרך Gemini API.

Usage:
    python nano_banana.py "prompt here"
    python nano_banana.py "prompt here" --aspect 16:9
    python nano_banana.py "prompt here" --out /path/to/image.png
    python nano_banana.py "prompt here" --aspect 9:16 --out /tmp/banana.png

Supported aspect ratios: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
Default: 1:1
"""
import argparse
import base64
import datetime as dt
import json
import pathlib
import re
import sys
import urllib.request
import urllib.error

MODEL = "gemini-2.5-flash-image"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
SETTINGS = pathlib.Path.home() / ".claude" / "settings.json"
DEFAULT_OUT_DIR = pathlib.Path.home() / "workspaces" / "_infra" / "nano_banana_output"


def load_api_key() -> str:
    data = json.loads(SETTINGS.read_text())
    key = data["mcpServers"]["gemini-transcription"]["env"]["GEMINI_API_KEY"]
    if not key:
        sys.exit("GEMINI_API_KEY לא נמצא ב-settings.json")
    return key


def generate(prompt: str, aspect: str, api_key: str) -> bytes:
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"imageConfig": {"aspectRatio": aspect}},
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Gemini API שגיאה {e.code}: {e.read().decode('utf-8', 'replace')}")

    for part in payload["candidates"][0]["content"]["parts"]:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data"):
            return base64.b64decode(inline["data"])
    sys.exit(f"לא חזרה תמונה. תגובה מלאה:\n{json.dumps(payload, ensure_ascii=False, indent=2)}")


def default_filename(prompt: str) -> pathlib.Path:
    slug = re.sub(r"[^\w\-]+", "_", prompt, flags=re.UNICODE).strip("_")[:40] or "image"
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return DEFAULT_OUT_DIR / f"{stamp}_{slug}.png"


def main() -> None:
    ap = argparse.ArgumentParser(description="Nano Banana (Gemini 2.5 Flash Image)")
    ap.add_argument("prompt", help="תיאור התמונה (עברית/אנגלית)")
    ap.add_argument("--aspect", default="1:1",
                    help="יחס גובה-רוחב: 1:1, 16:9, 9:16, 4:3, 3:4, 21:9... (ברירת מחדל 1:1)")
    ap.add_argument("--out", type=pathlib.Path, help="נתיב פלט. אם לא סופק — ייווצר אוטומטית בתיקיית nano_banana_output/")
    args = ap.parse_args()

    out = args.out or default_filename(args.prompt)
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"→ יוצר תמונה: {args.prompt!r} ({args.aspect})")
    img_bytes = generate(args.prompt, args.aspect, load_api_key())
    out.write_bytes(img_bytes)
    print(f"✓ נשמר: {out} ({len(img_bytes):,} bytes)")


if __name__ == "__main__":
    main()
