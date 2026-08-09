"""Run the demo for real and turn the captured session into docs/demo.cast and docs/demo.gif.

Usage (from the repo root, with the package installed):
    python scripts/record_demo.py
"""

import json
import subprocess
import sys
import textwrap
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "docs"
COLUMNS = 92
GEMMA = ["--model-name", "gemma-3n-e2b", "--embed-model", "paraphrase-multilingual-MiniLM-L12-v2"]

STEPS = [
    (["examples/earthquake-safety.pdf", "What should I do the moment the shaking starts?"], None),
    (["examples/earthquake-safety.pdf", "What should I do if I am trapped under rubble?"], None),
    (["examples/earthquake-safety.pdf", "What is the population of Tokyo?"], "…and when it isn't in the document, it says so"),
    (["examples/water-cycle-fa.pdf", "بیشتر آب کره زمین کجاست؟"] + GEMMA, "…same engine, a Persian document"),
]

BANNER = "wick — question answering over a local PDF, with the network unplugged"


def run(argv: list[str]) -> tuple[str, float]:
    started = time.monotonic()
    result = subprocess.run(
        [sys.executable, "-m", "wick.cli", *argv],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if result.returncode != 0:
        raise SystemExit(f"demo step failed: {argv}\n{result.stderr}")
    return result.stdout.strip(), time.monotonic() - started


def capture() -> list[dict]:
    session = [{"kind": "banner", "text": BANNER}]
    for argv, note in STEPS:
        if note:
            session.append({"kind": "note", "text": note})
        answer, elapsed = run(argv)
        session.append({"kind": "command", "text": shell_form(argv), "elapsed": elapsed})
        session.append({"kind": "answer", "text": answer})
        print(f"  {elapsed:5.1f}s  {argv[1][:60]}")
    return session


def shell_form(argv: list[str]) -> str:
    parts = ["wick"] + [f'"{a}"' if " " in a else a for a in argv]
    return " ".join(parts)


def write_cast(session: list[dict], path: Path) -> None:
    header = {
        "version": 2, "width": COLUMNS + 4, "height": 26,
        "timestamp": int(time.time()), "title": "wick — offline PDF Q&A",
        "env": {"SHELL": "/bin/sh", "TERM": "xterm-256color"},
    }
    lines, clock = [json.dumps(header)], 0.0
    for event in session:
        for text, delay in cast_events(event):
            clock += delay
            lines.append(json.dumps([round(clock, 3), "o", text], ensure_ascii=False))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cast_events(event: dict):
    kind = event["kind"]
    if kind == "banner":
        yield f"\u001b[32m{event['text']}\u001b[0m\r\n", 0.3
    elif kind == "note":
        yield f"\r\n\u001b[33m# {event['text']}\u001b[0m\r\n", 0.8
    elif kind == "command":
        yield "\r\n\u001b[36m$ \u001b[0m", 0.5
        for char in event["text"]:  # typing cadence, so the cast reads like a session
            yield char, 0.035
        yield "\r\n", event["elapsed"]
    else:
        for line in wrap(event["text"]):
            yield line + "\r\n", 0.05


def wrap(text: str) -> list[str]:
    out = []
    for paragraph in text.splitlines() or [""]:
        out.extend(textwrap.wrap(paragraph, COLUMNS) or [""])
    return out


def write_gif(session: list[dict], path: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    mono = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 17)
    arabic = ImageFont.truetype("C:/Windows/Fonts/tahoma.ttf", 17)
    line_height, pad, rows = 25, 22, 22
    width = pad * 2 + int(mono.getlength("M") * (COLUMNS + 2))
    height = pad * 2 + line_height * rows

    frames, durations, screen = [], [], []

    def snapshot(hold_ms: int) -> None:
        image = Image.new("RGB", (width, height), "#12141c")
        draw = ImageDraw.Draw(image)
        for row, (text, color) in enumerate(screen[-rows:]):
            draw_line(draw, text, pad + row * line_height, color, width, pad, mono, arabic)
        frames.append(image)
        durations.append(hold_ms)

    for event in session:
        for text, color, hold in gif_lines(event):
            screen.append((text, color))
            snapshot(hold)
    snapshot(2500)

    frames[0].save(
        path, save_all=True, append_images=frames[1:], duration=durations,
        loop=0, optimize=True, disposal=2,
    )


def gif_lines(event: dict):
    kind = event["kind"]
    if kind == "banner":
        yield event["text"], "#7ee787", 1200
    elif kind == "note":
        yield "", "#12141c", 60
        yield f"# {event['text']}", "#e3b341", 1100
    elif kind == "command":
        yield "", "#12141c", 60
        hold = min(int(event["elapsed"] * 1000), 2000)
        parts = textwrap.wrap(f"$ {event['text']}", COLUMNS, subsequent_indent="    ")
        for index, line in enumerate(parts):
            yield line, "#79c0ff", hold if index == len(parts) - 1 else 120
    else:
        for line in wrap(event["text"]):
            yield line, "#e6edf3", 420


def draw_line(draw, text, y, color, width, pad, mono, arabic) -> None:
    runs = split_runs(text)
    if runs and runs[0][1]:  # a wholly RTL line is right-aligned, as a terminal would show it
        body = shape(text)
        draw.text((width - pad - draw.textlength(body, font=arabic), y), body, font=arabic, fill=color)
        return
    x = pad
    for chunk, rtl in runs:
        font, body = (arabic, shape(chunk)) if rtl else (mono, chunk)
        draw.text((x, y), body, font=font, fill=color)
        x += draw.textlength(body, font=font)


def split_runs(text: str) -> list[tuple[str, bool]]:
    runs: list[list] = []
    for char in text:
        rtl = is_rtl(char)
        # A space joins whichever run it follows, so direction only flips on real letters.
        if runs and (runs[-1][1] == rtl or char == " "):
            runs[-1][0] += char
        else:
            runs.append([char, rtl])
    return [(chunk, rtl) for chunk, rtl in runs]


def is_rtl(text: str) -> bool:
    return any("\u0600" <= ch <= "\u06ff" for ch in text)


def shape(text: str) -> str:
    import arabic_reshaper
    from bidi.algorithm import get_display

    return get_display(arabic_reshaper.reshape(text))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(exist_ok=True)
    print("running demo steps...")
    recorded = capture()
    write_cast(recorded, OUT / "demo.cast")
    write_gif(recorded, OUT / "demo.gif")
    print(f"wrote {OUT / 'demo.cast'} and {OUT / 'demo.gif'}")
