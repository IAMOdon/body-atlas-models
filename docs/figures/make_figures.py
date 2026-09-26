#!/usr/bin/env python3
# =============================================================================
#  FIGURES — Body Atlas Models, same visual system as the @IAMOdon cards
#  -----------------------------------------------------------------
#  Conventions taken from _systeme/cartes.py, unchanged:
#    ground #0d0d0c, text #f8f7f4, grid #262623, series #3987e5 / #d95926,
#    Lora (titles) + Poppins Light (everything else), 1600x900, margin 130 px,
#    one off-centre glow per card. "sable" stays excluded (glow at cx = 0.50).
#
#  Colour meaning, the same in every figure:
#    blue   = the healthy organ, normal anatomy, structure labels
#    orange = pathology
#
#  RULE: no result is drawn until a result exists. These figures are the map
#  of the atlas and its design. No model has been trained. Every figure
#  carries its source line.
#
#  The atlas map is read from CATALOGUE.md at run time, so the figure cannot
#  drift from the committed index.
#
#  USAGE
#      pip install pillow matplotlib numpy      (and oxipng, for lossless size)
#      python docs/figures/make_figures.py
#  -> writes the PNGs to docs/figures/png/ (organ figures in png/<organ>/),
#     each passed through oxipng without loss when oxipng is installed
#  Fonts: Lora-Variable.ttf, Lora-Italic-Variable.ttf, Poppins-Light.ttf
#  in docs/fonts/ (not versioned) or ~/Library/Fonts.
# =============================================================================

import json
import logging
import os
import re
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "png")
CATALOGUE = os.path.join(ROOT, "CATALOGUE.md")

# --- 1. FONTS  (no silent fallback: the typography is part of the system) ----
FONT_DIRS = [
    os.path.join(ROOT, "docs", "fonts"),
    os.path.expanduser("~/Library/Fonts"),
    "/Library/Fonts",
    "/usr/share/fonts/truetype/google-fonts",
]
SERIF_NAME, SERIF_IT_NAME, SANS_NAME = (
    "Lora-Variable.ttf", "Lora-Italic-Variable.ttf", "Poppins-Light.ttf")


def _find_fonts():
    for d in FONT_DIRS:
        if all(os.path.exists(os.path.join(d, n))
               for n in (SERIF_NAME, SERIF_IT_NAME, SANS_NAME)):
            return d
    sys.exit("Lora + Poppins not found in: " + ", ".join(FONT_DIRS))


FONT_DIR = _find_fonts()
# Poppins Light is weight 300: matplotlib says so on every call, harmlessly.
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
for _n in (SERIF_NAME, SERIF_IT_NAME, SANS_NAME):
    fm.fontManager.addfont(os.path.join(FONT_DIR, _n))

# --- 2. THE SYSTEM  (identical to cartes.py) ---------------------------------
W, H = 1600, 900
DPI = 200

GROUND = (13, 13, 12)       # #0d0d0c
INK = "#f8f7f4"
INK2 = "#c3c2b7"
MUTED = "#6f6e66"
GRID = "#262623"
BLUE = "#3987e5"
ORANGE = "#d95926"
GREY = "#3a3a36"
PANEL = "#151514"           # just above the ground, for the pills

MARGIN = 130
GRAIN = 2.1

GLOWS = {
    "acier":  ((40, 48, 62), 0.30, 0.34),
    "braise": ((58, 44, 40), 0.68, 0.30),
    "mousse": ((44, 52, 46), 0.72, 0.62),
    "encre":  ((50, 46, 58), 0.24, 0.66),
    # "sable" excluded: its glow is centred horizontally.
}


def ground(glow, seed):
    """Gradient + grain, same formula as cartes.py."""
    (gr, gg, gb), cx, cy = GLOWS[glow]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx / W - cx) ** 2 + ((yy / H - cy) * 0.62) ** 2) / 0.85
    f = np.clip(1.0 - d, 0, 1) ** 2.6
    base = np.zeros((H, W, 3), np.float32)
    for i, (g0, g1) in enumerate(zip(GROUND, (gr, gg, gb))):
        base[..., i] = g0 + (g1 - g0) * f
    grain = np.random.default_rng(seed).normal(0, GRAIN, (H, W, 1)).astype(np.float32)
    return np.clip(base + grain, 0, 255).astype(np.uint8)


def frame(title, subtitle, source, glow, seed):
    """1600x900 card with glow, Lora title, italic subtitle, source line.

    Returns (fig, ax) where ax covers the whole card in pixel coordinates,
    origin bottom left. Everything is drawn in that frame.
    """
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    # the glow is drawn INSIDE the axes, under everything: a figimage would
    # sit above the axes artists and erase the card.
    ax.imshow(ground(glow, seed), extent=(0, W, 0, H), aspect="auto",
              interpolation="none", zorder=0)
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    ax.text(MARGIN, 0.855 * H, title, fontname="Lora", fontsize=17, color=INK)
    if subtitle:
        ax.text(MARGIN, 0.775 * H, subtitle, fontname="Lora", fontsize=8.2,
                color=INK2, style="italic")
    ax.text(MARGIN, 0.050 * H, source, fontname="Poppins", fontsize=5.2,
            color=MUTED)
    for txt, lim, what in ((title, 62, "title"), (subtitle or "", 150, "subtitle"),
                           (source, 195, "source")):
        if len(txt) > lim:
            print(f"  !! {what} of {len(txt)} characters (limit ~{lim}).")
    return fig, ax


