#!/usr/bin/env python3
"""Brain, use 2: the cerebral vessel network of a healthy brain.

    Body Atlas Models — for learning anatomy, never for diagnosis.
    Healthy subjects only. No clinical claim. No patient data anywhere in this run.

What this trains
----------------
A residual 3D U-Net with a single sigmoid output: vessel or not vessel, on
Time-of-Flight MR angiography. One hundred healthy adults from the IXI cohort,
with vessel masks refined by hand under three neurovascular surgeons
(doi:10.5281/zenodo.17393202, CC BY 4.0), over the IXI images themselves
(CC BY-SA 3.0).

Unlike use 1 there is no pre-training stage and no patient data: every brain
here is a healthy volunteer, and the only labels are the manual ones. Five
folds, so each of the hundred is scored exactly once by a model that never saw
it, then one last model on all hundred — the one delivered for this use.

The labels are binary. They do not name the arteries, and neither does this
model. No public dataset carries named artery labels on healthy subjects; the
only source that does, TopCoW, was built from stroke-centre patients. See
DATASETS.md.

The rarity is the whole problem
-------------------------------
Vessels take 0.261 % of a volume on average — rarer than every structure of
use 1 except the cerebellar vermis, which that run lost entirely the one time
its rarity was not designed for from the start. So here, from the first line:
patches are drawn on vessel voxels most of the time, the loss weights the thin
shell of background around each vessel, and the score that decides anything is
never Dice alone.

What it reports
---------------
Per subject and over the held-out folds: Dice, centreline Dice (clDice, which
a broken vessel tree fails even when Dice looks fine), and the two boundary
distances in millimetres read from the NIfTI affine — Hausdorff-95 and the
average symmetric surface distance. None of them is ever optimised directly.

Licences
--------
Labels CC BY 4.0, images CC BY-SA 3.0. The stricter governs, so the weights of
this model may be published under share-alike — the first use of the atlas
whose weights are not held back. That holds only as long as nothing with
heavier terms enters the training set.

Usage
-----
    pip install nibabel scikit-image
    python kaggle_train.py                 # the whole thing, self-timed
    python kaggle_train.py --smoke         # a few minutes on a CPU
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import tarfile
import time
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

# --------------------------------------------------------------------------- #
# 1. The two sources, by identifier and checksum
# --------------------------------------------------------------------------- #
LABELS_DOI = "10.5281/zenodo.17393202"
LABELS_RECORD = "17393202"
LABELS_FILE = "vessel_dataset.zip"
LABELS_MD5 = "96be3dd9d1413e8890f89721829a79f7"
LABELS_BYTES = 6580597

IMAGES_URL = "https://biomedic.doc.ic.ac.uk/brain-development/downloads/IXI/IXI-MRA.tar"
IMAGES_TOTAL = 12377712640
IMAGES_LICENCE = "CC BY-SA 3.0"

# The tar is uncompressed and the server honours byte ranges, so the hundred
# members we need are pulled directly instead of the 12.4 GB archive. The index
# (member -> offset, size) is built once and committed beside this script.
INDEX_FILE = "ixi_mra_index.json"

# One subject of the hundred is also in TopCoW's external test set (MRA_IXI_HH).
# Nothing from TopCoW is used here, so it changes nothing for this run — but any
# later comparison against TopCoW labels must drop it, or the same brain sits on
# both sides of the comparison.
TOPCOW_OVERLAP = ["IXI057"]


@dataclass
class Config:
    seed: int = 20261009
    patch: tuple = (128, 128, 64)   # x, y, z — z is only 100 voxels deep
    base_channels: int = 12
    depth: int = 4
    batch_size: int = 2
    accum: int = 2
    lr: float = 2e-3
    weight_decay: float = 1e-4
    warmup_frac: float = 0.03
    dice_weight: float = 1.0
    bce_pos_weight: float = 8.0     # Dice carries the imbalance; BCE only helps
    boundary_alpha: float = 4.0     # weight at the vessel surface is 1 + alpha
    boundary_tau: float = 1.5       # millimetres
    vessel_patch_frac: float = 0.7  # patches centred on a vessel voxel
    amp: bool = True
    fold_minutes: float = 25.0
    folds: int = 5
    final_model: bool = True
    val_subjects: int = 8           # inside each fold's training pool
    val_patches: int = 160
    checks: int = 10
    warmup_steps: int = 30
    calib_steps: int = 30
    overlap: float = 0.5
    crop_limit: int = 0
    out_dir: str = "out_use2"


def parse_args():
    cfg = Config()
    p = argparse.ArgumentParser(description="brain use 2: the healthy vessel network")
    p.add_argument("--work-dir", default="ixi")
    p.add_argument("--labels-root", default=None, help="an existing vessel_dataset directory")
    p.add_argument("--images-root", default=None, help="a directory of IXI*-MRA.nii.gz")
    p.add_argument("--index", default=None, help="path to " + INDEX_FILE)
    p.add_argument("--reuse-data", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--no-final-model", action="store_true")
    for name, value in asdict(cfg).items():
        if isinstance(value, tuple):
            p.add_argument(f"--{name.replace('_', '-')}", nargs=3, type=int, default=value)
        else:
            p.add_argument(f"--{name.replace('_', '-')}", type=type(value), default=value)
    a = p.parse_args()
    cfg = Config(**{k: (tuple(getattr(a, k)) if isinstance(getattr(Config, k, None), tuple)
                        or isinstance(asdict(cfg)[k], tuple) else getattr(a, k))
                    for k in asdict(cfg)})
    if a.no_final_model:
        cfg.final_model = False
    if a.smoke:
        cfg.patch = (64, 64, 32)
        cfg.base_channels, cfg.depth = 4, 3
        cfg.fold_minutes, cfg.folds, cfg.val_subjects = 0.4, 2, 1
        cfg.val_patches, cfg.checks = 12, 2
        cfg.warmup_steps, cfg.calib_steps = 5, 5
        cfg.amp = False
        if cfg.out_dir == Config().out_dir:
            cfg.out_dir = "out_use2_smoke"
    return cfg, a


def sha256_of_self() -> str:
    try:
        return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    except Exception:
        return "unknown"


def md5_of(path: Path, block: int = 1 << 20) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        while chunk := fh.read(block):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------- #
# 2. Fetching: the labels whole, the images member by member
# --------------------------------------------------------------------------- #
def http_range(url: str, start: int, length: int, attempts: int = 5) -> bytes:
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(
                url, headers={"Range": f"bytes={start}-{start + length - 1}"})
            with urllib.request.urlopen(req, timeout=180) as r:
                buf = bytearray()
                while chunk := r.read(1 << 20):
                    buf += chunk
                if len(buf) == length:
                    return bytes(buf)
        except Exception as exc:
            print(f"    range {start}: {type(exc).__name__}, retry {attempt}/{attempts}",
                  flush=True)
        time.sleep(2 * attempt)
    raise RuntimeError(f"could not read {length} bytes at {start}")


def fetch_labels(work: Path) -> Path:
    work.mkdir(parents=True, exist_ok=True)
    zp = work / LABELS_FILE
    if not (zp.exists() and zp.stat().st_size == LABELS_BYTES):
        print(f"  fetching {LABELS_FILE} ({LABELS_BYTES / 1e6:.1f} MB) from Zenodo "
              f"{LABELS_DOI}", flush=True)
        url = f"https://zenodo.org/api/records/{LABELS_RECORD}/files/{LABELS_FILE}/content"
        with urllib.request.urlopen(url, timeout=300) as r, open(zp, "wb") as fh:
            while chunk := r.read(1 << 20):
                fh.write(chunk)
    got = md5_of(zp)
    print(f"  {'ok' if got == LABELS_MD5 else 'MISMATCH':8s} {LABELS_FILE}  {got}", flush=True)
    if got != LABELS_MD5:
        raise RuntimeError(f"{LABELS_FILE}: md5 {got} is not the record's {LABELS_MD5}")
    out = work / "labels"
    if not (out / "vessel_dataset").is_dir():
        with zipfile.ZipFile(zp) as zf:
            zf.extractall(out)
    return out / "vessel_dataset"


def fetch_images_streaming(work: Path, wanted: list) -> Path:
    """Fallback with no index: stream the archive once and keep only what we need.

    Costs the whole 12.4 GB instead of 1.5, but depends on nothing but the URL.
    """
    out = work / "images"
    out.mkdir(parents=True, exist_ok=True)
    want = set(wanted)
    print(f"  no index: streaming the whole {IMAGES_TOTAL / 1e9:.1f} GB archive and "
          f"keeping {len(want)} members", flush=True)
    kept, t0 = 0, time.time()
    with urllib.request.urlopen(IMAGES_URL, timeout=600) as r:
        with tarfile.open(fileobj=r, mode="r|") as tf:
            for member in tf:
                sid = member.name[:6]
                if sid in want and member.isfile():
                    data = tf.extractfile(member).read()
                    (out / f"{sid}.nii.gz").write_bytes(data)
                    kept += 1
                    if kept % 20 == 0 or kept == len(want):
                        print(f"    {kept}/{len(want)} kept ({time.time() - t0:.0f}s)",
                              flush=True)
                if kept == len(want):
                    break
    return out


def fetch_images(work: Path, index: dict, wanted: list) -> Path:
    """Pull only the members we need out of the remote tar, by byte range."""
    out = work / "images"
    out.mkdir(parents=True, exist_ok=True)
    todo = [(sid, index[sid]) for sid in wanted if sid in index]
    missing = [s for s in wanted if s not in index]
    if missing:
        raise RuntimeError(f"no tar entry for {missing}")
    total = sum(v[2] for _, v in todo)
    print(f"  {len(todo)} members to pull, {total / 1e9:.2f} GB of the "
          f"{IMAGES_TOTAL / 1e9:.1f} GB archive ({100 * total / IMAGES_TOTAL:.0f} %)",
          flush=True)
    t0, done = time.time(), 0
    for n, (sid, (name, off, size)) in enumerate(todo, 1):
        dest = out / f"{sid}.nii.gz"
        if dest.exists() and dest.stat().st_size == size:
            done += size
            continue
        dest.write_bytes(http_range(IMAGES_URL, off, size))
        done += size
        if n % 10 == 0 or n == len(todo):
            el = time.time() - t0
            print(f"    {n}/{len(todo)}  {done / 1e9:.2f} GB  {done / 1e6 / max(el, 1e-9):.1f} MB/s",
                  flush=True)
    return out


# --------------------------------------------------------------------------- #
# 3. One subject, prepared once
# --------------------------------------------------------------------------- #
def boundary_weight(mask: np.ndarray, zooms, cfg: Config) -> np.ndarray:
    """1 + alpha*exp(-d/tau), d = mm to the nearest vessel surface.

    For a thin structure almost every vessel voxel is already a surface voxel, so
    what this really buys is the shell of BACKGROUND just outside each vessel —
    where the false positives live. That is the point.
    """
    from scipy import ndimage
    if not mask.any():
        return np.zeros(mask.shape, np.uint8)
    inner = ndimage.binary_erosion(mask, ndimage.generate_binary_structure(3, 1),
                                   border_value=0)
    surface = mask & ~inner
    if not surface.any():
        surface = mask
    d = ndimage.distance_transform_edt(~surface, sampling=zooms)
    w = np.exp(-d / max(cfg.boundary_tau, 1e-6))
    return np.clip(np.rint(w * 255), 0, 255).astype(np.uint8)


def prepare_subject(sid: str, image_path: Path, label_path: Path, cfg: Config):
    import nibabel as nib

    img = nib.as_closest_canonical(nib.load(str(image_path)))
    lab = nib.as_closest_canonical(nib.load(str(label_path)))
    vol = np.asarray(img.dataobj, np.float32)
    y = np.asarray(lab.dataobj)
    # one of the hundred is stored as float32 where the rest are int16; the values
    # are the same, so cast rather than special-case it
    y = (np.asarray(y) > 0.5).astype(np.uint8)
    if y.shape != vol.shape:
        raise RuntimeError(f"{sid}: label {y.shape} does not match image {vol.shape}")
    zooms = tuple(float(z) for z in img.header.get_zooms()[:3])

    head = vol > np.percentile(vol, 60)          # TOF has no skull strip: use signal
    box = []
    for axis, p in enumerate(cfg.patch):
        on = np.any(head, axis=tuple(a for a in range(3) if a != axis))
        lo, hi = int(np.argmax(on)), int(len(on) - np.argmax(on[::-1]))
        lo, hi = max(lo - 4, 0), min(hi + 4, head.shape[axis])
        if hi - lo < p:
            lo = max(lo - (p - (hi - lo)) // 2, 0)
            hi = min(lo + p, head.shape[axis])
            lo = max(hi - p, 0)
        box.append((lo, hi))
    if cfg.crop_limit:
        box = [(max(0, (lo + hi) // 2 - cfg.crop_limit // 2),
                min(head.shape[a], max(0, (lo + hi) // 2 - cfg.crop_limit // 2)
                    + max(cfg.crop_limit, cfg.patch[a])))
               for a, (lo, hi) in enumerate(box)]
    sl = tuple(slice(lo, hi) for lo, hi in box)

    inside = vol[sl]
    lo_i, hi_i = np.percentile(inside, (1, 99.5))   # TOF is bright and long-tailed
    image = np.clip((inside - lo_i) / max(hi_i - lo_i, 1e-6), 0, 1)
    image = np.rint(image * 255).astype(np.uint8)
    truth = y[sl]

    out = dict(name=sid, zooms=zooms, box=box, shape=image.shape, image=image,
               truth=truth, weight=boundary_weight(truth.astype(bool), zooms, cfg),
               vessel_voxels=int(truth.sum()),
               vessel_fraction=float(truth.mean()))

    rng = np.random.default_rng(cfg.seed + int(sid[3:]))
    flat = truth.reshape(-1)
    vox = np.flatnonzero(flat)
    take = vox if vox.size <= 6000 else rng.choice(vox, 6000, replace=False)
    out["vessel_centres"] = np.asarray(np.unravel_index(take, truth.shape)).T.astype(np.int16)
    tis = np.flatnonzero(image.reshape(-1) > 40)
    take = tis if tis.size <= 6000 else rng.choice(tis, 6000, replace=False)
    out["tissue_centres"] = np.asarray(np.unravel_index(take, image.shape)).T.astype(np.int16)
    return out


class PatchSet:
    """Patches, drawn on vessels most of the time because vessels are 0.26 % of a brain."""

    def __init__(self, subjects: list, cfg: Config, name: str):
        self.subjects, self.cfg, self.name = subjects, cfg, name
        self.rng = np.random.default_rng(cfg.seed + len(name))
        tot = sum(s["truth"].size for s in subjects)
        self.share = sum(s["vessel_voxels"] for s in subjects) / max(tot, 1)

    def draw(self, rng=None):
        rng = rng or self.rng
        sub = self.subjects[rng.integers(len(self.subjects))]
        on_vessel = rng.random() < self.cfg.vessel_patch_frac and len(sub["vessel_centres"])
        pts = sub["vessel_centres"] if on_vessel else sub["tissue_centres"]
        centre = pts[rng.integers(len(pts))].astype(np.int64)
        start = []
        for axis, p in enumerate(self.cfg.patch):
            jitter = int(rng.integers(-p // 5, p // 5 + 1))
            lo = int(centre[axis]) - p // 2 + jitter
            start.append(max(0, min(lo, sub["shape"][axis] - p)))
        sl = tuple(slice(lo, lo + p) for lo, p in zip(start, self.cfg.patch))
        return (sub["image"][sl].astype(np.float32) / 255.0,
                sub["truth"][sl].astype(np.float32),
                sub["weight"][sl].astype(np.float32) / 255.0)

    def fixed_set(self, n: int):
        rng = np.random.default_rng(self.cfg.seed + 7)
        return [self.draw(rng) for _ in range(n)]


# --------------------------------------------------------------------------- #
# 4. The model: the same residual 3D U-Net as use 1, with one output
# --------------------------------------------------------------------------- #
def build_model(cfg: Config):
    import torch
    import torch.nn as nn

    class ResBlock(nn.Module):
        def __init__(self, cin, cout):
            super().__init__()
            self.a = nn.Sequential(nn.Conv3d(cin, cout, 3, padding=1, bias=False),
                                   nn.InstanceNorm3d(cout, affine=True),
                                   nn.LeakyReLU(0.01, inplace=True))
            self.b = nn.Sequential(nn.Conv3d(cout, cout, 3, padding=1, bias=False),
                                   nn.InstanceNorm3d(cout, affine=True))
            self.skip = nn.Identity() if cin == cout else nn.Conv3d(cin, cout, 1, bias=False)
            self.act = nn.LeakyReLU(0.01, inplace=True)

        def forward(self, x):
            return self.act(self.b(self.a(x)) + self.skip(x))

    class UNet3D(nn.Module):
        def __init__(self):
            super().__init__()
            w = [cfg.base_channels * 2 ** i for i in range(cfg.depth + 1)]
            self.enc = nn.ModuleList()
            c = 1
            for x in w[:-1]:
                self.enc.append(ResBlock(c, x)); c = x
            self.bot = ResBlock(w[-2], w[-1])
            self.up, self.dec = nn.ModuleList(), nn.ModuleList()
            c = w[-1]
            for x in reversed(w[:-1]):
                self.up.append(nn.ConvTranspose3d(c, x, 2, 2))
                self.dec.append(ResBlock(2 * x, x)); c = x
            self.head = nn.Conv3d(w[0], 1, 1)       # one logit: vessel or not
            self.pool = nn.MaxPool3d(2)

        def forward(self, x):
            sk = []
            for e in self.enc:
                x = e(x); sk.append(x); x = self.pool(x)
            x = self.bot(x)
            for u, d, s in zip(self.up, self.dec, reversed(sk)):
                x = d(torch.cat([u(x), s], 1))
            return self.head(x)

    return UNet3D()


def augment(x, y, w, cfg: Config, gen):
    """x (N,1,D,H,W); y and w (N,D,H,W). Flip is left-right only."""
    import torch
    import torch.nn.functional as F

    n, dev = x.shape[0], x.device
    flip = torch.rand(n, device=dev, generator=gen) < 0.5
    if flip.any():
        x[flip] = torch.flip(x[flip], dims=[2])
        y[flip] = torch.flip(y[flip], dims=[1])
        w[flip] = torch.flip(w[flip], dims=[1])
    ang = (torch.rand(n, 3, device=dev, generator=gen) * 2 - 1) * math.radians(8.0)
    sc = 1 + (torch.rand(n, 1, device=dev, generator=gen) * 2 - 1) * 0.08
    sh = (torch.rand(n, 3, device=dev, generator=gen) * 2 - 1) * 0.04
    cx, sx = torch.cos(ang[:, 0]), torch.sin(ang[:, 0])
    cy, sy = torch.cos(ang[:, 1]), torch.sin(ang[:, 1])
    cz, sz = torch.cos(ang[:, 2]), torch.sin(ang[:, 2])
    z0, o1 = torch.zeros_like(cx), torch.ones_like(cx)
    rx = torch.stack([o1, z0, z0, z0, cx, -sx, z0, sx, cx], 1).view(n, 3, 3)
    ry = torch.stack([cy, z0, sy, z0, o1, z0, -sy, z0, cy], 1).view(n, 3, 3)
    rz = torch.stack([cz, -sz, z0, sz, cz, z0, z0, z0, o1], 1).view(n, 3, 3)
    theta = torch.cat([(rz @ ry @ rx) / sc.view(n, 1, 1), sh.view(n, 3, 1)], 2)
    grid = F.affine_grid(theta, list(x.shape), align_corners=False)
    x = F.grid_sample(x, grid, mode="bilinear", padding_mode="zeros", align_corners=False)
    pair = torch.stack([y, w], 1)
    pair = F.grid_sample(pair, grid, mode="nearest", padding_mode="zeros",
                         align_corners=False)
    y, w = pair[:, 0], pair[:, 1]
    g = torch.exp((torch.rand(n, 1, 1, 1, 1, device=dev, generator=gen) * 2 - 1) * 0.2)
    x = x.clamp(0, 1) ** g
    x = x + torch.randn(x.shape, device=dev, generator=gen) * 0.02
    return x.clamp(0, 1), y, w


def make_loss(cfg: Config, device):
    import torch
    import torch.nn.functional as F
    pos = torch.tensor(cfg.bce_pos_weight, device=device)

    def loss_fn(logits, y, w):
        logits = logits[:, 0]
        bce = F.binary_cross_entropy_with_logits(logits, y, pos_weight=pos,
                                                 reduction="none")
        weight = 1.0 + cfg.boundary_alpha * w
        bce = (bce * weight).sum() / weight.sum().clamp(min=1)
        p = torch.sigmoid(logits)
        inter = (p * y).sum()
        dice = (2 * inter + 1.0) / (p.sum() + y.sum() + 1.0)
        return bce + cfg.dice_weight * (1 - dice)

    return loss_fn


# --------------------------------------------------------------------------- #
# 5. Inference over a whole brain, and the metrics that decide anything
# --------------------------------------------------------------------------- #
def gaussian_window(shape, device):
    import torch
    gs = []
    for n in shape:
        t = torch.linspace(-1, 1, n, device=device)
        gs.append(torch.exp(-(t ** 2) / (2 * 0.25)))
    return (gs[0][:, None, None] * gs[1][None, :, None] * gs[2][None, None, :]).clamp_min(1e-3)


def predict_volume(model, sub, cfg: Config, device, threshold: float = 0.5):
    import torch
    p = cfg.patch
    stride = [max(1, int(round(s * (1 - cfg.overlap)))) for s in p]
    shape = sub["shape"]
    starts = []
    for axis in range(3):
        pos = list(range(0, max(shape[axis] - p[axis], 0) + 1, stride[axis]))
        if pos[-1] != shape[axis] - p[axis]:
            pos.append(max(shape[axis] - p[axis], 0))
        starts.append(pos)

    acc = torch.zeros(tuple(shape), dtype=torch.float32, device=device)
    norm = torch.zeros(tuple(shape), dtype=torch.float32, device=device)
    win = gaussian_window(p, device)
    image = torch.from_numpy(sub["image"].astype(np.float32) / 255.0)
    model.eval()
    batch, coords = [], []

    def flush():
        if not batch:
            return
        x = torch.stack(batch).unsqueeze(1).to(device)
        with torch.no_grad(), torch.autocast("cuda", enabled=(cfg.amp and device.type == "cuda")):
            out = torch.sigmoid(model(x).float())[:, 0]
        for k, (i, j, l) in enumerate(coords):
            acc[i:i + p[0], j:j + p[1], l:l + p[2]] += out[k] * win
            norm[i:i + p[0], j:j + p[1], l:l + p[2]] += win
        batch.clear(); coords.clear()

    for i in starts[0]:
        for j in starts[1]:
            for l in starts[2]:
                batch.append(image[i:i + p[0], j:j + p[1], l:l + p[2]])
                coords.append((i, j, l))
                if len(batch) == max(1, cfg.batch_size * 2):
                    flush()
    flush()
    prob = (acc / norm.clamp_min(1e-6)).cpu().numpy()
    return (prob >= threshold).astype(np.uint8), prob


def surface_distances(a: np.ndarray, b: np.ndarray, zooms):
    from scipy import ndimage
    if not a.any() or not b.any():
        return None
    union = a | b
    box = []
    for axis in range(3):
        on = np.any(union, axis=tuple(k for k in range(3) if k != axis))
        lo, hi = int(np.argmax(on)), int(len(on) - np.argmax(on[::-1]))
        box.append(slice(max(lo - 2, 0), min(hi + 2, union.shape[axis])))
    box = tuple(box)
    st = ndimage.generate_binary_structure(3, 1)
    sa = a[box] & ~ndimage.binary_erosion(a[box], st, border_value=0)
    sb = b[box] & ~ndimage.binary_erosion(b[box], st, border_value=0)
    if not sa.any() or not sb.any():
        return None
    da = ndimage.distance_transform_edt(~sa, sampling=zooms)
    db = ndimage.distance_transform_edt(~sb, sampling=zooms)
    both = np.concatenate([db[sa], da[sb]])
    return dict(assd_mm=float(both.mean()), hd95_mm=float(np.percentile(both, 95)),
                hd_mm=float(both.max()))


def cl_dice(pred: np.ndarray, truth: np.ndarray):
    """Centreline Dice: does the NETWORK survive, not just the overlap.

    A model that drops a whole branch can still score well on Dice, because the
    branch is a handful of voxels. clDice asks instead how much of the truth's
    skeleton lies inside the prediction, and how much of the prediction's
    skeleton lies inside the truth. A broken tree fails it.
    """
    try:
        from skimage.morphology import skeletonize
    except Exception:
        return None
    if not pred.any() or not truth.any():
        return None
    sp = skeletonize(pred.astype(bool))
    st = skeletonize(truth.astype(bool))
    if not sp.any() or not st.any():
        return None
    tprec = float((sp & truth.astype(bool)).sum() / sp.sum())   # precision of the skeleton
    tsens = float((st & pred.astype(bool)).sum() / st.sum())    # recall of the skeleton
    if tprec + tsens == 0:
        return None
    return dict(cldice=2 * tprec * tsens / (tprec + tsens),
                topology_precision=tprec, topology_sensitivity=tsens)


def score_volume(pred: np.ndarray, truth: np.ndarray, zooms) -> dict:
    p, g = pred.astype(bool), truth.astype(bool)
    n_p, n_g = int(p.sum()), int(g.sum())
    row = dict(truth_voxels=n_g, predicted_voxels=n_p)
    row["dice"] = float(2 * (p & g).sum() / (n_p + n_g)) if n_p + n_g else None
    row["recall"] = float((p & g).sum() / n_g) if n_g else None
    row["precision"] = float((p & g).sum() / n_p) if n_p else None
    row.update(surface_distances(p, g, zooms) or
               dict(assd_mm=None, hd95_mm=None, hd_mm=None))
    row.update(cl_dice(p, g) or dict(cldice=None, topology_precision=None,
                                     topology_sensitivity=None))
    return row


def patch_dice(model, fixed, cfg: Config, device) -> float:
    """A fast proxy on a fixed patch set: model selection only, never reported."""
    import torch
    model.eval()
    inter = denom = 0.0
    with torch.no_grad():
        for start in range(0, len(fixed), max(1, cfg.batch_size)):
            chunk = fixed[start:start + max(1, cfg.batch_size)]
            x = torch.from_numpy(np.stack([c[0] for c in chunk])).unsqueeze(1).to(device)
            with torch.autocast("cuda", enabled=(cfg.amp and device.type == "cuda")):
                p = (torch.sigmoid(model(x).float())[:, 0] >= 0.5).cpu().numpy()
            t = np.stack([c[1] for c in chunk]) > 0.5
            inter += float((p & t).sum()); denom += float(p.sum() + t.sum())
    return float(2 * inter / denom) if denom else 0.0


# --------------------------------------------------------------------------- #
# 6. One training run, fitted to a wall clock
# --------------------------------------------------------------------------- #
def train_stage(model, train_set: PatchSet, val_fixed, cfg: Config, device, *,
                minutes: float, label: str, fixed_steps: int | None = None):
    import torch

    loss_fn = make_loss(cfg, device)
    opt = torch.optim.AdamW(model.parameters(), cfg.lr, weight_decay=cfg.weight_decay)
    scaler = torch.amp.GradScaler("cuda", enabled=(cfg.amp and device.type == "cuda"))
    gen = torch.Generator(device=device); gen.manual_seed(cfg.seed)

    budget = minutes * 60.0
    total = 10 ** 9
    warm, calib = cfg.warmup_steps, cfg.warmup_steps + cfg.calib_steps
    t_warm = None
    history, best = [], dict(step=-1, score=-1.0, state=None)
    t0, step, next_check = time.time(), 0, None
    plan = f"{fixed_steps} steps" if fixed_steps else f"budget {minutes:.1f} min"
    print(f"\n[{label}] {plan}, {len(train_set.subjects)} brains, patch "
          f"{'x'.join(str(v) for v in cfg.patch)}, vessel share of the pool "
          f"{100 * train_set.share:.3f} %", flush=True)

    while True:
        model.train()
        opt.zero_grad(set_to_none=True)
        for _ in range(cfg.accum):
            xs, ys, ws = zip(*(train_set.draw() for _ in range(cfg.batch_size)))
            x = torch.from_numpy(np.stack(xs)).unsqueeze(1).to(device)
            y = torch.from_numpy(np.stack(ys)).to(device)
            w = torch.from_numpy(np.stack(ws)).to(device)
            x, y, w = augment(x, y, w, cfg, gen)
            with torch.autocast("cuda", enabled=(cfg.amp and device.type == "cuda")):
                loss = loss_fn(model(x), y, w)
            scaler.scale(loss / cfg.accum).backward()
        scaler.step(opt); scaler.update(); step += 1

        if step == warm:
            t_warm = time.time()
        if step == calib:
            rate = (calib - warm) / max(time.time() - t_warm, 1e-9)
            remaining = budget - (time.time() - t0)
            total = max(calib + 1, int(fixed_steps or calib + rate * remaining))
            next_check = max(1, total // cfg.checks)
            print(f"[{label}] {rate:.2f} steps/s after a {warm}-step warm-up -> "
                  f"{total} steps planned ({total * cfg.batch_size * cfg.accum} patches)",
                  flush=True)
        if step >= calib:
            frac = step / max(total, 1)
            scale = (frac / cfg.warmup_frac) if frac < cfg.warmup_frac else 0.5 * (
                1 + math.cos(math.pi * min((frac - cfg.warmup_frac) /
                                           max(1 - cfg.warmup_frac, 1e-9), 1.0)))
            for g in opt.param_groups:
                g["lr"] = cfg.lr * max(scale, 1e-3)
        if val_fixed and step >= calib and (step % next_check == 0 or step >= total):
            score = patch_dice(model, val_fixed, cfg, device)
            history.append(dict(step=step, loss=float(loss.detach()), patch_dice=score,
                                seconds=time.time() - t0))
            flag = ""
            if score > best["score"]:
                best = dict(step=step, score=score,
                            state={k: v.detach().cpu().clone()
                                   for k, v in model.state_dict().items()})
                flag = "  <- best"
            print(f"[{label}] step {step:5d}/{total}  loss {float(loss.detach()):.4f}  "
                  f"val patch Dice {score:.4f}  {time.time() - t0:5.0f}s{flag}", flush=True)
        if step >= total:
            break
        if fixed_steps is None and time.time() - t0 > budget * 1.5:
            break

    if best["state"] is not None:
        model.load_state_dict(best["state"])
    return dict(steps=step, planned=total, seconds=time.time() - t0,
                selection="held-out patches" if val_fixed else "none, last step",
                best_step=best["step"], best_patch_dice=best["score"], history=history)


# --------------------------------------------------------------------------- #
# 7. Drawing it, on a brain the model never saw
# --------------------------------------------------------------------------- #
def draw_overlay(sub, pred, out_dir: Path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"  (overlay skipped: {type(exc).__name__})", flush=True)
        return None
    image, truth = sub["image"], sub["truth"]
    # a maximum-intensity projection is how angiography is actually read
    axis = 2
    mip = image.max(axis=axis).T
    pm = pred.max(axis=axis).T.astype(bool)
    tm = truth.max(axis=axis).T.astype(bool)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.6), dpi=200)
    fig.patch.set_facecolor("#0d0d0c")
    for ax, (title, overlay, colour) in zip(axes, [
            ("the scan: TOF-MRA, maximum intensity projection", None, None),
            ("what the model says", pm, "#3987e5"),
            ("what the expert drew", tm, "#5fd0bd")]):
        ax.imshow(mip, cmap="gray", origin="lower", interpolation="nearest")
        if overlay is not None:
            rgba = np.zeros(overlay.shape + (4,), np.float32)
            rgba[overlay, :3] = matplotlib.colors.to_rgb(colour)
            rgba[overlay, 3] = 0.85
            ax.imshow(rgba, origin="lower", interpolation="nearest")
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(title, color="#f8f7f4", fontsize=9)
        for s in ax.spines.values():
            s.set_color("#262623")
    fig.suptitle(f"{sub['name']} — a healthy brain this model never saw",
                 color="#f8f7f4", fontsize=12)
    fig.text(0.012, 0.015, "Healthy anatomy, for learning — not a diagnosis. "
             "Contains MRI pixels: belongs with the run, never in a repository.",
             color="#6f6e66", fontsize=7)
    fig.tight_layout(rect=[0, 0.03, 1, 0.96])
    path = out_dir / f"overlay_{sub['name']}.png"
    fig.savefig(path, facecolor="#0d0d0c"); plt.close(fig)
    return path


# --------------------------------------------------------------------------- #
# 8. The run
# --------------------------------------------------------------------------- #
def main():
    cfg, args = parse_args()
    print(__doc__.strip().split("\n\n")[1], "\n", flush=True)
    import torch

    device = torch.device("cuda" if torch.cuda.is_available() else
                          ("mps" if torch.backends.mps.is_available() else "cpu"))
    gpu = torch.cuda.get_device_name(0) if device.type == "cuda" else str(device)
    print(f"torch {torch.__version__} | device {device} | {gpu}", flush=True)
    print(f"this script: sha256 {sha256_of_self()}", flush=True)
    if device.type != "cuda":
        cfg.amp = False
        print("!! no CUDA: only --smoke makes sense here", flush=True)

    random.seed(cfg.seed); np.random.seed(cfg.seed); torch.manual_seed(cfg.seed)
    torch.cuda.manual_seed_all(cfg.seed)
    torch.backends.cudnn.benchmark = True

    work = Path(args.work_dir)
    labels_dir = Path(args.labels_root) if args.labels_root else fetch_labels(work)
    ids = sorted(p.name.split(".")[0] for p in Path(labels_dir).glob("IXI*.nii.gz"))
    print(f"\n{len(ids)} annotated healthy subjects: {ids[0]} .. {ids[-1]}", flush=True)

    if args.images_root:
        images_dir = Path(args.images_root)
    else:
        index_path = Path(args.index or (Path(__file__).parent / INDEX_FILE))
        if index_path.exists():
            raw = json.loads(index_path.read_text())
            images_dir = fetch_images(work, {k: tuple(v) for k, v in raw.items()}, ids)
        else:
            print(f"  (no index at {index_path})", flush=True)
            images_dir = fetch_images_streaming(work, ids)

    if args.smoke:
        ids = ids[:6]

    t0 = time.time()
    prepared = {}
    for n, sid in enumerate(ids, 1):
        img = Path(images_dir) / f"{sid}.nii.gz"
        if not img.exists():
            cands = sorted(Path(images_dir).glob(f"{sid}-*.nii.gz"))
            if not cands:
                raise RuntimeError(f"no image for {sid} in {images_dir}")
            img = cands[0]
        prepared[sid] = prepare_subject(sid, img, Path(labels_dir) / f"{sid}.nii.gz", cfg)
        if n % 20 == 0 or n == len(ids):
            print(f"  prepared {n}/{len(ids)} ({time.time() - t0:.0f}s)", flush=True)

    frac = np.array([prepared[s]["vessel_fraction"] for s in ids])
    print(f"\nvessel share: mean {100 * frac.mean():.3f} %  "
          f"({100 * frac.min():.3f} % to {100 * frac.max():.3f} %)  "
          f"-> {cfg.vessel_patch_frac:.0%} of patches are drawn on a vessel voxel",
          flush=True)

    rng = random.Random(cfg.seed)
    shuffled = list(ids); rng.shuffle(shuffled)
    folds = [shuffled[i::cfg.folds] for i in range(cfg.folds)]
    assert sum(len(f) for f in folds) == len(ids) and all(folds)
    assert len({s for f in folds for s in f}) == len(ids), "a subject is in two folds"
    print(f"\n{cfg.folds} folds of {[len(f) for f in folds]}; each subject scored once, "
          f"by a model that never saw it", flush=True)

    model = build_model(cfg).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"residual 3D U-Net: {n_params:,d} parameters, one sigmoid output\n", flush=True)
    fresh = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    out_dir = Path(cfg.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    scored, fold_reports, to_draw = {}, [], {}
    for k, test in enumerate(folds):
        pool = [s for f, g in enumerate(folds) if f != k for s in g]
        rng.shuffle(pool)
        n_val = min(cfg.val_subjects, max(1, len(pool) - 1))
        val, train = pool[:n_val], pool[n_val:]
        assert not (set(test) & set(train)) and not (set(test) & set(val)), "fold leak"
        print(f"\n=== fold {k + 1}/{cfg.folds}: train {len(train)}, select {len(val)}, "
              f"test {len(test)}", flush=True)
        model.load_state_dict(fresh)
        rep = train_stage(model, PatchSet([prepared[s] for s in train], cfg, f"f{k}"),
                          PatchSet([prepared[s] for s in val], cfg, f"v{k}")
                          .fixed_set(cfg.val_patches),
                          cfg, device, minutes=cfg.fold_minutes, label=f"fold {k + 1}")
        rep["subjects"] = dict(train=train, val=val, test=test)
        fold_reports.append(rep)
        torch.save(dict(model=model.state_dict(), config=asdict(cfg), fold=k + 1,
                        subjects=rep["subjects"]), out_dir / f"weights_fold{k + 1}.pt")
        for sid in test:
            pred, _ = predict_volume(model, prepared[sid], cfg, device)
            scored[sid] = score_volume(pred, prepared[sid]["truth"], prepared[sid]["zooms"])
            if k == 0 and len(to_draw) < 2:
                to_draw[sid] = pred.copy()
        print(f"  scored {len(test)} held-out brains", flush=True)

    final = None
    if cfg.final_model:
        chosen = [r["best_step"] for r in fold_reports if r["best_step"] > 0]
        target = max(1, int(np.median(chosen))) if chosen else None
        print(f"\n=== the delivered model: all {len(ids)} brains, {target} steps, the "
              f"median the folds chose. Nothing is held out from it.", flush=True)
        model.load_state_dict(fresh)
        final = train_stage(model, PatchSet([prepared[s] for s in ids], cfg, "final"),
                            None, cfg, device, minutes=cfg.fold_minutes,
                            label="final", fixed_steps=target)
        final["subjects"] = ids
        final["how_to_quote_it"] = (
            "Trained on all one hundred brains, so none is left to test it. Its "
            "performance is the 5-fold cross-validated estimate in results.cross_validated "
            "— an estimate, not a measurement on unseen brains.")
        torch.save(dict(model=model.state_dict(), config=asdict(cfg), stage="final",
                        subjects=ids), out_dir / "weights_final.pt")

    def summarise(rows):
        out = {}
        for key in ("dice", "cldice", "hd95_mm", "assd_mm", "recall", "precision",
                    "topology_precision", "topology_sensitivity"):
            vals = [r[key] for r in rows.values() if r.get(key) is not None]
            out[key] = dict(mean=float(np.mean(vals)) if vals else None,
                            std=float(np.std(vals)) if vals else None,
                            min=float(np.min(vals)) if vals else None,
                            max=float(np.max(vals)) if vals else None,
                            subjects=len(vals))
        return out

    agg = summarise(scored)
    print("\n" + "=" * 86)
    print("CROSS-VALIDATED, on healthy brains each held out of its own fold")
    for key in ("dice", "cldice", "hd95_mm", "assd_mm", "recall", "precision"):
        m = agg[key]
        if m["mean"] is None:
            print(f"  {key:12s} —"); continue
        unit = " mm" if key.endswith("_mm") else ""
        print(f"  {key:12s} {m['mean']:.4f}{unit}   sd {m['std']:.4f}   "
              f"[{m['min']:.3f}, {m['max']:.3f}]   n={m['subjects']}")
    print("  Dice alone is not the verdict: clDice is what a broken vessel tree fails.")
    print("=" * 86, flush=True)

    report = dict(
        purpose="learning anatomy, never diagnosis",
        what_this_is="Brain use 2: a binary cerebral vessel network, trained and measured "
                     "on healthy subjects only. No patient data, no pre-training stage.",
        sources=dict(
            labels=dict(doi=LABELS_DOI, licence="CC BY 4.0", md5=LABELS_MD5,
                        n_subjects=len(ids)),
            images=dict(name="IXI MRA", url=IMAGES_URL, licence=IMAGES_LICENCE,
                        note="only the needed members were pulled, by byte range"),
            weights_ceiling="share-alike, inherited from the CC BY-SA 3.0 images"),
        caveats=dict(
            labels_are_binary="the arteries are not named; no public dataset names them "
                              "on healthy subjects today",
            topcow_overlap=dict(subjects=TOPCOW_OVERLAP,
                                note="also present in TopCoW's MRA_IXI_HH external test "
                                     "set. Nothing from TopCoW is used in this run, but "
                                     "any later comparison against TopCoW labels must "
                                     "drop these subjects."),
            costa_overlap="COSTA's IXI identifiers are behind a restricted record and "
                          "could not be checked; cross them before any COSTA volume "
                          "joins a training set."),
        environment=dict(torch=torch.__version__, cuda=torch.version.cuda, device=gpu,
                         python=sys.version.split()[0], script_sha256=sha256_of_self()),
        config={k: (list(v) if isinstance(v, tuple) else v) for k, v in asdict(cfg).items()},
        model=dict(parameters=n_params, architecture="residual 3D U-Net, binary head",
                   patch=list(cfg.patch), outputs=1),
        data=dict(subjects=ids, vessel_fraction_mean=float(frac.mean()),
                  vessel_fraction_min=float(frac.min()), vessel_fraction_max=float(frac.max())),
        split=dict(folds=[list(f) for f in folds],
                   rule="five folds over the hundred; each subject scored once by a model "
                        "that never saw it"),
        stage_folds=fold_reports,
        stage_final=final,
        results=dict(cross_validated=agg, per_subject=scored,
                     read_this_first=[
                         "Every brain here is a healthy volunteer. There is no patient "
                         "data in this run and no pre-training on any.",
                         "The labels are binary: vessel or not. No artery is named.",
                         "clDice measures whether the network survives; Dice does not. A "
                         "model that drops a branch can still look good on Dice.",
                         "HD95 and ASSD are millimetres from the NIfTI affine, and neither "
                         "is optimised: the loss uses a boundary-weighted BCE instead.",
                         "The delivered model is trained on all hundred; its performance is "
                         "the cross-validated estimate, not a held-out measurement."]))
    payload = json.dumps(report, indent=2)
    report["fingerprint"] = hashlib.md5(payload.encode()).hexdigest()
    (out_dir / "results_use2.json").write_text(json.dumps(report, indent=2))
    print(f"\nresults: {out_dir / 'results_use2.json'} "
          f"({(out_dir / 'results_use2.json').stat().st_size / 1e3:.0f} kB)")

    print("\ndrawing the segmentation on scans the model never saw:", flush=True)
    for sid, pred in to_draw.items():
        p = draw_overlay(prepared[sid], pred, out_dir)
        if p:
            print(f"  {p.name}  ({p.stat().st_size / 1e3:.0f} kB)", flush=True)

    import shutil
    archive = shutil.make_archive(str(out_dir), "zip", root_dir=out_dir.parent,
                                  base_dir=out_dir.name)
    print(f"\n{'=' * 78}\nEVERYTHING IS IN ONE FILE. Download it before the session ends:")
    print(f"  {archive}  ({Path(archive).stat().st_size / 1e6:.1f} MB)")
    for f in sorted(out_dir.iterdir()):
        print(f"    {f.name:30s} {f.stat().st_size / 1e6:8.2f} MB")
    print("=" * 78, flush=True)
    print("\nThe weights MAY be published here, under share-alike: the labels are "
          "CC BY 4.0 and the images CC BY-SA 3.0. That holds only while nothing with "
          "heavier terms enters the training set.")
    print("The overlay PNGs contain MRI pixels. They are for looking at, never for a "
          "repository.")


if __name__ == "__main__":
    main()
