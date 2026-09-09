#!/usr/bin/env python3
"""Transcribe audio/video to Hebrew text using the local ivrit-ai Whisper model.

Usage:
    transcribe.py <audio_path> [--out <txt_path>] [--srt <srt_path>] [--json <json_path>]

Prints the plain-text transcript to stdout.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("HF_HOME", "~/my-business/_infra/ivrit-ai-model")

MODEL_ID = "ivrit-ai/whisper-large-v3-turbo-ct2"


def format_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", help="Path to audio/video file")
    ap.add_argument("--out", help="Write plain text here (in addition to stdout)")
    ap.add_argument("--srt", help="Write SRT subtitles here")
    ap.add_argument("--json", help="Write segments JSON here")
    ap.add_argument("--language", default="he")
    ap.add_argument("--compute-type", default="int8", help="int8 (default, fastest CPU), float32, int8_float16")
    ap.add_argument("--quiet", action="store_true", help="Suppress progress to stderr")
    args = ap.parse_args()

    audio_path = Path(args.audio).expanduser().resolve()
    if not audio_path.exists():
        print(f"ERROR: file not found: {audio_path}", file=sys.stderr)
        sys.exit(2)

    from faster_whisper import WhisperModel

    log = (lambda *a, **k: None) if args.quiet else (lambda *a, **k: print(*a, file=sys.stderr, **k))

    log(f"[transcribe] loading model {MODEL_ID} (compute={args.compute_type})...")
    t0 = time.time()
    model = WhisperModel(MODEL_ID, device="cpu", compute_type=args.compute_type)
    log(f"[transcribe] model loaded in {time.time()-t0:.1f}s")

    log(f"[transcribe] transcribing {audio_path.name}...")
    t0 = time.time()
    segments_iter, info = model.transcribe(
        str(audio_path),
        language=args.language,
        vad_filter=True,
        beam_size=5,
    )

    segments = []
    full_text_parts = []
    for seg in segments_iter:
        segments.append({"start": seg.start, "end": seg.end, "text": seg.text})
        full_text_parts.append(seg.text)
        log(f"  [{format_srt_time(seg.start)} -> {format_srt_time(seg.end)}] {seg.text.strip()[:80]}")

    full_text = "".join(full_text_parts).strip()
    log(f"[transcribe] done in {time.time()-t0:.1f}s ({len(segments)} segments, duration {info.duration:.1f}s)")

    print(full_text)

    if args.out:
        Path(args.out).write_text(full_text + "\n", encoding="utf-8")
        log(f"[transcribe] wrote {args.out}")

    if args.srt:
        lines = []
        for i, s in enumerate(segments, 1):
            lines.append(str(i))
            lines.append(f"{format_srt_time(s['start'])} --> {format_srt_time(s['end'])}")
            lines.append(s["text"].strip())
            lines.append("")
        Path(args.srt).write_text("\n".join(lines), encoding="utf-8")
        log(f"[transcribe] wrote {args.srt}")

    if args.json:
        Path(args.json).write_text(
            json.dumps({"language": info.language, "duration": info.duration, "segments": segments}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        log(f"[transcribe] wrote {args.json}")


if __name__ == "__main__":
    main()
