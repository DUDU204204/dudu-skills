#!/usr/bin/env python3
"""
Imagen 4 (Google) — יצירת תמונות דרך Gemini API (predict endpoint).
איכותי יותר מ-Nano Banana, טוב יותר ברנדור טקסט.

Usage:
    python imagen.py "prompt" --aspect 1:1
    python imagen.py "prompt" --aspect 16:9 --out /path/to/image.png
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

MODEL = "imagen-4.0-generate-001"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:predict"
SETTINGS = pathlib.Path.home() / ".claude" / "settings.json"
DEFAULT_OUT_DIR = pathlib.Path.home() / "workspaces" / "_infra" / "nano_banana_output"

SUPPORTED_ASPECTS = {"1:1", "3:4", "4:3", "9:16", "16:9"}


def load_api_key() -> str:
    data = json.loads(SETTINGS.read_text())
    return data["mcpServers"]["gemini-transcription"]["env"]["GEMINI_API_KEY"]


def generate(prompt: str, aspect: str, api_key: str) -> bytes:
    body = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": aspect,
            "personGeneration": "allow_adult",
        },
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
        with urllib.request.urlopen(req, timeout=180) as resp:
            payload = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Imagen API שגיאה {e.code}: {e.read().decode('utf-8', 'replace')}")

    preds = payload.get("predictions", [])
    if not preds:
        sys.exit(f"לא חזרה תמונה. תגובה:\n{json.dumps(payload, ensure_ascii=False, indent=2)}")
    b64 = preds[0].get("bytesBase64Encoded")
    if not b64:
        sys.exit(f"אין bytesBase64Encoded. תגובה:\n{json.dumps(payload, ensure_ascii=False, indent=2)}")
    return base64.b64decode(b64)


def default_filename(prompt: str) -> pathlib.Path:
    slug = re.sub(r"[^\w\-]+", "_", prompt, flags=re.UNICODE).strip("_")[:40] or "image"
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return DEFAULT_OUT_DIR / f"{stamp}_imagen4_{slug}.png"


def main() -> None:
    ap = argparse.ArgumentParser(description="Imagen 4 (Google)")
    ap.add_argument("prompt")
    ap.add_argument("--aspect", default="1:1",
                    help=f"יחס: {sorted(SUPPORTED_ASPECTS)}")
    ap.add_argument("--out", type=pathlib.Path)
    args = ap.parse_args()

    if args.aspect not in SUPPORTED_ASPECTS:
        sys.exit(f"Imagen 4 תומך רק ב: {sorted(SUPPORTED_ASPECTS)}")

    out = args.out or default_filename(args.prompt)
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"→ Imagen 4: {args.prompt!r} ({args.aspect})")
    img = generate(args.prompt, args.aspect, load_api_key())
    out.write_bytes(img)
    print(f"✓ נשמר: {out} ({len(img):,} bytes)")


if __name__ == "__main__":
    main()
