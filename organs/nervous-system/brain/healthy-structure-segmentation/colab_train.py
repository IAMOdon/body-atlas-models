#!/usr/bin/env python3
"""
Body Atlas Models — brain, use 1: healthy structure segmentation.
Standalone training run for a GPU runtime (Colab T4 and up).

FOR LEARNING ANATOMY, NEVER FOR DIAGNOSIS. This script trains a small model on
labelled public MRI so that a student can see the structures of a healthy brain
named on an image, beside the labels an expert (or a program) drew. It is not a
diagnostic tool, it is not validated for clinical use, and nothing it produces
may be used to say what a person has.

The script is self-contained: it needs nothing from the repository it lives in.
It fetches Mindboggle-101 from Zenodo (doi:10.5281/zenodo.22070005), verifies
every file against the MD5 sums published by that record, extracts it, trains,
evaluates on held-out subjects, and writes weights, metrics and curves next to
each other.

ONE THING MATTERS THROUGHOUT. The two label volumes do not have the same
provenance:
  * the CORTEX is labelled by hand, following the DKT protocol;
  * every NON-CORTICAL structure comes from FreeSurfer's automatic
    segmentation ("aseg").
So a high score on the hippocampus means "agrees with FreeSurfer", not
"correct". Every metric below is reported with its provenance, and the summary
splits the two.

The weights this produces are NOT published under a permissive licence: the T1
images carry the terms of the projects that acquired them (OASIS, NKI, MMRR),
which conflict with the record's CC BY 4.0. Read the record's LICENSE before
sharing anything trained here.

Usage (Colab):
    !pip -q install nibabel
    !python colab_train.py
Options worth knowing:
    --data-root PATH   use an existing extracted copy, skip the download
    --smoke            a two-minute sanity run (few subjects, few epochs)
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
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

# --------------------------------------------------------------------------- #
# 1. The record, exactly as DATA.md records it
# --------------------------------------------------------------------------- #
ZENODO_RECORD = "22070005"
ZENODO_DOI = "10.5281/zenodo.22070005"
# file name -> (size in bytes, md5) as published by the record
RECORD_FILES = {
    "Mindboggle101_release3.zip": (5232272873, "7178353814033f9f56dc97bdef2d68e4"),
    "Mindboggle101_templates.zip": (245621865, "004cf36fb3e04da8c25f3aef73c85fad"),
    "DKT_classifier_evaluation.zip": (39525815, "6449062bf5f103ed094178669ffeb4ac"),
    "Mindboggle101_atlases.zip": (26370639, "adb803397b873c5d99abcec61ba9b1de"),
    "docs.zip": (20140530, "67aed2e5ae669a920e99a144165a3c17"),
    "DKT_labeling_protocol.zip": (206199, "30b13f370e10a0282250e636e6b475b5"),
    "README.md": (7190, "3c0077a03eda0f6ed59323e69459805b"),
    "LICENSE": (861, "c57007ca73fcacb52613233c0386c8af"),
}
# only these are needed to train; the rest is fetched for checksum parity and provenance
NEEDED = ["Mindboggle101_release3.zip"]

# --------------------------------------------------------------------------- #
# 2. The structures, and where each label comes from
#    codes follow FreeSurfer's colour table; the cortex comes from the manual file
# --------------------------------------------------------------------------- #
MANUAL, AUTO = "manual (DKT protocol)", "automatic (FreeSurfer aseg)"
CLASSES = [
    ("background", "-", ()),
    ("cerebral cortex", MANUAL, "manual>=1000"),
    ("cerebral white matter", AUTO, (2, 41)),
    ("lateral ventricle", AUTO, (4, 43, 5, 44)),
    ("thalamus", AUTO, (10, 49)),
    ("caudate", AUTO, (11, 50)),
    ("putamen", AUTO, (12, 51)),
    ("pallidum", AUTO, (13, 52)),
    ("hippocampus", AUTO, (17, 53)),
    ("amygdala", AUTO, (18, 54)),
    ("brainstem", AUTO, (16,)),
    ("cerebellum", AUTO, (7, 8, 46, 47)),
]
CLASS_NAMES = [c[0] for c in CLASSES]
N_CLASSES = len(CLASSES)
MANUAL_IDX = [i for i, c in enumerate(CLASSES) if c[1] == MANUAL]
AUTO_IDX = [i for i, c in enumerate(CLASSES) if c[1] == AUTO]


# --------------------------------------------------------------------------- #
# 3. Configuration. The defaults are the optimised run, not the demonstrator.
# --------------------------------------------------------------------------- #
@dataclass
class Config:
    # data
    crop: int = 192               # mm, at 1 mm isotropic: a 192x192 axial window
    min_labelled: int = 3000      # voxels, to drop slices that hold almost nothing
    context: int = 1              # 2.5D: this many slices each side feed the model
    train_frac: float = 0.70      # split is by SUBJECT, stratified by cohort
    val_frac: float = 0.15        # the rest is held out and touched once, at the end
    # model
    base_channels: int = 16       # a small U-Net: four levels, 16/32/64/128
    depth: int = 4
    # training
    epochs: int = 60
    batch_size: int = 32
    lr: float = 3e-3
    weight_decay: float = 1e-4
    warmup_epochs: int = 3
    amp: bool = True
    dice_weight: float = 0.5      # loss = weighted CE + dice_weight * soft Dice
    # augmentation (left-right flip is safe: the classes merge both hemispheres)
    aug_flip: float = 0.5
    aug_rotate_deg: float = 12.0
    aug_scale: float = 0.10
    aug_shift: float = 0.06
    aug_gamma: float = 0.25
    aug_noise: float = 0.02
    # bookkeeping
    seed: int = 20260926
    out_dir: str = "runs/brain-use1"
    subjects: int = 0             # 0 = every subject


def parse_args() -> tuple[Config, argparse.Namespace]:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[2])
    p.add_argument("--data-root", default="", help="an existing .../Mindboggle101_volumes")
    p.add_argument("--work-dir", default="mindboggle101", help="where to download and extract")
    p.add_argument("--out-dir", default=Config.out_dir)
    p.add_argument("--epochs", type=int, default=Config.epochs)
    p.add_argument("--batch-size", type=int, default=Config.batch_size)
    p.add_argument("--base-channels", type=int, default=Config.base_channels)
    p.add_argument("--crop", type=int, default=Config.crop)
    p.add_argument("--subjects", type=int, default=0, help="cap the number of subjects")
    p.add_argument("--seed", type=int, default=Config.seed)
    p.add_argument("--no-amp", action="store_true")
    p.add_argument("--smoke", action="store_true", help="tiny run to check the code path")
    a = p.parse_args()
    cfg = Config(epochs=a.epochs, batch_size=a.batch_size, base_channels=a.base_channels,
                 crop=a.crop, seed=a.seed, amp=not a.no_amp, out_dir=a.out_dir,
                 subjects=a.subjects)
    if a.smoke:
        cfg.epochs, cfg.subjects, cfg.crop, cfg.batch_size = 2, 8, 96, 8
        cfg.base_channels, cfg.depth, cfg.warmup_epochs = 8, 3, 0
    return cfg, a


# --------------------------------------------------------------------------- #
# 4. Fetch and verify. Nothing is trusted that does not match the record.
# --------------------------------------------------------------------------- #
def md5_of(path: Path, chunk: int = 1 << 22) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def download(name: str, dest: Path, attempts: int = 5) -> None:
    url = f"https://zenodo.org/api/records/{ZENODO_RECORD}/files/{name}/content"
    size = RECORD_FILES[name][0]
    for attempt in range(1, attempts + 1):
        have = dest.stat().st_size if dest.exists() else 0
        if have >= size:
            return
        req = urllib.request.Request(url)
        if have:
            req.add_header("Range", f"bytes={have}-")
        try:
            with urllib.request.urlopen(req, timeout=120) as r, open(dest, "ab" if have else "wb") as fh:
                done, t0, last = have, time.time(), time.time()
                while True:
                    block = r.read(1 << 20)
                    if not block:
                        break
                    fh.write(block)
                    done += len(block)
                    if time.time() - last > 10:
                        pct, mbps = 100 * done / size, done / 1e6 / max(time.time() - t0, 1e-9)
                        print(f"    {name}: {pct:5.1f}%  {done/1e9:.2f}/{size/1e9:.2f} GB  {mbps:.1f} MB/s",
                              flush=True)
                        last = time.time()
        except Exception as exc:                      # a dropped connection is normal on a long file
            print(f"    {name}: {type(exc).__name__} at {dest.stat().st_size if dest.exists() else 0} bytes, "
                  f"resuming (attempt {attempt}/{attempts})", flush=True)
            time.sleep(3 * attempt)
    if not dest.exists() or dest.stat().st_size < size:
        raise RuntimeError(f"{name}: download did not complete")


def fetch_and_verify(work: Path, only_needed: bool = False) -> dict:
    """Download the record, check every file, return {name: md5}."""
    work.mkdir(parents=True, exist_ok=True)
    wanted = NEEDED if only_needed else list(RECORD_FILES)
    checked = {}
    for name in wanted:
        size, want = RECORD_FILES[name]
        path = work / name
        if not (path.exists() and path.stat().st_size == size):
            print(f"  fetching {name} ({size/1e9:.2f} GB)", flush=True)
            download(name, path)
        got = md5_of(path)
        state = "ok" if got == want else "MISMATCH"
        print(f"  {state:8s} {name:32s} {got}", flush=True)
        if got != want:
            raise RuntimeError(f"{name}: md5 {got} does not match the record's {want}")
        checked[name] = got
    return checked


def extract(work: Path) -> Path:
    """Unpack the volumes (images and labels). Surfaces are left alone."""
    root = work / "extracted"
    volumes = root / "Mindboggle101_release3" / "Mindboggle101_volumes"
    if not volumes.is_dir():
        print("  unpacking Mindboggle101_release3.zip", flush=True)
        with zipfile.ZipFile(work / "Mindboggle101_release3.zip") as zf:
            zf.extractall(root)
    for tar_path in sorted(volumes.glob("*_volumes.tar.gz")):
        if not (volumes / tar_path.name.replace(".tar.gz", "")).is_dir():
            print(f"  unpacking {tar_path.name}", flush=True)
            with tarfile.open(tar_path) as tf:
                tf.extractall(volumes)
    return volumes


# --------------------------------------------------------------------------- #
# 5. Build the dataset: 2.5D axial slices, cropped, per subject
# --------------------------------------------------------------------------- #
def label_map(aseg: np.ndarray, manual: np.ndarray) -> np.ndarray:
    y = np.zeros(aseg.shape, np.uint8)
    for idx, (_, _, codes) in enumerate(CLASSES):
        if isinstance(codes, tuple):
            for code in codes:
                y[aseg == code] = idx
    y[manual >= 1000] = 1                 # the manual cortex wins wherever the two meet
    return y


def load_subject(subject: Path, cfg: Config):
    import nibabel as nib
    img = nib.as_closest_canonical(nib.load(subject / "t1weighted_brain.nii.gz"))
    aseg = np.asarray(nib.as_closest_canonical(
        nib.load(subject / "labels.DKT31.manual+aseg.nii.gz")).dataobj).astype(np.int32)
    manual = np.asarray(nib.as_closest_canonical(
        nib.load(subject / "labels.DKT31.manual.nii.gz")).dataobj).astype(np.int32)
    vol = img.get_fdata(dtype=np.float32)
    y = label_map(aseg, manual)

    lo, hi = np.percentile(vol[vol > 0], (1, 99))      # per subject: scanners differ
    vol = np.clip((vol - lo) / max(hi - lo, 1e-6), 0, 1)

    keep = [k for k in range(y.shape[2]) if int((y[:, :, k] > 0).sum()) > cfg.min_labelled]
    if not keep:
        return None
    lo_k, hi_k = min(keep), max(keep)

    ys, xs = np.where(y.any(axis=2))                    # centre the crop on the labelled tissue
    cx, cy = int(ys.mean()), int(xs.mean())
    half = cfg.crop // 2

    def window(a):
        x0, y0 = cx - half, cy - half
        out = np.zeros((cfg.crop, cfg.crop) + a.shape[2:], a.dtype)
        sx0, sy0 = max(x0, 0), max(y0, 0)
        sx1, sy1 = min(x0 + cfg.crop, a.shape[0]), min(y0 + cfg.crop, a.shape[1])
        out[sx0 - x0:sx1 - x0, sy0 - y0:sy1 - y0] = a[sx0:sx1, sy0:sy1]
        return out

    pad = cfg.context
    zs = range(max(lo_k - pad, 0), min(hi_k + pad + 1, y.shape[2]))
    image = window(vol[:, :, list(zs)])
    labels = window(y[:, :, list(zs)])
    centre = [k - zs.start for k in keep]
    return (np.ascontiguousarray(np.transpose(image, (2, 0, 1)) * 255).astype(np.uint8),
            np.ascontiguousarray(np.transpose(labels, (2, 0, 1))),
            np.asarray(centre, np.int32))


def cohort_of(subject: Path) -> str:
    return subject.parent.name.replace("_volumes", "")


def split_subjects(volumes: Path, cfg: Config):
    by_cohort = {}
    for cohort_dir in sorted(p for p in volumes.iterdir() if p.is_dir()):
        subs = sorted(p for p in cohort_dir.iterdir() if p.is_dir())
        if subs:
            by_cohort[cohort_of(subs[0])] = subs
    rng = random.Random(cfg.seed)
    train, val, test = [], [], []
    for cohort, subs in by_cohort.items():
        subs = list(subs)
        rng.shuffle(subs)                                 # seeded: the same split every run
        if cfg.subjects:
            subs = subs[:max(3, cfg.subjects // len(by_cohort))]
        n_tr = max(1, round(cfg.train_frac * len(subs)))
        n_va = max(1, round(cfg.val_frac * len(subs)))
        # every cohort must keep at least one held-out subject: the final score is
        # only meaningful on brains no part of the run has seen.
        while len(subs) - n_tr - n_va < 1 and n_tr > 1:
            n_tr -= 1
        train += subs[:n_tr]
        val += subs[n_tr:n_tr + n_va]
        test += subs[n_tr + n_va:]
    names = [{s.name for s in group} for group in (train, val, test)]
    assert not (names[0] & names[1]) and not (names[0] & names[2]) and not (names[1] & names[2]), \
        "a subject appears in more than one split"
    assert test, "no held-out subject: raise the number of subjects"
    return train, val, test, by_cohort


class SliceSet:
    """Slices of several subjects, kept per subject so 2.5D context never crosses brains."""

    def __init__(self, subjects, cfg: Config, name: str):
        self.cfg, self.name, self.subjects = cfg, name, []
        self.index = []
        t0 = time.time()
        for n, sub in enumerate(subjects, 1):
            loaded = load_subject(sub, cfg)
            if loaded is None:
                print(f"  {sub.name}: no labelled slice, skipped", flush=True)
                continue
            image, labels, centre = loaded
            sid = len(self.subjects)
            self.subjects.append(dict(name=sub.name, cohort=cohort_of(sub),
                                      image=image, labels=labels, centre=centre))
            self.index += [(sid, int(k)) for k in centre]
            if n % 10 == 0 or n == len(subjects):
                print(f"  {name}: {n}/{len(subjects)} subjects, {len(self.index)} slices "
                      f"({time.time() - t0:.0f}s)", flush=True)
        self.index = np.asarray(self.index, np.int32)

    def __len__(self):
        return len(self.index)

    def sample(self, i):
        sid, k = self.index[i]
        sub = self.subjects[sid]
        ctx = self.cfg.context
        lo, hi = k - ctx, k + ctx + 1
        stack = sub["image"][lo:hi]
        if len(stack) < 2 * ctx + 1:                       # near the ends: repeat the edge slice
            stack = np.concatenate([stack] + [stack[-1:]] * (2 * ctx + 1 - len(stack)))
        return stack.astype(np.float32) / 255.0, sub["labels"][k].astype(np.int64)


# --------------------------------------------------------------------------- #
# 6. The model: a small U-Net
# --------------------------------------------------------------------------- #
def build_model(cfg: Config):
    import torch.nn as nn

    class Block(nn.Sequential):
        def __init__(self, cin, cout):
            super().__init__(
                nn.Conv2d(cin, cout, 3, padding=1, bias=False), nn.BatchNorm2d(cout),
                nn.ReLU(inplace=True),
                nn.Conv2d(cout, cout, 3, padding=1, bias=False), nn.BatchNorm2d(cout),
                nn.ReLU(inplace=True))

    class UNet(nn.Module):
        def __init__(self):
            super().__init__()
            import torch
            widths = [cfg.base_channels * 2 ** i for i in range(cfg.depth)]
            self.encoders = nn.ModuleList()
            cin = 2 * cfg.context + 1
            for w in widths:
                self.encoders.append(Block(cin, w))
                cin = w
            self.bottom = Block(widths[-1], widths[-1] * 2)
            self.ups, self.decoders = nn.ModuleList(), nn.ModuleList()
            cin = widths[-1] * 2
            for w in reversed(widths):
                self.ups.append(nn.ConvTranspose2d(cin, w, 2, 2))
                self.decoders.append(Block(2 * w, w))
                cin = w
            self.head = nn.Conv2d(widths[0], N_CLASSES, 1)
            self.pool = nn.MaxPool2d(2)
            self.torch = torch

        def forward(self, x):
            skips = []
            for enc in self.encoders:
                x = enc(x)
                skips.append(x)
                x = self.pool(x)
            x = self.bottom(x)
            for up, dec, skip in zip(self.ups, self.decoders, reversed(skips)):
                x = dec(self.torch.cat([up(x), skip], 1))
            return self.head(x)

    return UNet()


# --------------------------------------------------------------------------- #
# 7. Augmentation, on the GPU, one batch at a time
# --------------------------------------------------------------------------- #
def augment(x, y, cfg: Config, gen):
    import torch
    import torch.nn.functional as F
    b = x.shape[0]
    dev = x.device
    if cfg.aug_flip:                                        # left-right only; classes merge sides
        flip = torch.rand(b, device=dev, generator=gen) < cfg.aug_flip
        x[flip] = torch.flip(x[flip], dims=[3])
        y[flip] = torch.flip(y[flip], dims=[2])
    ang = (torch.rand(b, device=dev, generator=gen) * 2 - 1) * math.radians(cfg.aug_rotate_deg)
    sc = 1 + (torch.rand(b, device=dev, generator=gen) * 2 - 1) * cfg.aug_scale
    tx = (torch.rand(b, device=dev, generator=gen) * 2 - 1) * cfg.aug_shift
    ty = (torch.rand(b, device=dev, generator=gen) * 2 - 1) * cfg.aug_shift
    cos, sin = torch.cos(ang) / sc, torch.sin(ang) / sc
    theta = torch.zeros(b, 2, 3, device=dev)
    theta[:, 0, 0], theta[:, 0, 1], theta[:, 0, 2] = cos, -sin, tx
    theta[:, 1, 0], theta[:, 1, 1], theta[:, 1, 2] = sin, cos, ty
    grid = F.affine_grid(theta, list(x.shape), align_corners=False)
    x = F.grid_sample(x, grid, mode="bilinear", padding_mode="zeros", align_corners=False)
    y = F.grid_sample(y.unsqueeze(1).float(), grid, mode="nearest",
                      padding_mode="zeros", align_corners=False).squeeze(1).long()
    if cfg.aug_gamma:                                       # intensity: scanners differ
        g = torch.exp((torch.rand(b, 1, 1, 1, device=dev, generator=gen) * 2 - 1) * cfg.aug_gamma)
        x = x.clamp(0, 1) ** g
    if cfg.aug_noise:
        x = x + torch.randn(x.shape, device=dev, generator=gen) * cfg.aug_noise
    return x.clamp(0, 1), y


# --------------------------------------------------------------------------- #
# 8. Losses and metrics
# --------------------------------------------------------------------------- #
def soft_dice_loss(logits, target):
    import torch
    import torch.nn.functional as F
    probs = F.softmax(logits, 1)
    hot = F.one_hot(target, N_CLASSES).permute(0, 3, 1, 2).float()
    dims = (0, 2, 3)
    inter = (probs * hot).sum(dims)
    denom = probs.sum(dims) + hot.sum(dims)
    dice = (2 * inter + 1.0) / (denom + 1.0)
    return 1 - dice[1:].mean()                              # background is not a structure


def dice_counts(pred, truth):
    """Per class: 2*|intersection|, |pred|+|truth|. Summed over a subject's slices."""
    inter = np.zeros(N_CLASSES, np.int64)
    total = np.zeros(N_CLASSES, np.int64)
    for c in range(N_CLASSES):
        p, g = pred == c, truth == c
        inter[c] = int(np.logical_and(p, g).sum())
        total[c] = int(p.sum() + g.sum())
    return inter, total


