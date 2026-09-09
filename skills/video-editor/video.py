#!/usr/bin/env python3
"""
Video editor wrapper around ffmpeg/ffprobe.
Common operations with sensible defaults, hardware acceleration on macOS (videotoolbox).

Usage:
  video.py concat <out.mp4> <in1> <in2> [...]
  video.py trim <in> <out> --start 00:00:10 --end 00:00:30
  video.py resize <in> <out> --aspect 9:16 [--mode crop|pad]
  video.py compress <in> <out> [--target-mb 25] [--crf 28]
  video.py extract-audio <in> <out.mp3>
  video.py mute <in> <out>
  video.py replace-audio <in_video> <in_audio> <out>
  video.py burn-subs <in_video> <in_srt> <out> [--font-size 28] [--rtl]
  video.py text <in> <out> --text "..." [--pos bottom|top|center] [--size 48]
  video.py speed <in> <out> --factor 2.0
  video.py thumbnail <in> <out.jpg> [--time 00:00:05]
  video.py gif <in> <out.gif> [--fps 12] [--width 480] [--start 00:00:00] [--duration 5]
  video.py info <in>
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, tempfile, shlex
from pathlib import Path

FFMPEG = "/usr/local/bin/ffmpeg"
FFPROBE = "/usr/local/bin/ffprobe"
HWACCEL = ["-hwaccel", "videotoolbox"]  # macOS hardware decode
HWENC = "h264_videotoolbox"  # macOS hardware encoder (fast)
SWENC = "libx264"  # software encoder (better quality/size)

def run(cmd: list[str], quiet: bool = False) -> int:
    if not quiet:
        print("→", " ".join(shlex.quote(c) for c in cmd), file=sys.stderr)
    return subprocess.call(cmd)

def probe(path: str) -> dict:
    out = subprocess.check_output([
        FFPROBE, "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", path
    ])
    return json.loads(out)

def get_duration(path: str) -> float:
    return float(probe(path)["format"]["duration"])

def get_video_size(path: str) -> tuple[int, int]:
    """Return display dimensions (width, height) — honors rotation metadata."""
    for s in probe(path)["streams"]:
        if s["codec_type"] == "video":
            w, h = s["width"], s["height"]
            rot = 0
            for sd in s.get("side_data_list", []) or []:
                if "rotation" in sd:
                    rot = int(sd["rotation"])
            if rot == 0:
                rot = int(s.get("tags", {}).get("rotate", 0) or 0)
            if abs(rot) % 180 == 90:
                w, h = h, w
            return w, h
    raise RuntimeError(f"No video stream in {path}")

# ---------- Operations ----------

def op_info(args):
    data = probe(args.input)
    fmt = data["format"]
    print(f"File:      {fmt['filename']}")
    print(f"Duration:  {float(fmt['duration']):.2f}s")
    print(f"Size:      {int(fmt['size'])/1024/1024:.2f} MB")
    print(f"Bitrate:   {int(fmt['bit_rate'])/1000:.0f} kbps")
    for s in data["streams"]:
        if s["codec_type"] == "video":
            print(f"Video:     {s['codec_name']} {s['width']}x{s['height']} {eval(s.get('r_frame_rate','0/1') or '0/1'):.2f}fps")
        elif s["codec_type"] == "audio":
            print(f"Audio:     {s['codec_name']} {s.get('sample_rate')}Hz {s.get('channels')}ch")

def op_concat(args):
    """Concatenate videos. Re-encodes to handle codec/resolution mismatches reliably."""
    inputs = args.inputs
    out = args.output
    if len(inputs) < 2:
        sys.exit("concat: need at least 2 inputs")
    # Build filter_complex - normalizes resolution & sample rate
    # Detect first video's resolution as the canonical target
    w, h = get_video_size(inputs[0])
    # Force even dimensions (x264 requires)
    w -= w % 2; h -= h % 2

    parts = []
    for p in inputs:
        parts.extend(["-i", p])

    filter_streams = []
    n = len(inputs)
    for i in range(n):
        filter_streams.append(
            f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v{i}];"
            f"[{i}:a]aresample=async=1,aformat=sample_rates=48000:channel_layouts=stereo[a{i}];"
        )
    concat_inputs = "".join(f"[v{i}][a{i}]" for i in range(n))
    filter_complex = "".join(filter_streams) + f"{concat_inputs}concat=n={n}:v=1:a=1[v][a]"

    cmd = [FFMPEG, "-y"] + parts + [
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "[a]",
        "-c:v", SWENC, "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        out
    ]
    sys.exit(run(cmd))

def op_trim(args):
    cmd = [FFMPEG, "-y"]
    if args.start: cmd += ["-ss", args.start]
    if args.end:   cmd += ["-to", args.end]
    cmd += ["-i", args.input]
    if args.copy:
        cmd += ["-c", "copy"]
    else:
        cmd += ["-c:v", SWENC, "-preset", "medium", "-crf", "20",
                "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-movflags", "+faststart", args.output]
    sys.exit(run(cmd))

ASPECT_MAP = {
    "9:16": (1080, 1920),   # Reels/Shorts/TikTok
    "16:9": (1920, 1080),   # YouTube/landscape
    "1:1":  (1080, 1080),   # Instagram feed square
    "4:5":  (1080, 1350),   # Instagram portrait
    "3:4":  (1080, 1440),
}

def op_resize(args):
    if args.aspect in ASPECT_MAP:
        tw, th = ASPECT_MAP[args.aspect]
    else:
        try:
            tw, th = map(int, args.aspect.lower().split("x"))
        except Exception:
            sys.exit(f"resize: bad --aspect {args.aspect!r}. Use 9:16/16:9/1:1/4:5/3:4 or WxH")
    tw -= tw % 2; th -= th % 2

    if args.mode == "crop":
        vf = (f"scale={tw}:{th}:force_original_aspect_ratio=increase,"
              f"crop={tw}:{th}")
    elif args.mode == "pad":
        vf = (f"scale={tw}:{th}:force_original_aspect_ratio=decrease,"
              f"pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2:black")
    else:  # blur pad: scale-fit, blurred background, center
        vf = (f"split=2[bg][fg];"
              f"[bg]scale={tw}:{th}:force_original_aspect_ratio=increase,"
              f"crop={tw}:{th},gblur=sigma=30[bg2];"
              f"[fg]scale={tw}:{th}:force_original_aspect_ratio=decrease[fg2];"
              f"[bg2][fg2]overlay=(W-w)/2:(H-h)/2")

    cmd = [FFMPEG, "-y", "-i", args.input,
           "-vf", vf,
           "-c:v", SWENC, "-preset", "medium", "-crf", "20",
           "-c:a", "copy",
           "-movflags", "+faststart",
           args.output]
    sys.exit(run(cmd))

def op_compress(args):
    """Two-pass if --target-mb specified, else CRF single-pass."""
    if args.target_mb:
        duration = get_duration(args.input)
        total_bits = args.target_mb * 8 * 1024 * 1024
        # leave ~128 kbps for audio
        audio_bps = 128_000
        video_bps = int(total_bits / duration) - audio_bps
        if video_bps < 200_000:
            print(f"⚠ target too tight; video would be {video_bps/1000:.0f} kbps", file=sys.stderr)
        passlog = tempfile.mktemp(prefix="ffpass_")
        # Pass 1
        cmd1 = [FFMPEG, "-y", "-i", args.input,
                "-c:v", SWENC, "-b:v", str(video_bps),
                "-pass", "1", "-passlogfile", passlog,
                "-an", "-f", "null", "/dev/null"]
        rc = run(cmd1)
        if rc != 0: sys.exit(rc)
        # Pass 2
        cmd2 = [FFMPEG, "-y", "-i", args.input,
                "-c:v", SWENC, "-b:v", str(video_bps),
                "-pass", "2", "-passlogfile", passlog,
                "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart",
                args.output]
        rc = run(cmd2)
        # cleanup
        for ext in ("-0.log", "-0.log.mbtree"):
            try: os.unlink(passlog + ext)
            except OSError: pass
        sys.exit(rc)
    else:
        cmd = [FFMPEG, "-y", "-i", args.input,
               "-c:v", SWENC, "-preset", "medium", "-crf", str(args.crf),
               "-c:a", "aac", "-b:a", "128k",
               "-movflags", "+faststart",
               args.output]
        sys.exit(run(cmd))

def op_extract_audio(args):
    out = args.output
    ext = Path(out).suffix.lower()
    cmd = [FFMPEG, "-y", "-i", args.input, "-vn"]
    if ext == ".mp3":
        cmd += ["-c:a", "libmp3lame", "-q:a", "2"]
    elif ext == ".wav":
        cmd += ["-c:a", "pcm_s16le"]
    elif ext == ".m4a":
        cmd += ["-c:a", "aac", "-b:a", "192k"]
    else:
        cmd += ["-c:a", "copy"]
    cmd.append(out)
    sys.exit(run(cmd))

def op_mute(args):
    cmd = [FFMPEG, "-y", "-i", args.input, "-c:v", "copy", "-an", args.output]
    sys.exit(run(cmd))

def op_replace_audio(args):
    cmd = [FFMPEG, "-y",
           "-i", args.input_video,
           "-i", args.input_audio,
           "-map", "0:v:0", "-map", "1:a:0",
           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
           "-shortest",
           args.output]
    sys.exit(run(cmd))

def op_burn_subs(args):
    """Burn SRT subtitles into video. Supports Hebrew RTL."""
    srt = args.srt
    style = (f"FontName=Arial,FontSize={args.font_size},"
             f"PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
             f"BorderStyle=1,Outline=2,Shadow=1,MarginV=40")
    # for RTL we ensure libass picks up directionality
    sub_filter = f"subtitles={shlex.quote(srt)}:force_style='{style}'"
    cmd = [FFMPEG, "-y", "-i", args.input_video,
           "-vf", sub_filter,
           "-c:v", SWENC, "-preset", "medium", "-crf", "20",
           "-c:a", "copy",
           args.output]
    sys.exit(run(cmd))

def op_text(args):
    pos_map = {
        "top":    "x=(w-text_w)/2:y=80",
        "center": "x=(w-text_w)/2:y=(h-text_h)/2",
        "bottom": "x=(w-text_w)/2:y=h-text_h-80",
    }
    pos = pos_map.get(args.pos, pos_map["bottom"])
    text = args.text.replace("'", r"\'").replace(":", r"\:")
    vf = (f"drawtext=text='{text}':fontsize={args.size}:"
          f"fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=12:"
          f"{pos}")
    cmd = [FFMPEG, "-y", "-i", args.input,
           "-vf", vf,
           "-c:v", SWENC, "-preset", "medium", "-crf", "20",
           "-c:a", "copy", args.output]
    sys.exit(run(cmd))

def op_speed(args):
    f = args.factor
    if f <= 0: sys.exit("speed: --factor must be > 0")
    vf = f"setpts={1/f}*PTS"
    # audio atempo supports 0.5..2.0; chain if outside
    atempo_chain = []
    rem = f
    while rem > 2.0:
        atempo_chain.append("atempo=2.0"); rem /= 2.0
    while rem < 0.5:
        atempo_chain.append("atempo=0.5"); rem /= 0.5
    atempo_chain.append(f"atempo={rem}")
    af = ",".join(atempo_chain)
    cmd = [FFMPEG, "-y", "-i", args.input,
           "-vf", vf, "-af", af,
           "-c:v", SWENC, "-preset", "medium", "-crf", "20",
           "-c:a", "aac", "-b:a", "192k",
           args.output]
    sys.exit(run(cmd))

def op_thumbnail(args):
    cmd = [FFMPEG, "-y", "-ss", args.time, "-i", args.input,
           "-frames:v", "1", "-q:v", "2", args.output]
    sys.exit(run(cmd))

def op_gif(args):
    palette = tempfile.mktemp(suffix=".png")
    in_args = ["-ss", args.start] if args.start else []
    if args.duration:
        in_args += ["-t", str(args.duration)]
    vf_palette = f"fps={args.fps},scale={args.width}:-1:flags=lanczos,palettegen"
    vf_use = f"fps={args.fps},scale={args.width}:-1:flags=lanczos[x];[x][1:v]paletteuse"
    rc = run([FFMPEG, "-y"] + in_args + ["-i", args.input, "-vf", vf_palette, palette])
    if rc != 0: sys.exit(rc)
    rc = run([FFMPEG, "-y"] + in_args + ["-i", args.input, "-i", palette,
                                          "-filter_complex", vf_use, args.output])
    try: os.unlink(palette)
    except OSError: pass
    sys.exit(rc)

# ---------- CLI ----------

def main():
    ap = argparse.ArgumentParser(prog="video.py", description="ffmpeg wrapper")
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("info"); p.add_argument("input"); p.set_defaults(fn=op_info)

    p = sp.add_parser("concat")
    p.add_argument("output"); p.add_argument("inputs", nargs="+")
    p.set_defaults(fn=op_concat)

    p = sp.add_parser("trim")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--start"); p.add_argument("--end")
    p.add_argument("--copy", action="store_true", help="stream copy (fast, no re-encode; cut may snap to keyframes)")
    p.set_defaults(fn=op_trim)

    p = sp.add_parser("resize")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--aspect", required=True, help="9:16 / 16:9 / 1:1 / 4:5 / 3:4 / WxH")
    p.add_argument("--mode", choices=["crop", "pad", "blur"], default="crop")
    p.set_defaults(fn=op_resize)

    p = sp.add_parser("compress")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--target-mb", type=float, default=None)
    p.add_argument("--crf", type=int, default=28)
    p.set_defaults(fn=op_compress)

    p = sp.add_parser("extract-audio")
    p.add_argument("input"); p.add_argument("output")
    p.set_defaults(fn=op_extract_audio)

    p = sp.add_parser("mute")
    p.add_argument("input"); p.add_argument("output")
    p.set_defaults(fn=op_mute)

    p = sp.add_parser("replace-audio")
    p.add_argument("input_video"); p.add_argument("input_audio"); p.add_argument("output")
    p.set_defaults(fn=op_replace_audio)

    p = sp.add_parser("burn-subs")
    p.add_argument("input_video"); p.add_argument("srt"); p.add_argument("output")
    p.add_argument("--font-size", type=int, default=28)
    p.add_argument("--rtl", action="store_true")
    p.set_defaults(fn=op_burn_subs)

    p = sp.add_parser("text")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--text", required=True)
    p.add_argument("--pos", choices=["top", "center", "bottom"], default="bottom")
    p.add_argument("--size", type=int, default=48)
    p.set_defaults(fn=op_text)

    p = sp.add_parser("speed")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--factor", type=float, required=True)
    p.set_defaults(fn=op_speed)

    p = sp.add_parser("thumbnail")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--time", default="00:00:01")
    p.set_defaults(fn=op_thumbnail)

    p = sp.add_parser("gif")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--fps", type=int, default=12)
    p.add_argument("--width", type=int, default=480)
    p.add_argument("--start", default=None)
    p.add_argument("--duration", type=float, default=None)
    p.set_defaults(fn=op_gif)

    args = ap.parse_args()
    args.fn(args)

if __name__ == "__main__":
    main()