def pill(ax, x, y, w, h, text, edge=GRID, colour=INK2, size=6.4, dashed=False):
    ax.add_patch(FancyBboxPatch((x, y - h / 2), w, h,
                 boxstyle="round,pad=0,rounding_size=10",
                 facecolor=PANEL, edgecolor=edge, linewidth=0.9,
                 linestyle=(0, (2.5, 2.5)) if dashed else "-", zorder=3))
    if text:
        ax.text(x + 18, y, text, fontname="Poppins", fontsize=size,
                color=colour, va="center", zorder=4)


def arrow(ax, x0, x1, y, colour=MUTED):
    ax.annotate("", xy=(x1, y), xytext=(x0, y), zorder=2,
                arrowprops=dict(arrowstyle="-|>", color=colour, lw=0.9,
                                shrinkA=0, shrinkB=0, mutation_scale=7))


def save(fig, name, subdir=""):
    out = os.path.join(OUT, subdir)
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, name)
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    with Image.open(path) as im:
        if im.size != (W, H):
            print(f"  !! {name}: {im.size}, expected {(W, H)}")
    # lossless recompression: same pixels, smaller file
    if shutil.which("oxipng"):
        subprocess.run(["oxipng", "-q", "-o", "4", "--strip", "safe", path], check=True)
    else:
        print("  !! oxipng not found: PNG left uncompressed")
    print("wrote", os.path.relpath(path, ROOT))


# =============================================================================
#  READING THE INDEX
#  Systems are "## N. Title", organs "### Name". An organ has normal data when
#  its "Normal and anatomy" line names a dataset, pathology data when at least
#  one family names a dataset. Reference sections have no pathology.
# =============================================================================
SHORT = {
    "Foundations": "foundations",
    "Special senses": "special senses",
    "Blood and lymphatic system": "blood and lymphatic",
    "Cells and basic tissues": "cells and tissues",
    "Whole-body anatomy on CT and MRI": "whole body on CT and MRI",
    "3D reference anatomy": "3D reference anatomy",
    "Cross-system teaching benchmarks": "teaching benchmarks",
    "Aorta, great and pulmonary vessels": "great vessels",
    "Larynx and upper airway": "larynx",
    "Oral cavity, pharynx and teeth": "mouth and teeth",
    "Small and large bowel": "bowel",
    "Liver and biliary tree": "liver and bile ducts",
    "Uterus, cervix and ovaries": "uterus and ovaries",
    "Pregnancy and fetus": "pregnancy and fetus",
    "Blood cells and bone marrow": "blood and marrow",
    "Across the skeleton": "whole skeleton",
    "Skeletal muscles": "muscles",
}


def short(name):
    if name in SHORT:
        return SHORT[name]
    return re.sub(r" system$", "", name).lower()


def read_index():
    systems, organ, n_datasets = [], None, 0
    for line in open(CATALOGUE, encoding="utf-8"):
        m = re.match(r"^## (\d+)\. (.+)$", line)
        if m:
            systems.append({"num": int(m.group(1)), "name": m.group(2), "organs": []})
            organ = None
            continue
        if line.startswith("## "):
            organ = None
        m = re.match(r"^### (.+)$", line)
        if m and systems:
            organ = {"name": m.group(1), "normal": False, "patho": False,
                     "reference": False}
            systems[-1]["organs"].append(organ)
            continue
        if re.match(r"^\| .+ \| \d{4}-\d{2}-\d{2} \|\s*$", line):
            n_datasets += 1
            continue
        if organ is None:
            continue
        if "**1 · Normal and anatomy:**" in line:
            organ["normal"] = "no verified dataset" not in line
        elif "not applicable (reference section)" in line:
            organ["reference"] = True
        elif line.startswith("  - ") and "no verified dataset" not in line:
            organ["patho"] = True
    n_organs = sum(len(s["organs"]) for s in systems)
    if not systems or not n_organs:
        sys.exit("could not read systems and organs from CATALOGUE.md")
    return systems, n_organs, n_datasets