def evaluate(model, dataset: SliceSet, cfg: Config, device, batch: int = 32):
    import torch
    model.eval()
    per_subject = []
    with torch.no_grad():
        for sub in dataset.subjects:
            inter = np.zeros(N_CLASSES, np.int64)
            total = np.zeros(N_CLASSES, np.int64)
            idx = [i for i, (sid, _) in enumerate(dataset.index)
                   if dataset.subjects[sid]["name"] == sub["name"]]
            for start in range(0, len(idx), batch):
                chunk = idx[start:start + batch]
                xs, ys = zip(*(dataset.sample(i) for i in chunk))
                x = torch.from_numpy(np.stack(xs)).to(device)
                with torch.autocast("cuda", enabled=(cfg.amp and device.type == "cuda")):
                    pred = model(x).argmax(1).cpu().numpy()
                i2, t2 = dice_counts(pred, np.stack(ys))
                inter += i2
                total += t2
            dice = {CLASS_NAMES[c]: (float(2 * inter[c] / total[c]) if total[c] else None)
                    for c in range(1, N_CLASSES)}
            per_subject.append(dict(subject=sub["name"], cohort=sub["cohort"],
                                    slices=len(idx), dice=dice))
    return per_subject


def summarise(per_subject):
    out = {}
    for c in range(1, N_CLASSES):
        name = CLASS_NAMES[c]
        vals = [s["dice"][name] for s in per_subject if s["dice"][name] is not None]
        out[name] = dict(provenance=CLASSES[c][1],
                         mean=float(np.mean(vals)) if vals else None,
                         std=float(np.std(vals)) if vals else None,
                         min=float(np.min(vals)) if vals else None,
                         max=float(np.max(vals)) if vals else None,
                         subjects=len(vals))
    grouped = {}
    for label, idxs in (("manual (DKT cortex)", MANUAL_IDX), ("automatic (FreeSurfer aseg)", AUTO_IDX)):
        vals = [out[CLASS_NAMES[c]]["mean"] for c in idxs
                if c and out[CLASS_NAMES[c]]["mean"] is not None]
        grouped[label] = dict(structures=len(vals),
                              mean_of_structure_means=float(np.mean(vals)) if vals else None)
    return out, grouped


