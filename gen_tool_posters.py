#!/usr/bin/env python3
"""
gen_tool_posters.py — regenerate the bland tool-category posters.

User feedback: 工具型的那几个游戏海报太平淡了，没有什么吸引力.
Album-cover-generator + mugshot-booth + my-meme were kept (they
already have personality). This script targets the remaining 6:
  field-guide / fit-check / trash-or-treasure / almanac /
  meow-machine / rhythm-machine

Each entry is a config dict:
  id        — output filename basename (matches posters/<id>.png)
  prompt    — text-to-image prompt (NO TEXT, character-led action)
  title_*   — wordmark overlay style (font, color, position, tilt)
  mask      — strength of the top-band gradient that covers AI-baked text
"""
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

# ─── transit gen-image ────────────────────────────────────────────────
API_URL = "https://chat.aiwaves.tech/aigram/api/gen-image"
HEADERS = {
    "Content-Type": "application/json",
    "Origin":  "https://aigram.app",
    "Referer": "https://aigram.app/",
    "User-Agent": "Mozilla/5.0",
}


def gen_image(prompt: str, timeout: int = 360, retries: int = 3) -> str:
    payload = {"prompt": prompt}
    data = json.dumps(payload).encode()
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(API_URL, data=data, method="POST", headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = json.loads(r.read())
            url = body.get("url")
            if not url:
                raise RuntimeError(f"gen response had no url: {body}")
            return url
        except urllib.error.HTTPError as e:
            err_body = ""
            try: err_body = e.read().decode("utf-8", errors="replace")[:200]
            except Exception: pass
            last_err = RuntimeError(f"HTTP {e.code} (attempt {attempt+1}/{retries}): {err_body}")
            print(f"   retry {attempt+1}/{retries} after HTTP {e.code}", flush=True)
        except Exception as e:
            last_err = e
            print(f"   retry {attempt+1}/{retries} after {e}", flush=True)
        time.sleep(8 * (attempt + 1))
    raise last_err or RuntimeError("gen failed")


def download_image(url: str, out_path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    ext = os.path.splitext(url.split("?")[0])[1].lower()
    if ext and ext != ".png":
        tmp = out_path.with_suffix(out_path.suffix + ext)
        tmp.write_bytes(data)
        subprocess.run(["sips", "-s", "format", "png", str(tmp), "--out", str(out_path)],
                       check=True, capture_output=True)
        tmp.unlink()
    else:
        out_path.write_bytes(data)


# ─── PIL helpers ────────────────────────────────────────────────────
def find_font(candidates: list, size: int) -> ImageFont.FreeTypeFont:
    """Try given font paths in order, fall back to common macOS fonts."""
    paths = list(candidates) + [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/System/Library/Fonts/Supplemental/Futura.ttc",
        "/Library/Fonts/Impact.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


@dataclass
class Title:
    text: str
    color: Tuple[int, int, int]
    shadow: Tuple[int, int, int] = (0, 0, 0)
    pos: str = "top"               # "top" | "bottom"
    tilt: float = 0.0
    size_ratio: float = 0.16       # of canvas height
    fonts: list = field(default_factory=list)


@dataclass
class PosterCfg:
    id: str
    prompt: str
    title: Title
    mask_alpha: int = 215          # top-band cover strength (0=clear, 255=opaque)
    mask_band_pct: float = 0.30    # height of mask as fraction of canvas


def bake_poster(art: Path, out: Path, cfg: PosterCfg) -> None:
    base = Image.open(art).convert("RGBA")
    W, H = base.size

    # Mask the wordmark band (covers any AI-baked text behind the title).
    band_h = int(H * cfg.mask_band_pct)
    band = Image.new("RGBA", (W, band_h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for y in range(band_h):
        u = y / band_h if cfg.title.pos == "top" else 1.0 - y / band_h
        if u < 0.55:
            a = cfg.mask_alpha
        else:
            t = 1.0 - (u - 0.55) / 0.45
            a = int(cfg.mask_alpha * (t ** 1.2))
        bd.line([(0, y), (W, y)], fill=(18, 16, 12, max(0, a)))
    band_y = 0 if cfg.title.pos == "top" else H - band_h
    base.alpha_composite(band, (0, band_y))

    # ALSO mask the OPPOSITE edge — the model bakes gibberish at both ends.
    soft_h = int(H * 0.20)
    soft = Image.new("RGBA", (W, soft_h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(soft)
    for y in range(soft_h):
        u = y / soft_h if cfg.title.pos == "bottom" else 1.0 - y / soft_h
        a = int(220 * (1.0 - u) ** 1.5)   # opaque at edge → 0 toward center
        sd.line([(0, y), (W, y)], fill=(18, 16, 12, max(0, a)))
    soft_y = 0 if cfg.title.pos == "bottom" else H - soft_h
    base.alpha_composite(soft, (0, soft_y))

    # Wordmark text on a transparent layer, then rotate + composite.
    size = int(H * cfg.title.size_ratio)
    font = find_font(cfg.title.fonts, size)
    text = cfg.title.text
    scratch = ImageDraw.Draw(Image.new("RGBA", (W, H)))
    bbox = scratch.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    shadow_dx, shadow_dy = int(size * 0.075), int(size * 0.095)
    pad = int(size * 0.30)
    layer_w = tw + pad * 2 + shadow_dx
    layer_h = th + pad * 2 + shadow_dy
    layer = Image.new("RGBA", (layer_w, layer_h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    origin = (pad - bbox[0], pad - bbox[1])
    ld.text((origin[0] + shadow_dx, origin[1] + shadow_dy),
            text, font=font, fill=(*cfg.title.shadow, 255))
    ld.text(origin, text, font=font, fill=(*cfg.title.color, 255))
    if abs(cfg.title.tilt) > 0.05:
        layer = layer.rotate(cfg.title.tilt, resample=Image.BICUBIC, expand=True)

    px = (W - layer.width) // 2
    if cfg.title.pos == "top":
        py = int(H * 0.04)
    else:
        py = H - layer.height - int(H * 0.04)
    base.alpha_composite(layer, (px, py))
    base.convert("RGB").save(out, "PNG", optimize=True)


# ─── per-game configs ────────────────────────────────────────────────
NO_TEXT = (
    "Wordless illustration, purely visual. Labels and signage in scene are "
    "blank or abstract pictograms, not readable lettering. "
    "Image fills the entire square frame edge to edge, full-bleed, "
    "no border, no panel, no letterbox, no matte."
)

# Find Bangers if installed for comic titles; falls back to Impact.
BANGERS = [os.path.expanduser("~/Library/Fonts/Bangers-Regular.ttf")]
# Editorial-serif fallback for the AlterU Press titles.
SERIF = [
    "/System/Library/Fonts/Supplemental/Didot.ttc",
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
]


CONFIGS = [
    PosterCfg(
        id="alteru-press-field-guide",
        prompt=(
            "Square illustrated poster of an old-school field naturalist's "
            "discovery moment. Foreground: a chunky voxel-art style "
            "explorer in safari hat and round glasses, holding up an antique "
            "brass camera, photographing a single iconic ordinary object — a "
            "vintage teapot — that floats centered in front of them like a "
            "museum specimen, surrounded by faint hand-drawn annotation arrows "
            "and tiny sketched ethnographic notes radiating outward in 6 "
            "directions. Background: a softly-lit cream paper backdrop with a "
            "subtle grid, a stack of curiosity drawers, a brass lamp, vintage "
            "specimen jars. Editorial poster aesthetic mixed with bold voxel "
            "figure. Palette: warm cream, dusty pink, deep ink, accent teal "
            "#3fb6ac. Sense of wonder and discovery. " + NO_TEXT
        ),
        title=Title(
            text="FIELD GUIDE",
            color=(40, 32, 28), shadow=(220, 110, 160),
            pos="bottom", tilt=0.0, size_ratio=0.11, fonts=SERIF,
        ),
        mask_alpha=200, mask_band_pct=0.22,
    ),
    PosterCfg(
        id="fit-check",
        prompt=(
            "Square fashion magazine cover style illustration of a confident "
            "Crossy Road voxel-style character striking a pose in a bold "
            "outfit — leopard print coat, statement red heels, pink bag — "
            "in front of a vintage full-length mirror. The mirror reflection "
            "shows the same character but with a giant glowing KEEP / TOSS "
            "verdict stamp hovering over them (shown as two stamp shapes "
            "without legible English letters — abstract green check + red X). "
            "Background: a chic boutique fitting room, soft warm lighting, "
            "clothing rack with vibrant pieces, mirror-ball ceiling lamp. "
            "Editorial fashion illustration mixed with bold voxel figure. "
            "Saturated palette: dusty rose, gold, warm cream, accent teal "
            "#3fb6ac. Energetic confident vibe. " + NO_TEXT
        ),
        title=Title(
            text="FIT CHECK",
            color=(255, 90, 140), shadow=(40, 25, 30),
            pos="top", tilt=-2.5, size_ratio=0.16, fonts=BANGERS,
        ),
        mask_alpha=220, mask_band_pct=0.28,
    ),
    PosterCfg(
        id="trash-or-treasure",
        prompt=(
            "Square comic illustration, 80s arcade aesthetic. Center: a hand "
            "with a chunky cartoon arm presenting an ordinary household item "
            "— a slightly dusty porcelain Funko-style figurine — toward the "
            "viewer. Behind it, a massive glowing magical eye floating mid-air, "
            "shooting two diverging beams of light from the figurine: one beam "
            "to the upper-left ending in a green glowing aura around a "
            "treasure chest icon (KEEP), one beam to the lower-right ending "
            "in a red glowing aura around a trash can icon (TOSS). Dramatic "
            "lighting, retro-futuristic, dark purple-magenta-cyan vaporwave "
            "background with subtle grid lines and palm silhouettes. Bold "
            "comic linework + neon glow effects. Saturated palette: hot pink, "
            "neon cyan, deep purple, glowing yellow accents. Sense of "
            "judgment and verdict. " + NO_TEXT
        ),
        title=Title(
            text="TRASH OR TREASURE",
            color=(255, 200, 60), shadow=(255, 50, 120),
            pos="top", tilt=-2.0, size_ratio=0.09, fonts=BANGERS,
        ),
        mask_alpha=220, mask_band_pct=0.26,
    ),
    PosterCfg(
        id="alteru-press-almanac",
        prompt=(
            "Square illustrated poster of a cozy ritual moment from a daily "
            "almanac. Center: a chunky voxel character at a small writing "
            "desk in a cozy lamplit room at dawn, hand-writing a letter with "
            "a quill on parchment paper. Floating around them like a fortune "
            "scroll: 3 small comic vignettes of recommended daily actions "
            "(walking outside on a path, meeting an old friend across a "
            "table for tea, reading a book in a chair). One subtle moon-phase "
            "ring at the top corner. Background: cream paper textured wall, "
            "potted plant, a steaming teacup, soft golden hour light. "
            "Editorial illustration with a hint of tarot mysticism. Palette: "
            "warm cream, deep navy ink, dusty rose, accent gold. Calm, "
            "contemplative, ritual energy. " + NO_TEXT
        ),
        title=Title(
            text="ALMANAC",
            color=(35, 28, 50), shadow=(220, 110, 160),
            pos="bottom", tilt=0.0, size_ratio=0.13, fonts=SERIF,
        ),
        mask_alpha=180, mask_band_pct=0.22,
    ),
    PosterCfg(
        id="meow-machine",
        prompt=(
            "Square comic poster, 80s synth-pop aesthetic. Center: 8 chunky "
            "cartoon cats in a row, each one a different color (ginger, "
            "black, white, calico, grey, brown, tabby, siamese), all wearing "
            "tiny headphones and standing behind miniature glowing synthesizers "
            "with rainbow LED keys. The cats are open-mouthed mid-meow with "
            "musical notes and waveform symbols floating up from each one in "
            "saturated neon colors. Background: a deep purple stage with "
            "scanning spotlights, a giant pulsing equalizer wall, neon palm "
            "leaves at the edges, retro grid floor. Bold comic linework + "
            "neon glow. Saturated palette: hot pink, electric blue, neon "
            "yellow, vibrant teal #3fb6ac. Energetic synth-cat band vibe. "
            + NO_TEXT
        ),
        title=Title(
            text="MEOW MACHINE",
            color=(255, 80, 180), shadow=(40, 20, 60),
            pos="top", tilt=-2.5, size_ratio=0.11, fonts=BANGERS,
        ),
        mask_alpha=220, mask_band_pct=0.24,
    ),
    PosterCfg(
        id="rhythm-machine",
        prompt=(
            "Square retro-futuristic poster of a TR-808 style drum machine "
            "in dramatic neon studio lighting. The drum machine is a chunky "
            "black box with glowing red and orange step buttons, knobs and "
            "VU meters, viewed at a 3/4 dynamic angle. Two cartoon hands "
            "with bright wristbands hover over it, fingers tapping the "
            "glowing pads, with musical notes and waveform pulses exploding "
            "outward in neon colors. Background: a moody studio scene with "
            "vinyl records on a wall, glowing cassette tapes, a glowing "
            "speaker cone, deep purple atmospheric haze. Bold graphic poster "
            "style + neon glow effects + speed lines for tapping energy. "
            "Saturated palette: hot orange, neon red, deep purple, electric "
            "blue, accent teal #3fb6ac. Sense of beat and rhythm. " + NO_TEXT
        ),
        title=Title(
            text="RHYTHM MACHINE",
            color=(255, 100, 60), shadow=(60, 20, 60),
            pos="top", tilt=-2.0, size_ratio=0.10, fonts=BANGERS,
        ),
        mask_alpha=220, mask_band_pct=0.24,
    ),
]


def main() -> None:
    here = Path(__file__).resolve().parent
    posters_dir = here / "posters"
    raw_dir = here / "_poster_raw"
    raw_dir.mkdir(exist_ok=True)
    posters_dir.mkdir(exist_ok=True)

    for i, cfg in enumerate(CONFIGS, 1):
        print(f"\n[{i}/{len(CONFIGS)}] {cfg.id}", flush=True)
        art = raw_dir / f"{cfg.id}.png"
        final = posters_dir / f"{cfg.id}.png"
        print("  → gen…", flush=True)
        url = gen_image(cfg.prompt)
        print(f"     {url}", flush=True)
        print("  → download + convert…", flush=True)
        download_image(url, art)
        print(f"     {art.stat().st_size:,} bytes", flush=True)
        print("  → bake title…", flush=True)
        bake_poster(art, final, cfg)
        print(f"     saved {final} ({final.stat().st_size:,} bytes)", flush=True)
    print("\nall done.", flush=True)


if __name__ == "__main__":
    main()