# =============================================================================
#  FIGURE 01 — the atlas map
#  Every system and organ in the index, in teaching order. Two dots per organ:
#  blue if a verified public dataset shows it healthy or labels its structures,
#  orange if one covers its pathology, a grey point where none was found.
#  Dots say that data exists. They say nothing about any model.
# =============================================================================
def fig01_atlas_map():
    systems, n_organs, n_datasets = read_index()
    fig, ax = frame(
        "the body, as it is taught",
        f"{len(systems)} chapters and {n_organs} organs, each read healthy first "
        "and through its diseases after.",
        f"index of {n_organs} organs and {n_datasets} public datasets, each checked on "
        "17 september 2026  ·  CATALOGUE.md  ·  one model trained so far: brain, use 1",
        glow="acier", seed=2601)

    cols = 4
    colw = (W - 2 * MARGIN) / cols
    tops = [652, 452, 252]
    step = 23
    for i, s in enumerate(systems):
        x = MARGIN + (i % cols) * colw
        top = tops[i // cols]
        ax.text(x, top, f"{s['num']:02d}", fontname="Poppins", fontsize=6.2,
                color=MUTED, va="center")
        ax.text(x + 34, top, short(s["name"]), fontname="Poppins", fontsize=7.0,
                color=INK, va="center")
        ax.plot([x, x + colw - 36], [top - 17, top - 17], color=GRID, lw=0.8)
        for j, o in enumerate(s["organs"]):
            y = top - 42 - j * step
            nx, px = x + 6, x + 25
            if o["normal"]:
                ax.scatter([nx], [y], s=22, color=BLUE, zorder=4)
            else:
                ax.scatter([nx], [y], s=5, color=GREY, zorder=4)
            if not o["reference"]:
                if o["patho"]:
                    ax.scatter([px], [y], s=22, color=ORANGE, zorder=4)
                else:
                    ax.scatter([px], [y], s=5, color=GREY, zorder=4)
            has_any = o["normal"] or o["patho"]
            ax.text(x + 44, y, short(o["name"]), fontname="Poppins", fontsize=5.6,
                    color=INK2 if has_any else MUTED, va="center")

    ly = 0.855 * H + 22
    lx = W - MARGIN - 330
    for k, (kind, label) in enumerate((("blue", "healthy anatomy or structure labels"),
                                       ("orange", "pathology"),
                                       ("grey", "no verified public dataset yet"))):
        yy = ly - k * 26
        if kind == "grey":
            ax.scatter([lx + 6], [yy], s=5, color=GREY)
        else:
            ax.scatter([lx + 6], [yy], s=22, color=BLUE if kind == "blue" else ORANGE)
        ax.text(lx + 24, yy, label, fontname="Poppins", fontsize=5.6, color=INK2,
                va="center")

    save(fig, "01_atlas_map.png")


# =============================================================================
#  FIGURE 02 — the learning path
#  The order a student follows, left to right, with one worked example taken
#  from the index (respiratory system). Brackets below say what a model adds
#  at each level. Nothing here is a result.
# =============================================================================
def fig02_learning_path():
    fig, ax = frame(
        "healthy first, then disease",
        "the order a student follows through every organ of the atlas, and "
        "what a model adds at each step.",
        "schematic  ·  worked example from the respiratory chapter of CATALOGUE.md  ·  "
        "every output is shown beside the dataset's expert label",
        glow="encre", seed=2602)

    steps = [
        ("system", "respiratory", GRID, INK2),
        ("organ", "lungs and pleura", GRID, INK2),
        ("structure", "lobes, fissures, hila", GRID, INK2),
        ("healthy first", "the normal lung", BLUE, INK),
        ("imaging modality", "radiograph, CT, ultrasound", GRID, INK2),
        ("pathology", "pneumonia, nodules", ORANGE, INK),
    ]
    n = len(steps)
    gap = 30
    bw = (W - 2 * MARGIN - (n - 1) * gap) / n
    y = 575
    xs = [MARGIN + i * (bw + gap) for i in range(n)]
    ax.text(MARGIN, 640, "the path", fontname="Poppins", fontsize=7.4, color=INK)
    for i, (x, (label, example, edge, colour)) in enumerate(zip(xs, steps)):
        pill(ax, x, y, bw, 52, label, edge=edge, colour=colour, size=6.6)
        ax.text(x + 18, y - 52, example, fontname="Poppins", fontsize=5.6,
                color=MUTED, va="center")
        if i < n - 1:
            arrow(ax, x + bw + 4, x + bw + gap - 4, y)

    # --- what a model adds, bracketed under the steps it serves ------------
    ax.text(MARGIN, 405, "what a model adds", fontname="Poppins", fontsize=7.4,
            color=INK)

    def bracket(i0, i1, yb, text, colour, sub):
        x0, x1 = xs[i0] + 8, xs[i1] + bw - 8
        ax.plot([x0, x0, x1, x1], [yb + 12, yb, yb, yb + 12], color=colour,
                lw=1.0, zorder=3)
        ax.scatter([x0 + 10], [yb - 30], s=46, facecolors="none", edgecolors=colour,
                   linewidths=1.1, zorder=4)
        ax.text(x0 + 30, yb - 30, text, fontname="Poppins", fontsize=6.4,
                color=INK2, va="center")
        ax.text(x0 + 30, yb - 56, sub, fontname="Poppins", fontsize=5.4,
                color=MUTED, va="center")

    bracket(1, 1, 355, "reconstruct in 3D", BLUE, "the organ, from CT or MRI")
    bracket(2, 2, 355, "recognise, segment", BLUE, "name it, trace its edge")
    bracket(3, 5, 355, "compare healthy and pathological", ORANGE,
            "what changes in shape, size, signal or texture")
    bracket(0, 5, 215, "classify labelled cases", INK2,
            "across the whole atlas, with the expert label always beside the output")

    ax.text(MARGIN, 108, "for learning anatomy and pathology  ·  never to say what a person has",
            fontname="Poppins", fontsize=6.2, color=INK2)

    save(fig, "02_learning_path.png")


# =============================================================================
#  FIGURE 03 — one specialist per organ
#  The atlas on the left, one small model per organ in the middle (one tile
#  per organ in the index), the levels of enrichment on the right. Tiles are
#  outlines: no model exists yet. The shared backbone is a closed, dashed door.
# =============================================================================
def fig03_specialists():
    systems, n_organs, _ = read_index()
    fig, ax = frame(
        "one specialist per organ",
        "a small model for each organ, loaded when that organ is studied. "
        "adding an organ never changes another.",
        f"design  ·  {n_organs} organs in CATALOGUE.md  ·  one model trained so far  ·  "
        "notebooks open, weights licensed model by model from their training data",
        glow="mousse", seed=2603)

    # --- left: the atlas ----------------------------------------------------
    lx, lw = MARGIN, 230
    ax.text(lx, 640, "the atlas", fontname="Poppins", fontsize=7.4, color=INK)
    shown = ["brain", "eye", "heart", "lungs and pleura", "liver and bile ducts",
             "kidneys", "spine", "skin"]
    active = "lungs and pleura"
    ys = [585 - i * 50 for i in range(len(shown))]
    for yy, name in zip(ys, shown):
        on = name == active
        pill(ax, lx, yy, lw, 38, name, edge=BLUE if on else GRID,
             colour=INK if on else INK2, size=6.0)
    ax.text(lx, ys[-1] - 48, f"… {n_organs} organs", fontname="Poppins",
            fontsize=5.8, color=MUTED, va="center")
    y_active = ys[shown.index(active)]

    # --- middle: the specialists, one tile per organ ------------------------
    gx, gy = 580, 585
    tcols, tw, th, tgap = 5, 50, 30, 12
    ax.text(gx, 640, "the specialists", fontname="Poppins", fontsize=7.4, color=INK)
    # tiles are unlabelled, one per organ: the lit one sits on the row of the
    # organ being studied, so the arrow never crosses another tile.
    row_active = min(range((n_organs - 1) // tcols + 1),
                     key=lambda r: abs(gy - r * (th + tgap) - y_active))
    k_active = row_active * tcols
    tile_active = None
    for k in range(n_organs):
        cx = gx + (k % tcols) * (tw + tgap)
        cy = gy - (k // tcols) * (th + tgap)
        on = k == k_active
        ax.add_patch(FancyBboxPatch((cx, cy - th / 2), tw, th,
                     boxstyle="round,pad=0,rounding_size=6", facecolor=PANEL,
                     edgecolor=BLUE if on else GRID, linewidth=1.1 if on else 0.8,
                     zorder=3))
        if on:
            tile_active = (cx, cy)
    grid_right = gx + tcols * (tw + tgap) - tgap
    grid_bottom = gy - ((n_organs - 1) // tcols) * (th + tgap) - th / 2

    tx, ty = tile_active
    ax.annotate("", xy=(tx - 6, ty), xytext=(lx + lw + 8, y_active), zorder=2,
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.9, alpha=0.85,
                                shrinkA=0, shrinkB=0, mutation_scale=7))
    ax.text(lx + lw + 22, max(ty, y_active) + 24, "loaded when studied",
            fontname="Poppins", fontsize=5.6, color=INK2, va="center")

    ax.text(gx, grid_bottom - 34, "one model, one notebook, one organ",
            fontname="Poppins", fontsize=5.8, color=INK2, va="center")
    pill(ax, gx, grid_bottom - 96, 330, 58, "", edge=GREY, dashed=True)
    ax.text(gx + 18, grid_bottom - 84, "shared backbone: kept closed", fontname="Poppins",
            fontsize=5.6, color=MUTED, va="center", zorder=4)
    ax.text(gx + 18, grid_bottom - 108, "opened only for a measured data gap",
            fontname="Poppins", fontsize=5.2, color=MUTED, va="center", zorder=4)

    # --- right: what the loaded specialist adds, level by level -------------
    rx, rw = 1000, W - MARGIN - 1000
    ax.text(rx, 640, "what it adds, level by level", fontname="Poppins",
            fontsize=7.4, color=INK)
    levels = [
        ("structure", "recognise and name", BLUE),
        ("structure", "segment its boundary", BLUE),
        ("organ", "reconstruct in 3D", BLUE),
        ("healthy vs pathological", "compare", ORANGE),
    ]
    rys = [585 - i * 78 for i in range(len(levels))]
    for yy, (level, action, colour) in zip(rys, levels):
        pill(ax, rx, yy, rw, 52, "", edge=GRID)
        ax.scatter([rx + 26], [yy], s=46, facecolors="none", edgecolors=colour,
                   linewidths=1.1, zorder=5)
        ax.text(rx + 50, yy + 10, action, fontname="Poppins", fontsize=6.4,
                color=INK, va="center", zorder=5)
        ax.text(rx + 50, yy - 12, level, fontname="Poppins", fontsize=5.2,
                color=MUTED, va="center", zorder=5)
    ax.plot([grid_right + 22, rx - 22], [tile_active[1], tile_active[1]],
            color=BLUE, lw=0.9, alpha=0.6, ls=(0, (2, 3)), zorder=2)
    ax.plot([rx - 22, rx - 22], [rys[-1], rys[0]], color=BLUE, lw=0.9, alpha=0.6,
            ls=(0, (2, 3)), zorder=2)

    ax.text(rx, rys[-1] - 72, "every output beside the dataset's expert label",
            fontname="Poppins", fontsize=6.0, color=INK2, va="center")
    ax.text(rx, rys[-1] - 100, "for learning, never for diagnosis", fontname="Poppins",
            fontsize=5.6, color=MUTED, va="center")

    save(fig, "03_specialists.png")


# =============================================================================
#  FIGURE 04 — the licences
#  One licence for the repository, one licence per model. The counts are the
#  weights ceilings of the register in CATALOGUE.md, read at run time. A
#  ceiling is a limit, not a grant: nothing here has been released.
# =============================================================================
CEILING_ROWS = [
    ("P", "cc0  ·  cc by  ·  mit  ·  open notices", "permissive, attribution where required"),
    ("SA", "cc by-sa", "share-alike, same licence"),
    ("NC", "cc by-nc  ·  nc-sa  ·  non-commercial terms", "non-commercial only"),
    ("X", "agreements  ·  credentials  ·  no derivatives", "not published without permission"),
    ("U", "missing  ·  conflicting  ·  per-source terms", "held back until confirmed"),
]


def read_ceilings():
    counts = {k: 0 for k, _, _ in CEILING_ROWS}
    header = None
    for line in open(CATALOGUE, encoding="utf-8"):
        if line.startswith("| Dataset |"):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            continue
        if header and re.match(r"^\| .+ \| \d{4}-\d{2}-\d{2} \|\s*$", line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            ceiling = cells[header.index("Weights ceiling")]
            if ceiling.startswith("Permissive"):
                counts["P"] += 1
            elif ceiling.startswith("Share-alike"):
                counts["SA"] += 1
            elif ceiling.startswith("Non-commercial"):
                counts["NC"] += 1
            elif ceiling.startswith(("Not shareable", "Not publishable", "None:", "Only under")):
                counts["X"] += 1
            elif ceiling.startswith(("Undetermined", "Depends")):
                counts["U"] += 1
            else:
                sys.exit(f"unclassified weights ceiling: {ceiling}")
    if not sum(counts.values()):
        sys.exit("no weights ceiling column found in CATALOGUE.md")
    return counts


def fig04_licences():
    counts = read_ceilings()
    total = sum(counts.values())
    fig, ax = frame(
        "the weights follow the data",
        "one licence for the repository. one licence per model, never wider than "
        "the data it was trained on.",
        f"weights ceilings of the {total} datasets in CATALOGUE.md, researched with their "
        "licences on 17 september 2026  ·  a project rule, not legal advice",
        glow="braise", seed=2604)

    # --- the repository -------------------------------------------------------
    ax.text(MARGIN, 640, "the repository", fontname="Poppins", fontsize=7.4, color=INK)
    pill(ax, MARGIN, 585, 560, 50, "code  ·  notebooks  ·  catalogue  ·  documents",
         edge=GRID, colour=INK2, size=6.2)
    arrow(ax, MARGIN + 572, MARGIN + 632, 585)
    ax.text(MARGIN + 650, 585, "one permissive licence for the whole project",
            fontname="Poppins", fontsize=6.4, color=INK, va="center")
    ax.plot([MARGIN, W - MARGIN], [520, 520], color=GRID, lw=0.8)

    # --- the weights ----------------------------------------------------------
    ax.text(MARGIN, 480, "the weights, one licence per model", fontname="Poppins",
            fontsize=7.4, color=INK)
    lx, lw_, rx, rw, bx = MARGIN, 440, 640, 400, 1110
    ax.text(lx, 440, "terms of the training data", fontname="Poppins", fontsize=5.6,
            color=MUTED, va="center")
    ax.text(rx, 440, "ceiling for the model's weights", fontname="Poppins", fontsize=5.6,
            color=MUTED, va="center")
    ax.text(bx, 440, "datasets in the index", fontname="Poppins", fontsize=5.6,
            color=MUTED, va="center")
    bmax = W - MARGIN - bx - 60
    top = max(counts.values())
    for i, (key, terms, ceiling) in enumerate(CEILING_ROWS):
        y = 390 - i * 58
        pill(ax, lx, y, lw_, 42, terms, edge=GRID, colour=INK2, size=5.8)
        arrow(ax, lx + lw_ + 10, rx - 10, y)
        pill(ax, rx, y, rw, 42, ceiling, edge=GRID, colour=INK, size=6.0)
        blen = max(4, bmax * counts[key] / top)
        ax.add_patch(FancyBboxPatch((bx, y - 6), blen, 12,
                     boxstyle="round,pad=0,rounding_size=4", facecolor=INK2,
                     edgecolor="none", alpha=0.55, zorder=3))
        ax.text(bx + blen + 14, y, str(counts[key]), fontname="Poppins", fontsize=6.0,
                color=INK2, va="center")

    ax.text(MARGIN, 100, "trained on several datasets, a model takes the most restrictive "
            "of their terms", fontname="Poppins", fontsize=6.2, color=INK2)

    save(fig, "04_licences.png")


# =============================================================================
#  BRAIN MODULE — organs/nervous-system/brain/
#  Two schematics. Every dataset name drawn here must be listed as Retained or
#  Companion in the module's DATASETS.md: the script stops otherwise, so a
#  figure can never show a choice the module no longer makes.
# =============================================================================
BRAIN_DIR = os.path.join(ROOT, "organs", "nervous-system", "brain")


def brain_retained():
    names = []
    for line in open(os.path.join(BRAIN_DIR, "DATASETS.md"), encoding="utf-8"):
        if line.startswith(("| **Retained**", "| **Companion**")):
            names.append(line.split("|")[2])
    if not names:
        sys.exit("no Retained or Companion rows found in the brain DATASETS.md")
    return names


def check_brain_names(shown):
    rows = brain_retained()
    for name in shown:
        if not any(name in r for r in rows):
            sys.exit(f"brain figure shows '{name}', which DATASETS.md does not retain")


BRAIN_USES = [
    # (short label, datasets as drawn, datasets as named in DATASETS.md)
    ("1 · healthy structures", ["Mindboggle-101", "Decathlon hippocampus"],
     ["Mindboggle-101", "Medical Segmentation Decathlon"]),
    ("2 · healthy vessels", ["TopCoW"], ["TopCoW"]),
    ("3 · classification", ["Cheng tumour set", "RSNA ICH 2019"],
     ["Cheng", "RSNA Intracranial Hemorrhage 2019"]),
    ("4 · lesion segmentation", ["BraTS · Decathlon", "ISLES 2022 · MSLesSeg"],
     ["BraTS", "ISLES 2022", "MSLesSeg", "MS3SEG"]),
    ("5 · 3D reconstruction", ["ICBM152 2009", "SPL/NAC atlas"],
     ["MNI ICBM152 2009", "Open Anatomy SPL/NAC brain atlas"]),
]

# rows, and what each use does on each row:
#   "N" healthy labels a person drew                     (blue, filled)
#   "A" healthy labels FreeSurfer produced, automatic     (blue, ring)
#   "P" pathology labels                                 (orange, filled)
#   "3" rebuilt in 3D from the 2D outputs                (ink ring)
BRAIN_ROWS = [
    ("the brain as a whole case", ["", "", "P", "", ""]),
    ("cerebral cortex", ["N", "", "", "P", "3"]),
    ("cerebral white matter", ["A", "", "", "P", "3"]),
    ("deep grey nuclei", ["A", "", "", "P", "3"]),
    ("hippocampus", ["N", "", "", "", "3"]),
    ("ventricles", ["A", "", "", "", "3"]),
    ("brainstem", ["A", "", "", "", "3"]),
    ("cerebellum", ["A", "", "", "", "3"]),
    ("arteries of the circle of Willis", ["", "N", "", "", "3"]),
]


def mark(ax, x, y, kind, s=46):
    if kind == "N":
        ax.scatter([x], [y], s=s, color=BLUE, zorder=4)
    elif kind == "A":
        ax.scatter([x], [y], s=s, facecolors="none", edgecolors=BLUE,
                   linewidths=1.1, zorder=4)
    elif kind == "P":
        ax.scatter([x], [y], s=s, color=ORANGE, zorder=4)
    elif kind == "3":
        ax.scatter([x], [y], s=s, facecolors="none", edgecolors=INK2,
                   linewidths=1.0, linestyle=(0, (1.5, 1.5)), zorder=4)


def fig05_brain_map():
    check_brain_names([n for _, _, names in BRAIN_USES for n in names])
    fig, ax = frame(
        "the brain, structure by structure",
        "eight structures and five uses, built in order. each use is its own model, "
        "trained on its own data.",
        "the plan  ·  retained datasets read from organs/nervous-system/brain/DATASETS.md  ·  "
        "use 1 is trained: see 03_use1_results",
        glow="acier", seed=2605)

    cols = [600 + i * 200 for i in range(len(BRAIN_USES))]
    for x, (label, shown, _) in zip(cols, BRAIN_USES):
        ax.text(x, 650, label, fontname="Poppins", fontsize=6.2, color=INK,
                ha="center", va="center")
        for k, name in enumerate(shown):
            ax.text(x, 624 - k * 20, name, fontname="Poppins", fontsize=5.0,
                    color=MUTED, ha="center", va="center")

    top, step = 552, 45
    for i, (name, marks) in enumerate(BRAIN_ROWS):
        y = top - i * step - (14 if i > 0 else 0)
        if i == 1:
            ax.plot([MARGIN, cols[-1] + 60], [y + step / 2 + 4, y + step / 2 + 4],
                    color=GRID, lw=0.8)
        ax.text(MARGIN, y, name, fontname="Poppins", fontsize=6.0,
                color=INK if i == 0 else INK2, va="center")
        ax.plot([MARGIN + 330, cols[-1] + 60], [y, y], color=GRID, lw=0.5,
                alpha=0.6, zorder=1)
        for x, m in zip(cols, marks):
            if m:
                mark(ax, x, y, m)

    ly = 108
    items = [("N", "healthy labels drawn by a person"),
             ("A", "healthy labels from FreeSurfer, automatic"),
             ("P", "pathology labels"),
             ("3", "rebuilt in 3D from the 2D outputs")]
    lx = MARGIN
    for kind, text in items:
        mark(ax, lx + 6, ly, kind, s=36)
        ax.text(lx + 22, ly, text, fontname="Poppins", fontsize=5.6, color=INK2,
                va="center")
        lx += 22 + len(text) * 8.6 + 40

    save(fig, "01_structures_and_uses.png", subdir="brain")


def fig06_brain_healthy_to_lesion():
    check_brain_names(["Mindboggle-101", "TopCoW", "BraTS", "ISLES 2022", "MSLesSeg",
                       "MS3SEG", "Cheng", "RSNA Intracranial Hemorrhage 2019",
                       "MNI ICBM152 2009"])
    fig, ax = frame(
        "every lesion is read against the healthy brain",
        "use 1 comes first. each lesion is then shown among the healthy structures "
        "it sits in, with its expert label beside it.",
        "schematic  ·  datasets from organs/nervous-system/brain/DATASETS.md  ·  only use 1 "
        "is trained so far  ·  for learning, never to say what a person has",
        glow="braise", seed=2606)

    # --- left: the healthy reference ----------------------------------------
    lx, lw = MARGIN, 320
    ax.text(lx, 640, "the healthy brain", fontname="Poppins", fontsize=7.4, color=INK)
    ax.add_patch(FancyBboxPatch((lx, 300), lw, 300,
                 boxstyle="round,pad=0,rounding_size=12", facecolor=PANEL,
                 edgecolor=BLUE, linewidth=1.0, zorder=3))
    ax.text(lx + 20, 572, "use 1  ·  structures", fontname="Poppins", fontsize=6.2,
            color=INK, va="center", zorder=4)
    for k, s in enumerate(["cortex, white matter", "deep grey nuclei, hippocampus",
                           "ventricles, brainstem, cerebellum"]):
        ax.text(lx + 20, 536 - k * 30, s, fontname="Poppins", fontsize=5.8,
                color=INK2, va="center", zorder=4)
    ax.plot([lx + 20, lx + lw - 20], [432, 432], color=GRID, lw=0.8, zorder=4)
    ax.text(lx + 20, 404, "use 2  ·  named arteries", fontname="Poppins", fontsize=6.2,
            color=INK, va="center", zorder=4)
    ax.text(lx + 20, 372, "circle of Willis", fontname="Poppins", fontsize=5.8,
            color=INK2, va="center", zorder=4)
    ax.text(lx + 20, 326, "Mindboggle-101  ·  TopCoW", fontname="Poppins", fontsize=5.0,
            color=MUTED, va="center", zorder=4)

    # --- middle: the lesions, as labelled ------------------------------------
    mx, mw = 600, 460
    ax.text(mx, 640, "the lesion, as labelled", fontname="Poppins", fontsize=7.4,
            color=INK)
    lesions = [
        ("tumour sub-regions", "MRI", "BraTS  ·  Decathlon", "4"),
        ("ischaemic stroke", "MRI", "ISLES 2022", "4"),
        ("multiple sclerosis", "MRI", "MSLesSeg  ·  MS3SEG", "4"),
        ("tumour type", "MRI", "Cheng tumour set", "3"),
        ("haemorrhage", "CT", "RSNA ICH 2019", "3"),
    ]
    ys = [578 - i * 66 for i in range(len(lesions))]
    for y, (name, mod, data, use) in zip(ys, lesions):
        pill(ax, mx, y, mw, 46, "", edge=ORANGE if use == "4" else GRID)
        ax.text(mx + 18, y + 8, name, fontname="Poppins", fontsize=6.2, color=INK,
                va="center", zorder=5)
        ax.text(mx + 18, y - 12, f"use {use}  ·  {mod}", fontname="Poppins",
                fontsize=5.0, color=MUTED, va="center", zorder=5)
        ax.text(mx + mw - 18, y, data, fontname="Poppins", fontsize=5.4, color=INK2,
                va="center", ha="right", zorder=5)
        ax.annotate("", xy=(mx - 6, y), xytext=(lx + lw + 6, 450), zorder=2,
                    arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.8, alpha=0.55,
                                    shrinkA=0, shrinkB=0, mutation_scale=6))
    ax.text(mx, ys[-1] - 50, "orange edge: outlined (use 4)   ·   grey edge: classified, "
            "one label per case (use 3)", fontname="Poppins", fontsize=5.4, color=MUTED,
            va="center")

    # --- right: what the student compares ------------------------------------
    rx = 1140
    ax.text(rx, 640, "what a student compares", fontname="Poppins", fontsize=7.4,
            color=INK)
    for k, s in enumerate(["which healthy structures it sits in",
                           "what it displaces or replaces",
                           "how its signal differs from healthy tissue",
                           "the expert label beside every output"]):
        y = 578 - k * 66
        ax.scatter([rx + 8], [y], s=40, facecolors="none",
                   edgecolors=ORANGE if k < 3 else INK2, linewidths=1.1, zorder=4)
        ax.text(rx + 28, y, s, fontname="Poppins", fontsize=5.8, color=INK2,
                va="center")

    # --- bottom: then in 3D -----------------------------------------------------
    ax.plot([MARGIN, W - MARGIN], [170, 170], color=GRID, lw=0.8)
    mark(ax, MARGIN + 8, 132, "3", s=40)
    ax.text(MARGIN + 28, 132, "then in 3D (use 5): lesion and healthy structures rebuilt "
            "together, placed in the MNI ICBM152 2009 reference space",
            fontname="Poppins", fontsize=6.0, color=INK2, va="center")

    save(fig, "02_healthy_to_lesion.png", subdir="brain")


# =============================================================================
#  FIGURE 07 — brain use 1, what the optimised run scored
#  Every number is read from the run's own record, results_t4.json, so the
#  figure cannot drift from the notebook or the model card. One dot per
#  held-out subject: the spread is the point, not the average.
# =============================================================================
def fig07_brain_use1_results():
    path = os.path.join(BRAIN_DIR, "healthy-structure-segmentation", "results_t4.json")
    if not os.path.exists(path):
        sys.exit(f"no run record at {path}")
    with open(path, encoding="utf-8") as fh:
        res = json.load(fh)
    rows = sorted(res["structures"], key=lambda s: -s["mean_dice"])
    cols = res["per_subject_dice"]["columns"]
    table = res["per_subject_dice"]["rows"]
    run, cfg_run, split = res["run"], res["config"], res["split"]
    outlier = min(table, key=lambda n: sum(table[n]) / len(table[n]))

    fig, ax = frame(
        "what the small model found, structure by structure",
        f"one run on a {run['environment']['device']}: {split['train_subjects']} brains to "
        f"train, {split['held_out_subjects']} held out. one dot per held-out brain.",
        f"Dice on sampled axial slices  ·  {cfg_run['parameters']:,d} parameters, seed "
        f"{run['seed']}  ·  Mindboggle-101 {res['dataset']['doi']}  ·  "
        "no clinical claim, nothing about any person",
        glow="mousse", seed=2607)

    x0, x1 = 620, 1430                      # Dice 0.0 at x0, 1.0 at x1: the full range
    def X(d):
        return x0 + (x1 - x0) * d

    top, step = 588, 40
    for k in range(6):                      # axis first, under the dots
        d = k * 0.2
        ax.plot([X(d), X(d)], [top + 26, top - (len(rows) - 1) * step - 22],
                color=GRID, lw=0.8, zorder=1)
        ax.text(X(d), top + 38, f"{d:.1f}", fontname="Poppins", fontsize=5.4,
                color=MUTED, ha="center")
    ax.text(X(0.5), top + 62, "Dice overlap with the dataset's labels", fontname="Poppins",
            fontsize=6.0, color=INK2, ha="center")

    for i, row in enumerate(rows):
        y = top - i * step
        manual = row["provenance"].startswith("manual")
        colour = BLUE if manual else INK2
        ax.text(MARGIN, y, row["name"], fontname="Poppins", fontsize=6.2,
                color=INK if manual else INK2, va="center")
        ax.text(MARGIN + 300, y, f"{row['mean_dice']:.3f}", fontname="Poppins",
                fontsize=6.2, color=INK if manual else INK2, va="center", ha="right")
        ax.text(MARGIN + 320, y, "drawn by a person" if manual else "FreeSurfer",
                fontname="Poppins", fontsize=5.0, color=MUTED, va="center")
        j = cols.index(row["name"])
        for name, values in table.items():
            if name == outlier:
                ax.scatter([X(values[j])], [y], s=34, facecolors="none", edgecolors=MUTED,
                           linewidths=1.0, zorder=4)
            else:
                ax.scatter([X(values[j])], [y], s=16, color=colour, alpha=0.55, zorder=3)
        ax.scatter([X(row["mean_dice"])], [y], s=58, color=colour, zorder=5)

    ly = 132
    ax.scatter([MARGIN + 6], [ly], s=58, color=BLUE)
    ax.text(MARGIN + 22, ly, "mean, manual labels", fontname="Poppins", fontsize=5.6,
            color=INK2, va="center")
    ax.scatter([MARGIN + 246], [ly], s=58, color=INK2)
    ax.text(MARGIN + 262, ly, "mean, FreeSurfer labels", fontname="Poppins", fontsize=5.6,
            color=INK2, va="center")
    ax.scatter([MARGIN + 516], [ly], s=16, color=INK2, alpha=0.55)
    ax.text(MARGIN + 532, ly, "one held-out brain", fontname="Poppins", fontsize=5.6,
            color=INK2, va="center")
    ax.scatter([MARGIN + 736], [ly], s=34, facecolors="none", edgecolors=MUTED, linewidths=1.0)
    ax.text(MARGIN + 752, ly, f"{outlier}, a template brain, unlike the others",
            fontname="Poppins", fontsize=5.6, color=INK2, va="center")

    ax.text(MARGIN, 92, "a score against FreeSurfer's labels means agreement with "
            "FreeSurfer, not correctness", fontname="Poppins", fontsize=6.0, color=INK2)

    save(fig, "03_use1_results.png", subdir="brain")


FIGURES = [fig01_atlas_map, fig02_learning_path, fig03_specialists, fig04_licences,
           fig05_brain_map, fig06_brain_healthy_to_lesion,
           fig07_brain_use1_results]

if __name__ == "__main__":
    for f in FIGURES:
        f()