# --------------------------------------------------------------------------- #
# 9. Train
# --------------------------------------------------------------------------- #
def main():
    cfg, args = parse_args()
    print(__doc__.strip().split("\n\n")[1], "\n", flush=True)     # the banner, every run

    import torch
    import torch.nn as nn

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"torch {torch.__version__} | device {device} "
          f"| {torch.cuda.get_device_name(0) if device.type == 'cuda' else 'cpu'}", flush=True)
    if device.type != "cuda":
        print("!! no GPU visible: this run is meant for a GPU runtime", flush=True)
        cfg.amp = False

    random.seed(cfg.seed)
    np.random.seed(cfg.seed)
    torch.manual_seed(cfg.seed)
    torch.cuda.manual_seed_all(cfg.seed)
    torch.backends.cudnn.benchmark = True        # speed; exact kernels may vary between runs

    # ---- data ------------------------------------------------------------- #
    if args.data_root:
        volumes, checksums = Path(args.data_root), {"note": "local copy, checksums not re-read"}
        print(f"using existing data at {volumes}", flush=True)
    else:
        work = Path(args.work_dir)
        print(f"fetching Mindboggle-101 ({ZENODO_DOI}) into {work}", flush=True)
        checksums = fetch_and_verify(work, only_needed=args.smoke)
        volumes = extract(work)
    assert volumes.is_dir(), f"no volumes at {volumes}"

    train_subs, val_subs, test_subs = split_subjects(volumes, cfg)[:3]
    print(f"\nsplit by subject: {len(train_subs)} train | {len(val_subs)} val | "
          f"{len(test_subs)} held out", flush=True)
    train_set = SliceSet(train_subs, cfg, "train")
    val_set = SliceSet(val_subs, cfg, "val")
    test_set = SliceSet(test_subs, cfg, "held-out")

    share = np.zeros(N_CLASSES, np.float64)
    for sub in train_set.subjects:
        share += np.bincount(sub["labels"][sub["centre"]].reshape(-1), minlength=N_CLASSES)
    share /= share.sum()
    print("\nclass share of the training slices:")
    for c in range(N_CLASSES):
        print(f"  {CLASS_NAMES[c]:24s} {100 * share[c]:6.3f}%   {CLASSES[c][1]}", flush=True)

    weights = 1.0 / np.sqrt(np.clip(share, 1e-6, None))
    weights = torch.tensor(weights / weights.mean(), dtype=torch.float32, device=device)

    # ---- model ------------------------------------------------------------ #
    model = build_model(cfg).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"\nsmall U-Net: {n_params:,d} parameters "
          f"({cfg.depth} levels, {cfg.base_channels} channels at the top, "
          f"{2 * cfg.context + 1} input slices)", flush=True)

    opt = torch.optim.AdamW(model.parameters(), cfg.lr, weight_decay=cfg.weight_decay)
    ce = nn.CrossEntropyLoss(weight=weights)
    scaler = torch.amp.GradScaler("cuda", enabled=(cfg.amp and device.type == "cuda"))
    gen = torch.Generator(device=device)
    gen.manual_seed(cfg.seed)

    steps = max(1, math.ceil(len(train_set) / cfg.batch_size))

    def lr_at(epoch, step):
        t = epoch + step / steps
        if t < cfg.warmup_epochs:
            return cfg.lr * (t + 1e-9) / max(cfg.warmup_epochs, 1e-9)
        p = (t - cfg.warmup_epochs) / max(cfg.epochs - cfg.warmup_epochs, 1e-9)
        return 0.5 * cfg.lr * (1 + math.cos(math.pi * min(p, 1.0)))

    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    history, best = [], dict(epoch=-1, score=-1.0)
    rng = np.random.default_rng(cfg.seed)
    t_start = time.time()

    for epoch in range(cfg.epochs):
        model.train()
        order = rng.permutation(len(train_set))
        running, seen = 0.0, 0
        t_epoch = time.time()
        for step, start in enumerate(range(0, len(order), cfg.batch_size)):
            chunk = order[start:start + cfg.batch_size]
            xs, ys = zip(*(train_set.sample(i) for i in chunk))
            x = torch.from_numpy(np.stack(xs)).to(device, non_blocking=True)
            y = torch.from_numpy(np.stack(ys)).to(device, non_blocking=True)
            x, y = augment(x, y, cfg, gen)
            for group in opt.param_groups:
                group["lr"] = lr_at(epoch, step)
            opt.zero_grad(set_to_none=True)
            with torch.autocast("cuda", enabled=(cfg.amp and device.type == "cuda")):
                logits = model(x)
                loss = ce(logits, y) + cfg.dice_weight * soft_dice_loss(logits, y)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            running += loss.detach().item() * len(chunk)
            seen += len(chunk)

        val_scores = evaluate(model, val_set, cfg, device)
        val_table, _ = summarise(val_scores)
        val_mean = float(np.mean([v["mean"] for v in val_table.values() if v["mean"] is not None]))
        history.append(dict(epoch=epoch + 1, loss=running / max(seen, 1),
                            val_mean_dice=val_mean, lr=opt.param_groups[0]["lr"],
                            seconds=time.time() - t_epoch))
        flag = ""
        if val_mean > best["score"]:
            best = dict(epoch=epoch + 1, score=val_mean)
            torch.save(dict(model=model.state_dict(), config=asdict(cfg),
                            classes=CLASS_NAMES, epoch=epoch + 1, val_mean_dice=val_mean),
                       out_dir / "weights_best.pt")
            flag = "  <- best so far, saved"
        print(f"epoch {epoch + 1:3d}/{cfg.epochs}  loss {history[-1]['loss']:.4f}  "
              f"val Dice {val_mean:.4f}  {history[-1]['seconds']:.0f}s{flag}", flush=True)

    train_seconds = time.time() - t_start

    # ---- final evaluation, once, on the held-out subjects ------------------ #
    state = torch.load(out_dir / "weights_best.pt", map_location=device, weights_only=False)
    model.load_state_dict(state["model"])
    per_subject = evaluate(model, test_set, cfg, device)
    table, grouped = summarise(per_subject)

    print("\nheld-out subjects, Dice per structure")
    head = " | ".join(f"{n[:11]:>11s}" for n in CLASS_NAMES[1:])
    print(f"{'subject':16s} | {head}")
    for row in per_subject:
        print(f"{row['subject']:16s} | " + " | ".join(
            f"{(row['dice'][n] if row['dice'][n] is not None else float('nan')):11.3f}"
            for n in CLASS_NAMES[1:]))
    print(f"{'mean':16s} | " + " | ".join(
        f"{(table[n]['mean'] if table[n]['mean'] is not None else float('nan')):11.3f}"
        for n in CLASS_NAMES[1:]))

    print("\nby provenance — read this before reading any score above:")
    for label, g in grouped.items():
        print(f"  {label:30s} {g['structures']:2d} structures  "
              f"mean of means {g['mean_of_structure_means']:.4f}"
              if g["mean_of_structure_means"] is not None else f"  {label}: none")
    print("  a score against FreeSurfer's labels means 'agrees with FreeSurfer', not 'correct'.")

    # ---- fingerprint, metrics, curves -------------------------------------- #
    report = dict(
        purpose="learning anatomy, never diagnosis",
        dataset=dict(doi=ZENODO_DOI, record=ZENODO_RECORD, checksums=checksums),
        config=asdict(cfg),
        seed=cfg.seed,
        environment=dict(torch=torch.__version__, cuda=torch.version.cuda,
                         device=(torch.cuda.get_device_name(0) if device.type == "cuda" else "cpu"),
                         python=sys.version.split()[0]),
        split=dict(train=[s.name for s in train_subs], val=[s.name for s in val_subs],
                   held_out=[s.name for s in test_subs],
                   slices=dict(train=len(train_set), val=len(val_set), held_out=len(test_set))),
        model=dict(parameters=n_params, base_channels=cfg.base_channels, depth=cfg.depth,
                   input_slices=2 * cfg.context + 1),
        training=dict(seconds=train_seconds, best_epoch=best["epoch"],
                      best_val_mean_dice=best["score"], history=history),
        classes=[dict(index=i, name=n, provenance=p) for i, (n, p, _) in enumerate(CLASSES)],
        results=dict(per_subject=per_subject, per_structure=table, by_provenance=grouped),
    )
    payload = json.dumps(report, indent=2, sort_keys=False)
    (out_dir / "metrics.json").write_text(payload)
    report["fingerprint"] = hashlib.md5(payload.encode()).hexdigest()
    (out_dir / "metrics.json").write_text(json.dumps(report, indent=2))
    print("\n===== METRICS JSON =====")
    print(json.dumps(report, indent=2)[:4000])
    print("===== END (full copy in metrics.json) =====")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(11, 4))
        ax[0].plot([h["epoch"] for h in history], [h["loss"] for h in history])
        ax[0].set_xlabel("epoch"); ax[0].set_ylabel("training loss")
        ax[1].plot([h["epoch"] for h in history], [h["val_mean_dice"] for h in history])
        ax[1].set_xlabel("epoch"); ax[1].set_ylabel("validation mean Dice")
        fig.suptitle("brain use 1 — small U-Net, healthy structures (no clinical claim)")
        fig.tight_layout()
        fig.savefig(out_dir / "curves.png", dpi=150)
        print(f"curves written to {out_dir / 'curves.png'}")
    except Exception as exc:
        print(f"(curves skipped: {type(exc).__name__}: {exc})")

    print(f"\nweights:  {out_dir / 'weights_best.pt'}  (best epoch {best['epoch']})")
    print(f"metrics:  {out_dir / 'metrics.json'}")
    print(f"total:    {time.time() - t_start:.0f}s")
    print("\nThe weights are not published under a permissive licence: the T1 images carry")
    print("the terms of OASIS, NKI and MMRR. See the record's LICENSE before sharing them.")


if __name__ == "__main__":
    main()
