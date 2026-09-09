#!/usr/bin/env python3
"""
GPT-Image-2 (OpenAI) — יצירת תמונות דרך OpenAI Images API.
המודל החדש (השיק 2026-04-21), עוצמה ברנדור טקסט (כולל עברית), עד 4K.

Usage:
    python gpt_image.py "prompt" --size 1024x1024 --out /path/to/image.png
    python gpt_image.py "prompt" --aspect 16:9 --quality high
    python gpt_image.py "prompt" --aspect 16:9 --4k          # 3840x2160
"""
import argparse
import base64
import datetime as dt
import json
import os
import pathlib
import re
import sys
import urllib.request
import urllib.error

ENDPOINT = "https://api.openai.com/v1/images/generations"
MODEL = "gpt-image-2"
ENV_FILE = pathlib.Path.home() / "workspaces" / "_infra" / "telegram-agent" / ".env"
DEFAULT_OUT_DIR = pathlib.Path.home() / "workspaces" / "_infra" / "nano_banana_output"

ASPECT_TO_SIZE = {
    "1:1": "1024x1024",
    "3:2": "1536x1024",
    "2:3": "1024x1536",
    "16:9": "1536x1024",
    "9:16": "1024x1536",
}

ASPECT_TO_SIZE_4K = {
    "1:1": "2048x2048",
    "3:2": "3072x2048",
    "2:3": "2048x3072",
    "16:9": "3840x2160",
    "9:16": "2160x3840",
}


def load_api_key() -> str:
    if "OPENAI_API_KEY" in os.environ:
        return os.environ["OPENAI_API_KEY"]
    for line in ENV_FILE.read_text().splitlines():
        if line.startswith("OPENAI_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("OPENAI_API_KEY לא נמצא")


def generate(prompt: str, size: str, quality: str, api_key: str) -> bytes:
    body = {
        "model": MODEL,
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "n": 1,
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            payload = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"OpenAI API שגיאה {e.code}: {e.read().decode('utf-8', 'replace')}")

    b64 = payload["data"][0].get("b64_json")
    if b64:
        return base64.b64decode(b64)
    url = payload["data"][0].get("url")
    if url:
        with urllib.request.urlopen(url, timeout=60) as r:
            return r.read()
    sys.exit(f"לא חזרה תמונה. תגובה:\n{json.dumps(payload, ensure_ascii=False, indent=2)}")


def default_filename(prompt: str) -> pathlib.Path:
    slug = re.sub(r"[^\w\-]+", "_", prompt, flags=re.UNICODE).strip("_")[:40] or "image"
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return DEFAULT_OUT_DIR / f"{stamp}_gptimage_{slug}.png"


def main() -> None:
    ap = argparse.ArgumentParser(description="GPT-Image-2 (OpenAI)")
    ap.add_argument("prompt")
    ap.add_argument("--size", default=None, help="כל גודל חוקי, כפולות של 16; עד 3840 לקצה ארוך")
    ap.add_argument("--aspect", default="1:1", help="1:1 | 3:2 | 2:3 | 16:9 | 9:16")
    ap.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    ap.add_argument("--4k", dest="four_k", action="store_true", help="פלט באיכות 4K לפי ה-aspect")
    ap.add_argument("--out", type=pathlib.Path)
    args = ap.parse_args()

    table = ASPECT_TO_SIZE_4K if args.four_k else ASPECT_TO_SIZE
    size = args.size or table.get(args.aspect, "1024x1024")
    out = args.out or default_filename(args.prompt)
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"→ GPT-Image-2: {args.prompt!r} ({size}, quality={args.quality})")
    img = generate(args.prompt, size, args.quality, load_api_key())
    out.write_bytes(img)
    print(f"✓ נשמר: {out} ({len(img):,} bytes)")


if __name__ == "__main__":
    main()
