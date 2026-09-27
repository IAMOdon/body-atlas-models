#!/usr/bin/env python3
"""Brain, use 1, version 2: a 3D specialist trained toward expert truth.

    Body Atlas Models — for learning anatomy, never for diagnosis.
    Healthy brains only. No clinical claim. The weights are not published.

What changes from version 1
--------------------------
Version 1 learned eleven structures from FreeSurfer's automatic segmentation
(*aseg*) and could therefore only ever agree with a program. Version 2 trains
in two stages, so that it can be measured against labels a person drew:

  stage 1, pre-training   81 subjects, aseg labels, every structure.
                          No OASIS-TRT-20 subject takes part.
  stage 2, fine-tuning    the 20 OASIS-TRT-20 subjects, whose subcortical
                          structures were labelled by hand (CMA protocol,
                          Zenodo 22071825, CC BY-NC-ND 4.0). Four folds: each
                          subject is tested exactly once, by a model that
                          never saw it.
  stage 3, the model      one last fine-tuning on all twenty, for the median
                          number of steps the folds chose. This is the model of
                          record for the use. Nothing is held out from it, so
                          its performance is the cross-validated estimate of
                          stage 2 — an estimate, not a measurement on unseen
                          brains. Say it that way wherever it is quoted.

The cortex is manual (DKT protocol) in both stages and for all 101 subjects.
Cerebral white matter has no manual counterpart anywhere in the data: it stays
an *automatic* class, is reported as such, and is never counted as expert truth.

The two provenances are never mixed for one structure. Where the expert is
silent and aseg is not, the voxel teaches nothing at all (see `target_expert`).

What it reports
---------------
Per structure and per subject, on brains held out of every stage:
Dice, and the two distances that say where a boundary actually is —
Hausdorff-95 and the average symmetric surface distance, both in millimetres
read from the NIfTI affine. Each is reported twice and never averaged
together: against the manual labels ("correct") and against aseg ("agrees
with FreeSurfer"). The pre-trained model is measured on the same subjects
against the same manual labels, so the gain from fine-tuning is visible.

Licences, before anything is shared
-----------------------------------
The T1 images carry the terms of the projects that acquired them (OASIS, NKI,
MMRR). The expert subcortical labels are CC BY-NC-ND 4.0: no commercial use,
and no distribution of modified versions. The weights stay unpublished.

What it leaves on the runtime
-----------------------------
Everything lands in one output directory and is zipped at the very end, so a single
file can be pulled off before the runtime is torn down:

    out_v2/results_v2.json        the record: per structure AND per subject
    out_v2/weights_best.pt        stage 1, the best pre-training checkpoint
    out_v2/weights_fold{1..4}.pt  each fold's selected weights
    out_v2/weights_final.pt       the delivered model, fine-tuned on all twenty
    out_v2/overlay_<subject>.png  the model's segmentation drawn on the real scan
    out_v2.zip                    all of the above

The overlays carry MRI pixels. They are for looking at, not for a repository.

Usage
-----
    pip install nibabel torch scipy
    python colab_train_v2.py                     # both stages, self-timed
    python colab_train_v2.py --smoke             # a few minutes on a CPU
    python colab_train_v2.py --inventory         # list every code in the data
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
# 1. The two records, by identifier, size and checksum
# --------------------------------------------------------------------------- #
MAIN_DOI = "10.5281/zenodo.22070005"
MAIN_RECORD = "22070005"
MAIN_FILES = {
    # only release3: the other seven files of the record are not needed here
    "Mindboggle101_release3.zip": (5232272873, "7178353814033f9f56dc97bdef2d68e4"),
}

EXPERT_DOI = "10.5281/zenodo.22071825"
EXPERT_RECORD = "22071825"
EXPERT_FILES = {
    "OASIS-TRT-20_DKT31_CMA_labels_v2.zip": (6117496, "ca7652287d266a002a9ae8170611006c"),
    "README.md": (3263, "c21ecd209b595d3306fa15ff875853b2"),
    "README_subcortical_labels.txt": (903, "e5effa6a758ad8996ce42bad4d4ec78e"),
    "LICENSE": (779, "1e332ad1e6a5a6dcccd5a2ec8b82825e"),
}
# deliberately not fetched: OASIS-TRT-20_BrainCOLOR_labels_noncortex.zip carries the
# original Neuromorphometrics numbers on a different grid. Its codes collide with
# FreeSurfer's while meaning other structures, so mixing it in would produce labels
# that are silently wrong. The DKT31_CMA volumes are already converted.

EXPERT_COHORT = "OASIS-TRT-20"

# --------------------------------------------------------------------------- #
# 2. The classes, and where each one's truth comes from
# --------------------------------------------------------------------------- #
IGNORE = 255

# name, aseg codes, manual (CMA) codes, truth available
CLASSES = [
    ("background",              (),                 (),                "n/a"),
    ("cerebral cortex",         "cortex",           "cortex",          "manual"),
    ("cerebral white matter",   (2, 41, 251, 252, 253, 254, 255), (),  "automatic only"),
    ("lateral ventricle",       (4, 5, 43, 44, 31, 63), (4, 5, 43, 44, 31, 63), "manual"),
    ("third ventricle",         (14,),              (14,),             "manual"),
    ("fourth ventricle",        (15,),              (15,),             "manual"),
    ("thalamus",                (10, 49),           (10, 49),          "manual"),
    ("caudate",                 (11, 50),           (11, 50),          "manual"),
    ("putamen",                 (12, 51),           (12, 51),          "manual"),
    ("pallidum",                (13, 52),           (13, 52),          "manual"),
    ("hippocampus",             (17, 53),           (17, 53),          "manual"),
    ("amygdala",                (18, 54),           (18, 54),          "manual"),
    ("accumbens",               (26, 58),           (26, 58),          "manual"),
    ("ventral diencephalon",    (28, 60),           (28, 60),          "manual"),
    ("brainstem",               (16,),              (16,),             "manual"),
    ("cerebellar cortex",       (6, 8, 45, 47),     (6, 8, 45, 47),    "manual"),
    ("cerebellar white matter", (7, 46),            (7, 46),           "manual"),
    ("cerebellar vermis",       (),                 (630, 631, 632),   "manual only"),
]
CLASS_NAMES = [c[0] for c in CLASSES]
N_CLASSES = len(CLASSES)
IDX = {name: i for i, name in enumerate(CLASS_NAMES)}
CORTEX, WM, VERMIS = IDX["cerebral cortex"], IDX["cerebral white matter"], IDX["cerebellar vermis"]

# Structures either source labels that are not classes here. They are ignored, never
# called background: something is there, we simply do not teach it.
#   24 CSF, 30/62 vessel, 85 optic chiasm, 72 5th ventricle (a normal variant, 4 subjects),
#   74 a stray blob in OASIS-TRT-20-3, 77-80 hypointensities, 91/92 basal forebrain
#   (manual only, ~430 voxels: too small to measure at 1 mm).
ASEG_IGNORE = (24, 30, 62, 85, 72, 74, 77, 78, 79, 80, 91, 92)
MANUAL_IGNORE = (24, 30, 62, 85, 72, 74, 91, 92)

# classes whose score may be called "correct" — everything with manual truth
MANUAL_CLASSES = [i for i, c in enumerate(CLASSES) if c[3].startswith("manual") and i != 0]
AUTO_CLASSES = [i for i, c in enumerate(CLASSES) if c[3] == "automatic only"]


def _lut(which: int, ignore_codes) -> np.ndarray:
    """A lookup table from label code to class index, for one source."""
    lut = np.zeros(2100, np.uint8)
    for idx, spec in enumerate(CLASSES):
        codes = spec[which]
        if isinstance(codes, tuple):
            for code in codes:
                lut[code] = idx
    for code in ignore_codes:
        lut[code] = IGNORE
    lut[1000:] = CORTEX                 # every DKT cortical code, left or right
    return lut


ASEG_LUT = _lut(1, ASEG_IGNORE)
MANUAL_LUT = _lut(2, MANUAL_IGNORE)
MAPPED_ASEG = {int(c) for c in np.nonzero(ASEG_LUT[:1000])[0]}
MAPPED_MANUAL = {int(c) for c in np.nonzero(MANUAL_LUT[:1000])[0]}


def apply_lut(vol: np.ndarray, lut: np.ndarray) -> np.ndarray:
    return lut[np.clip(vol, 0, 2099)]


def target_pretrain(aseg: np.ndarray, manual_cortex: np.ndarray) -> np.ndarray:
    """Stage 1: aseg everywhere, the manual cortex on top of it."""
    out = apply_lut(aseg, ASEG_LUT)
    out[manual_cortex >= 1000] = CORTEX
    return out


def target_expert(cma: np.ndarray, aseg: np.ndarray) -> np.ndarray:
    """Stage 2: the expert decides; where the expert is silent, almost nothing is taught.

    Voxel by voxel:
      the expert names a structure of ours          -> that class
      the expert names one we do not model          -> ignore
      the expert is silent and aseg says white matter -> white matter
                                        (its only source anywhere in this dataset)
      the expert is silent and aseg names something -> ignore, never background:
                                        the expert did not confirm it
      both silent (outside the brain)               -> background
    """
    man = apply_lut(cma, MANUAL_LUT)
    asg = apply_lut(aseg, ASEG_LUT)
    out = man.copy()
    silent = man == 0
    out[silent & (asg == WM)] = WM
    out[silent & (asg != WM) & (asg != 0)] = IGNORE
    return out


# --------------------------------------------------------------------------- #
# 3. Configuration
# --------------------------------------------------------------------------- #
@dataclass
class Config:
    seed: int = 20260927
    patch: int = 96                 # voxels, 1 mm isotropic
    base_channels: int = 12
    depth: int = 4                  # downsamplings
    batch_size: int = 2
    accum: int = 2                  # effective batch 4
    lr_pretrain: float = 2e-3
    lr_finetune: float = 3e-4
    weight_decay: float = 1e-4
    warmup_frac: float = 0.03
    dice_weight: float = 1.0
    boundary_alpha: float = 4.0     # weight at a class boundary is 1 + alpha
    boundary_tau: float = 2.0       # millimetres, decay of that extra weight
    rare_class_frac: float = 0.8    # patches centred on a uniformly chosen present class
    amp: bool = True
    # time, not epochs: the script measures its own speed and fits the budget
    pretrain_minutes: float = 60.0
    finetune_minutes: float = 8.0
    folds: int = 4
    final_model: bool = True         # stage 3: the single model delivered for the use
    val_expert_subjects: int = 3    # inside each fold's fine-tuning pool
    val_patches: int = 160          # fixed patch set, model selection only
    checks: int = 12                # validations spread over a stage
    warmup_steps: int = 30          # discarded before timing: cuDNN is still choosing
    calib_steps: int = 30           # steps actually timed, to plan the schedule
    pretrain_steps: int = 0         # >0: pin stage 1 to exactly this many steps
    cold_sampling_boost: float = 3.0  # a class stage 1 never saw is drawn this much more
    cold_weight_boost: float = 2.0    # and counts this much more in stage 2's loss
    overlap: float = 0.5            # sliding window at inference
    crop_limit: int = 0             # >0: keep only this cube around the brain centre (smoke)
    aug_flip: float = 0.5
    aug_rotate_deg: float = 10.0
    aug_scale: float = 0.1
    aug_shift: float = 0.05
    aug_gamma: float = 0.25
    aug_noise: float = 0.02
    out_dir: str = "out_v2"


def parse_args():
    cfg = Config()
    p = argparse.ArgumentParser(description="brain use 1 v2: 3D, toward expert truth")
    p.add_argument("--work-dir", default="mindboggle")
    p.add_argument("--data-root", default=None,
                   help="an existing Mindboggle101_volumes directory")
    p.add_argument("--expert-root", default=None,
                   help="an existing OASIS-TRT-20_DKT31_CMA_labels_v2 directory")
    p.add_argument("--cache-dir", default=None, help="where the prepared volumes go")
    p.add_argument("--stage", choices=("all", "pretrain", "finetune"), default="all")
    p.add_argument("--resume", default=None, help="a weights_best.pt to fine-tune from")
    p.add_argument("--reuse-data", action="store_true",
                   help="if the data is already unpacked here, use it and skip the "
                        "download and the checksums")
    p.add_argument("--inventory", action="store_true",
                   help="list every label code in the data and stop")
    p.add_argument("--smoke", action="store_true", help="a tiny run, for catching bugs")
    p.add_argument("--no-final-model", action="store_true",
                   help="stop after the folds, without training the delivered model")
    for name, value in asdict(cfg).items():
        p.add_argument(f"--{name.replace('_', '-')}", type=type(value), default=value)
    args = p.parse_args()
    cfg = Config(**{k: getattr(args, k) for k in asdict(cfg)})
    if args.no_final_model:
        cfg.final_model = False
    if args.smoke:
        cfg.patch, cfg.base_channels, cfg.depth = 32, 4, 3
        cfg.batch_size, cfg.accum = 2, 1
        cfg.pretrain_minutes, cfg.finetune_minutes = 0.4, 0.25
        cfg.folds, cfg.val_expert_subjects = 2, 1
        cfg.val_patches, cfg.checks = 12, 2
        cfg.crop_limit = 72             # a small box: the point is bugs, not scores
        cfg.warmup_steps, cfg.calib_steps = 5, 5
        cfg.amp = False
        if cfg.out_dir == Config().out_dir:        # never override an explicit --out-dir
            cfg.out_dir = "out_v2_smoke"
    return cfg, args


# --------------------------------------------------------------------------- #
# 4. Fetch and verify
# --------------------------------------------------------------------------- #
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


def download(record: str, name: str, size: int, dest: Path, attempts: int = 6) -> None:
    url = f"https://zenodo.org/api/records/{record}/files/{name}/content"
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
                    if time.time() - last > 15:
                        print(f"    {name}: {100 * done / size:5.1f}%  {done / 1e9:.2f}/{size / 1e9:.2f} GB"
                              f"  {done / 1e6 / max(time.time() - t0, 1e-9):.1f} MB/s", flush=True)
                        last = time.time()
        except Exception as exc:
            print(f"    {name}: {type(exc).__name__}, resuming (attempt {attempt}/{attempts})", flush=True)
            time.sleep(3 * attempt)
    if not dest.exists() or dest.stat().st_size < size:
        raise RuntimeError(f"{name}: download did not complete")


def fetch_record(work: Path, record: str, files: dict) -> dict:
    work.mkdir(parents=True, exist_ok=True)
    checked = {}
    for name, (size, want) in files.items():
        path = work / name
        if not (path.exists() and path.stat().st_size == size):
            print(f"  fetching {name} ({size / 1e6:.1f} MB)", flush=True)
            download(record, name, size, path)
        got = md5_of(path)
        print(f"  {'ok' if got == want else 'MISMATCH':8s} {name:46s} {got}", flush=True)
        if got != want:
            raise RuntimeError(f"{name}: md5 {got} is not the record's {want}")
        checked[name] = got
    return checked


def extract_main(work: Path) -> Path:
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


def extract_expert(work: Path) -> Path:
    root = work / "extracted-expert"
    out = root / "OASIS-TRT-20_DKT31_CMA_labels_v2"
    if not out.is_dir():
        print("  unpacking OASIS-TRT-20_DKT31_CMA_labels_v2.zip", flush=True)
        with zipfile.ZipFile(work / "OASIS-TRT-20_DKT31_CMA_labels_v2.zip") as zf:
            zf.extractall(root)
    return out


# --------------------------------------------------------------------------- #
# 5. Prepare each subject once: crop, normalise, targets, boundary weights
# --------------------------------------------------------------------------- #
def boundary_weight(target: np.ndarray, zooms, cfg: Config) -> np.ndarray:
    """uint8 encoding of 1 + alpha*exp(-d/tau), d = mm to the nearest class boundary."""
    from scipy import ndimage

    edge = np.zeros(target.shape, bool)
    for axis in range(3):
        for shift in (1, -1):
            nb = np.roll(target, shift, axis)
            diff = (nb != target) & (target != IGNORE) & (nb != IGNORE)
            plane = [slice(None)] * 3
            plane[axis] = 0 if shift == 1 else -1
            diff[tuple(plane)] = False          # the wrapped face is not a boundary
            edge |= diff
    if not edge.any():
        return np.zeros(target.shape, np.uint8)
    d = ndimage.distance_transform_edt(~edge, sampling=zooms)
    w = np.exp(-d / max(cfg.boundary_tau, 1e-6))        # in [0, 1]
    return np.clip(np.rint(w * 255), 0, 255).astype(np.uint8)


def prepare_subject(subject: Path, expert_file, cfg: Config) -> dict | None:
    """Everything the training needs for one brain, cropped to its own brain box."""
    import nibabel as nib

    img = nib.as_closest_canonical(nib.load(str(subject / "t1weighted_brain.nii.gz")))
    zooms = tuple(float(z) for z in img.header.get_zooms()[:3])      # mm, read, never assumed
    vol = np.asarray(img.dataobj, dtype=np.float32)
    aseg = np.asarray(nib.as_closest_canonical(
        nib.load(str(subject / "labels.DKT31.manual+aseg.nii.gz"))).dataobj).astype(np.int32)
    manual = np.asarray(nib.as_closest_canonical(
        nib.load(str(subject / "labels.DKT31.manual.nii.gz"))).dataobj).astype(np.int32)
    cma = None
    if expert_file is not None:
        cma = np.asarray(nib.as_closest_canonical(
            nib.load(str(expert_file))).dataobj).astype(np.int32)
        if cma.shape != aseg.shape:
            raise RuntimeError(f"{subject.name}: expert labels are on another grid")

    brain = vol > 0
    if not brain.any():
        return None
    box = []
    for axis in range(3):
        on = np.any(brain, axis=tuple(a for a in range(3) if a != axis))
        lo, hi = int(np.argmax(on)), int(len(on) - np.argmax(on[::-1]))
        lo, hi = max(lo - 4, 0), min(hi + 4, brain.shape[axis])
        if hi - lo < cfg.patch:                          # a patch must fit in the crop
            grow = cfg.patch - (hi - lo)
            lo = max(lo - grow // 2, 0)
            hi = min(lo + cfg.patch, brain.shape[axis])
            lo = max(hi - cfg.patch, 0)
        box.append((lo, hi))
    if cfg.crop_limit:                                   # smoke runs: a small central box
        side = max(cfg.crop_limit, cfg.patch)
        box = [(max(0, (lo + hi) // 2 - side // 2),
                min(brain.shape[a], max(0, (lo + hi) // 2 - side // 2) + side))
               for a, (lo, hi) in enumerate(box)]
    sl = tuple(slice(lo, hi) for lo, hi in box)

    lo_i, hi_i = np.percentile(vol[brain], (1, 99))       # per subject: scanners differ
    image = np.clip((vol[sl] - lo_i) / max(hi_i - lo_i, 1e-6), 0, 1)
    image = np.rint(image * 255).astype(np.uint8)

    out = dict(name=subject.name, cohort=subject.parent.name.replace("_volumes", ""),
               zooms=zooms, box=box, shape=image.shape, image=image)
    out["aseg_target"] = target_pretrain(aseg, manual)[sl]
    if cma is not None:
        out["expert_target"] = target_expert(cma, aseg)[sl]
        out["train_target"] = out["expert_target"]
    else:
        out["train_target"] = out["aseg_target"]
    out["weight"] = boundary_weight(out["train_target"], zooms, cfg)
    out["counts"] = np.bincount(out["train_target"].reshape(-1), minlength=256)[:N_CLASSES]

    # where to centre patches: a bounded sample of voxels per class
    rng = np.random.default_rng(cfg.seed + abs(hash(subject.name)) % 10000)
    centres = {}
    for c in range(1, N_CLASSES):
        where = np.flatnonzero(out["train_target"].reshape(-1) == c)
        if where.size:
            take = where if where.size <= 1200 else rng.choice(where, 1200, replace=False)
            centres[c] = np.asarray(np.unravel_index(take, out["train_target"].shape)).T.astype(np.int16)
    inside = np.flatnonzero(image.reshape(-1) > 8)
    take = inside if inside.size <= 4000 else rng.choice(inside, 4000, replace=False)
    centres[0] = np.asarray(np.unravel_index(take, image.shape)).T.astype(np.int16)
    out["centres"] = centres
    return out


def inventory(volumes: Path, expert_dir) -> None:
    """Every code present in either source, and whether this script accounts for it."""
    import nibabel as nib
    from collections import Counter

    aseg_seen, man_seen = Counter(), Counter()
    subs = sorted(p for d in sorted(volumes.iterdir()) if d.is_dir()
                  for p in sorted(d.iterdir()) if p.is_dir())
    for n, sub in enumerate(subs, 1):
        a = np.asarray(nib.load(str(sub / "labels.DKT31.manual+aseg.nii.gz")).dataobj).astype(np.int32)
        for c in np.unique(a):
            if 0 < c < 1000:
                aseg_seen[int(c)] += 1
        if n % 20 == 0:
            print(f"  {n}/{len(subs)} aseg volumes read", flush=True)
    if expert_dir is not None:
        for f in sorted(Path(expert_dir).glob("*_DKT31_CMA_labels.nii.gz")):
            m = np.asarray(nib.load(str(f)).dataobj).astype(np.int32)
            for c in np.unique(m):
                if 0 < c < 1000:
                    man_seen[int(c)] += 1

    def report(title, seen, mapped, ignored):
        print(f"\n{title}")
        unaccounted = []
        for code, n in sorted(seen.items()):
            if code in ignored:
                state = "ignored"
            elif code in mapped:
                state = CLASS_NAMES[int(_state_lut(code, title))]
            else:
                state = "UNACCOUNTED"
                unaccounted.append(code)
            print(f"  {code:4d}  in {n:3d} subjects   {state}")
        print(f"  -> unaccounted codes: {unaccounted or 'none'}")

    def _state_lut(code, title):
        return (ASEG_LUT if "aseg" in title else MANUAL_LUT)[code]

    report("aseg volumes (all 101 subjects)", aseg_seen, MAPPED_ASEG, set(ASEG_IGNORE))
    report("manual CMA volumes (20 OASIS-TRT-20 subjects)", man_seen, MAPPED_MANUAL, set(MANUAL_IGNORE))


# --------------------------------------------------------------------------- #
# 6. Splits: no OASIS subject in pre-training, every OASIS subject tested once
# --------------------------------------------------------------------------- #
def build_splits(volumes: Path, cfg: Config, smoke: bool = False):
    by_cohort = {}
    for cohort_dir in sorted(p for p in volumes.iterdir() if p.is_dir()):
        subs = sorted(p for p in cohort_dir.iterdir() if p.is_dir())
        if subs:
            by_cohort[cohort_dir.name.replace("_volumes", "")] = subs

    expert = list(by_cohort.get(EXPERT_COHORT, []))
    pool = [s for name, subs in by_cohort.items() if name != EXPERT_COHORT for s in subs]
    if smoke:
        expert = expert[:6]
        pool = []
        for name, subs in by_cohort.items():
            if name != EXPERT_COHORT:
                pool += subs[:2]

    rng = random.Random(cfg.seed)
    pre_train, pre_val = [], []
    for name, subs in by_cohort.items():
        if name == EXPERT_COHORT:
            continue
        subs = [s for s in subs if s in pool]
        rng.shuffle(subs)
        n_val = max(1, round(0.15 * len(subs)))
        pre_val += subs[:n_val]
        pre_train += subs[n_val:]

    shuffled = list(expert)
    rng.shuffle(shuffled)
    folds = [shuffled[i::cfg.folds] for i in range(cfg.folds)]      # each subject in one fold

    assert not ({s.name for s in pre_train + pre_val} & {s.name for s in expert}), \
        "an OASIS subject reached pre-training"
    assert sum(len(f) for f in folds) == len(expert) and all(folds), "bad fold split"
    assert len({s.name for f in folds for s in f}) == len(expert), "a subject is in two folds"
    return pre_train, pre_val, folds, expert


# --------------------------------------------------------------------------- #
# 7. Patches
# --------------------------------------------------------------------------- #
class PatchSet:
    """Patches drawn from prepared subjects, weighted toward the rare structures."""

    def __init__(self, subjects: list, cfg: Config, name: str, boost: dict | None = None):
        self.subjects, self.cfg, self.name = subjects, cfg, name
        self.boost = boost or {}
        self.rng = np.random.default_rng(cfg.seed + len(name))
        counts = np.zeros(N_CLASSES, np.float64)
        for s in subjects:
            counts += s["counts"]
        self.share = counts / max(counts.sum(), 1)
        self.present = [c for c in range(1, N_CLASSES) if counts[c] > 0]

    def draw(self, rng=None):
        rng = rng or self.rng
        sub = self.subjects[rng.integers(len(self.subjects))]
        if rng.random() < self.cfg.rare_class_frac:
            options = [c for c in self.present if c in sub["centres"]]
            if options:
                # uniform over the structures present, except that a class stage 1 never
                # saw is drawn more often: it has to be learned from nothing, against
                # what stage 1 taught about the tissue around it.
                w = np.array([self.boost.get(c, 1.0) for c in options], np.float64)
                cls = int(options[int(rng.choice(len(options), p=w / w.sum()))])
            else:
                cls = 0
        else:
            cls = 0
        pts = sub["centres"][cls]
        centre = pts[rng.integers(len(pts))].astype(np.int64)
        return self.crop(sub, centre, rng)

    def crop(self, sub, centre, rng=None):
        p = self.cfg.patch
        start = []
        for axis in range(3):
            jitter = 0 if rng is None else int(rng.integers(-p // 6, p // 6 + 1))
            lo = int(centre[axis]) - p // 2 + jitter
            lo = max(0, min(lo, sub["shape"][axis] - p))
            start.append(lo)
        sl = tuple(slice(lo, lo + p) for lo in start)
        return (sub["image"][sl].astype(np.float32) / 255.0,
                sub["train_target"][sl].astype(np.int64),
                sub["weight"][sl].astype(np.float32) / 255.0)

    def fixed_set(self, n: int):
        rng = np.random.default_rng(self.cfg.seed + 7)
        return [self.draw(rng) for _ in range(n)]


# --------------------------------------------------------------------------- #
# 8. The model: a residual 3D U-Net
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
            self.skip = (nn.Identity() if cin == cout
                         else nn.Conv3d(cin, cout, 1, bias=False))
            self.act = nn.LeakyReLU(0.01, inplace=True)

        def forward(self, x):
            return self.act(self.b(self.a(x)) + self.skip(x))

    class UNet3D(nn.Module):
        def __init__(self):
            super().__init__()
            widths = [cfg.base_channels * 2 ** i for i in range(cfg.depth + 1)]
            self.encoders = nn.ModuleList()
            cin = 1
            for w in widths[:-1]:
                self.encoders.append(ResBlock(cin, w))
                cin = w
            self.bottom = ResBlock(widths[-2], widths[-1])
            self.ups, self.decoders = nn.ModuleList(), nn.ModuleList()
            cin = widths[-1]
            for w in reversed(widths[:-1]):
                self.ups.append(nn.ConvTranspose3d(cin, w, 2, 2))
                self.decoders.append(ResBlock(2 * w, w))
                cin = w
            self.head = nn.Conv3d(widths[0], N_CLASSES, 1)
            self.pool = nn.MaxPool3d(2)

        def forward(self, x):
            skips = []
            for enc in self.encoders:
                x = enc(x)
                skips.append(x)
                x = self.pool(x)
            x = self.bottom(x)
            for up, dec, skip in zip(self.ups, self.decoders, reversed(skips)):
                x = dec(torch.cat([up(x), skip], 1))
            return self.head(x)

    return UNet3D()


# --------------------------------------------------------------------------- #
# 9. Augmentation, on the GPU
# --------------------------------------------------------------------------- #
def augment(x, y, w, cfg: Config, gen):
    """x (N,1,D,H,W) float, y (N,D,H,W) long, w (N,D,H,W) float."""
    import torch
    import torch.nn.functional as F

    n, dev = x.shape[0], x.device
    if cfg.aug_flip:
        # after as_closest_canonical the first axis runs left to right, and every
        # class here merges the two sides, so a left-right flip stays true
        flip = torch.rand(n, device=dev, generator=gen) < cfg.aug_flip
        if flip.any():
            x[flip] = torch.flip(x[flip], dims=[2])
            y[flip] = torch.flip(y[flip], dims=[1])
            w[flip] = torch.flip(w[flip], dims=[1])

    ang = (torch.rand(n, 3, device=dev, generator=gen) * 2 - 1) * math.radians(cfg.aug_rotate_deg)
    sc = 1 + (torch.rand(n, 1, device=dev, generator=gen) * 2 - 1) * cfg.aug_scale
    sh = (torch.rand(n, 3, device=dev, generator=gen) * 2 - 1) * cfg.aug_shift
    cx, sx = torch.cos(ang[:, 0]), torch.sin(ang[:, 0])
    cy, sy = torch.cos(ang[:, 1]), torch.sin(ang[:, 1])
    cz, sz = torch.cos(ang[:, 2]), torch.sin(ang[:, 2])
    zero, one = torch.zeros_like(cx), torch.ones_like(cx)
    rx = torch.stack([one, zero, zero, zero, cx, -sx, zero, sx, cx], 1).view(n, 3, 3)
    ry = torch.stack([cy, zero, sy, zero, one, zero, -sy, zero, cy], 1).view(n, 3, 3)
    rz = torch.stack([cz, -sz, zero, sz, cz, zero, zero, zero, one], 1).view(n, 3, 3)
    rot = (rz @ ry @ rx) / sc.view(n, 1, 1)
    theta = torch.cat([rot, sh.view(n, 3, 1)], 2)

    grid = F.affine_grid(theta, list(x.shape), align_corners=False)
    x = F.grid_sample(x, grid, mode="bilinear", padding_mode="zeros", align_corners=False)
    pair = torch.stack([y.float(), w], 1)
    pair = F.grid_sample(pair, grid, mode="nearest", padding_mode="zeros", align_corners=False)
    y, w = pair[:, 0].long(), pair[:, 1]

    if cfg.aug_gamma:
        g = torch.exp((torch.rand(n, 1, 1, 1, 1, device=dev, generator=gen) * 2 - 1) * cfg.aug_gamma)
        x = x.clamp(0, 1) ** g
    if cfg.aug_noise:
        x = x + torch.randn(x.shape, device=dev, generator=gen) * cfg.aug_noise
    return x.clamp(0, 1), y, w


# --------------------------------------------------------------------------- #
# 10. Loss: boundary-weighted cross-entropy + soft Dice, both ignoring IGNORE
# --------------------------------------------------------------------------- #
def make_loss(class_weights, cfg: Config):
    import torch
    import torch.nn.functional as F

    def loss_fn(logits, y, w):
        valid = y != IGNORE
        n_valid = valid.sum().clamp(min=1)
        ce = F.cross_entropy(logits, torch.where(valid, y, torch.zeros_like(y)),
                             weight=class_weights, reduction="none")
        weight = 1.0 + cfg.boundary_alpha * w            # the boundary counts more
        ce = (ce * weight * valid).sum() / (weight * valid).sum().clamp(min=1)

        probs = F.softmax(logits, 1) * valid.unsqueeze(1)
        hot = F.one_hot(torch.where(valid, y, torch.zeros_like(y)), N_CLASSES)
        hot = hot.permute(0, 4, 1, 2, 3).float() * valid.unsqueeze(1)
        dims = (0, 2, 3, 4)
        inter, denom = (probs * hot).sum(dims), probs.sum(dims) + hot.sum(dims)
        here = denom[1:] > 0
        dice = (2 * inter[1:] + 1.0) / (denom[1:] + 1.0)
        dice_loss = 1 - (dice[here].mean() if here.any() else dice.mean() * 0)
        return ce + cfg.dice_weight * dice_loss, float(n_valid)

    return loss_fn


# --------------------------------------------------------------------------- #
# 11. Inference over a whole brain, and the metrics
# --------------------------------------------------------------------------- #
def gaussian_window(p: int, device):
    import torch
    t = torch.linspace(-1, 1, p, device=device)
    g = torch.exp(-(t ** 2) / (2 * 0.25))
    return (g[:, None, None] * g[None, :, None] * g[None, None, :]).clamp_min(1e-3)


def predict_volume(model, sub, cfg: Config, device):
    """Sliding window with 50 % overlap and a gaussian weight, over the brain box."""
    import torch

    p = cfg.patch
    stride = max(1, int(round(p * (1 - cfg.overlap))))
    shape = sub["shape"]
    starts = []
    for axis in range(3):
        pos = list(range(0, max(shape[axis] - p, 0) + 1, stride))
        if pos[-1] != shape[axis] - p:
            pos.append(max(shape[axis] - p, 0))
        starts.append(pos)

    acc = torch.zeros((N_CLASSES,) + tuple(shape), dtype=torch.float32, device=device)
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
            out = torch.softmax(model(x).float(), 1)
        for k, (i, j, l) in enumerate(coords):
            acc[:, i:i + p, j:j + p, l:l + p] += out[k] * win
            norm[i:i + p, j:j + p, l:l + p] += win
        batch.clear()
        coords.clear()

    for i in starts[0]:
        for j in starts[1]:
            for l in starts[2]:
                batch.append(image[i:i + p, j:j + p, l:l + p])
                coords.append((i, j, l))
                if len(batch) == max(1, cfg.batch_size * 2):
                    flush()
    flush()
    pred = (acc / norm.clamp_min(1e-6)).argmax(0).to(torch.uint8).cpu().numpy()
    return pred


def surface_of(mask: np.ndarray) -> np.ndarray:
    from scipy import ndimage
    if not mask.any():
        return mask
    inner = ndimage.binary_erosion(mask, ndimage.generate_binary_structure(3, 1),
                                   border_value=0)
    return mask & ~inner


def surface_distances(a: np.ndarray, b: np.ndarray, zooms):
    """Symmetric surface distances in millimetres, computed inside a bounding box."""
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
    sa, sb = surface_of(a[box]), surface_of(b[box])
    if not sa.any() or not sb.any():
        return None
    da = ndimage.distance_transform_edt(~sa, sampling=zooms)
    db = ndimage.distance_transform_edt(~sb, sampling=zooms)
    d_ab, d_ba = db[sa], da[sb]                       # a's surface to b, and back
    both = np.concatenate([d_ab, d_ba])
    return dict(assd_mm=float(both.mean()),
                hd95_mm=float(np.percentile(both, 95)),
                hd_mm=float(both.max()))


def score_volume(pred: np.ndarray, truth: np.ndarray, zooms, classes) -> dict:
    """Dice, HD95 and ASSD per class, ignoring voxels the truth does not teach."""
    valid = truth != IGNORE
    out = {}
    for c in classes:
        p, g = (pred == c) & valid, truth == c
        n_p, n_g = int(p.sum()), int(g.sum())
        row = dict(truth_voxels=n_g, predicted_voxels=n_p)
        row["dice"] = float(2 * np.logical_and(p, g).sum() / (n_p + n_g)) if n_p + n_g else None
        row.update(surface_distances(p, g, zooms) or dict(assd_mm=None, hd95_mm=None, hd_mm=None))
        out[CLASS_NAMES[c]] = row
    return out


def patch_dice(model, fixed, cfg: Config, device) -> float:
    """A fast proxy on a fixed patch set: model selection only, never reported."""
    import torch
    model.eval()
    inter = np.zeros(N_CLASSES)
    denom = np.zeros(N_CLASSES)
    with torch.no_grad():
        for start in range(0, len(fixed), max(1, cfg.batch_size)):
            chunk = fixed[start:start + max(1, cfg.batch_size)]
            x = torch.from_numpy(np.stack([c[0] for c in chunk])).unsqueeze(1).to(device)
            with torch.autocast("cuda", enabled=(cfg.amp and device.type == "cuda")):
                pred = model(x).argmax(1).cpu().numpy()
            truth = np.stack([c[1] for c in chunk])
            valid = truth != IGNORE
            for c in range(1, N_CLASSES):
                p, g = (pred == c) & valid, truth == c
                inter[c] += np.logical_and(p, g).sum()
                denom[c] += p.sum() + g.sum()
    scores = [2 * inter[c] / denom[c] for c in range(1, N_CLASSES) if denom[c] > 0]
    return float(np.mean(scores)) if scores else 0.0




# --------------------------------------------------------------------------- #
# 11b. Drawing it: the segmentation on the scan it came from
# --------------------------------------------------------------------------- #
STRUCTURE_COLOUR = {
    "cerebral cortex": "#3987e5", "cerebral white matter": "#55524a",
    "lateral ventricle": "#5fd4f2", "third ventricle": "#9fe0ee",
    "fourth ventricle": "#7ec4d8", "thalamus": "#e8a83c", "caudate": "#c46fd6",
    "putamen": "#ef7f5e", "pallidum": "#f4d35e", "hippocampus": "#4fbd82",
    "amygdala": "#a9d94f", "accumbens": "#f291b8", "ventral diencephalon": "#b2895c",
    "brainstem": "#8f86e8", "cerebellar cortex": "#5fd0bd",
    "cerebellar white matter": "#2f9c8c", "cerebellar vermis": "#f0e469",
}
ABOVE = ("cerebral cortex", "thalamus", "putamen", "pallidum", "lateral ventricle",
         "hippocampus")
BELOW = ("cerebellar cortex", "cerebellar white matter", "cerebellar vermis",
         "brainstem", "fourth ventricle")


def pick_slice(truth: np.ndarray, wanted, floor: int = 100) -> int:
    """The axial slice showing most of `wanted`, then most structures overall."""
    want = [IDX[n] for n in wanted]
    best, best_key = 0, (-1, -1)
    for k in range(truth.shape[2]):
        col = truth[:, :, k]
        counts = {c: int((col == c).sum()) for c in range(1, N_CLASSES)}
        key = (sum(counts[c] >= floor for c in want),
               sum(v >= floor for v in counts.values()))
        if key > best_key:
            best, best_key = k, key
    return best


def draw_overlays(sub: dict, pred: np.ndarray, out_dir: Path) -> Path | None:
    """Three panels at two axial levels: the scan, the model, the expert."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.colors import to_rgb
        from matplotlib.patches import Rectangle
    except Exception as exc:
        print(f"  (overlay skipped: {type(exc).__name__}: {exc})", flush=True)
        return None

    truth, image = sub["expert_target"], sub["image"]
    levels = [pick_slice(truth, ABOVE), pick_slice(truth, BELOW)]
    offset = sub["box"][2][0]          # the crop's origin: report slices of the volume
    valid = truth != IGNORE

    def panel_data(k):
        t, p = truth[:, :, k], pred[:, :, k]
        here = [c for c in range(1, N_CLASSES)
                if (t == c).sum() > 100 or (p == c).sum() > 100]
        scores = {}
        for c in here:
            a = (p == c) & valid[:, :, k]
            g = t == c
            n = a.sum() + g.sum()
            scores[c] = float(2 * np.logical_and(a, g).sum() / n) if n else None
        return dict(k=k, image=image[:, :, k], truth=t, pred=p, here=here, dice=scores)

    rows = [panel_data(k) for k in levels]
    order = [c for c in range(1, N_CLASSES) if any(c in r["here"] for r in rows)]
    order.sort(key=lambda c: -max(int((r["truth"] == c).sum()) for r in rows))

    def rgba(lab, here):
        out = np.zeros(lab.shape + (4,), np.float32)
        for c in here:
            m = lab == c
            out[m, :3] = to_rgb(STRUCTURE_COLOUR[CLASS_NAMES[c]])
            out[m, 3] = 0.68
        return out

    W, H, INK, INK2, MUTED = 1900, 1900, "#f8f7f4", "#c3c2b7", "#6f6e66"
    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
    fig.patch.set_facecolor("#0d0d0c")
    fig.text(0.031, 0.966, "what the model segments, on one real brain", fontsize=17,
             color=INK)
    fig.text(0.031, 0.941, f"{sub['name']} — a brain this model never saw, segmented in 3D "
             f"and read off two axial levels", fontsize=9, color=INK2, style="italic")
    for i, c in enumerate(("the scan: T1-weighted MRI", "what the model says",
                           "what the expert drew")):
        fig.text(0.031 + i * 0.318 + 0.1475, 0.908, c, fontsize=9, color=INK, ha="center")

    pw = 0.295
    ph = pw * W / H
    captions = [f"above the tentorium, axial slice {levels[0] + offset}",
                f"the posterior fossa, axial slice {levels[1] + offset}"]
    for r, top in enumerate((0.882, 0.554)):
        fig.text(0.031, top + 0.007, captions[r], fontsize=7.6, color=INK2)
        for i in range(3):
            ax = fig.add_axes([0.031 + i * 0.318, top - ph, pw, ph])
            ax.imshow(rows[r]["image"].T, cmap="gray", origin="lower",
                      interpolation="nearest")
            if i:
                lab = rows[r]["pred"] if i == 1 else rows[r]["truth"]
                ax.imshow(rgba(lab, rows[r]["here"]).transpose(1, 0, 2), origin="lower",
                          interpolation="nearest")
            ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values():
                s.set_color("#262623")

    ly = 0.190
    fig.text(0.031, ly + 0.040, "Dice against the expert labels, on each slice",
             fontsize=7.6, color=INK2)
    for col in range(3):
        for j, r in enumerate(rows):
            fig.text(0.031 + col * 0.320 + 0.236 + j * 0.044, ly + 0.020,
                     f"slice {r['k'] + offset}", fontsize=6.2, color=MUTED, ha="right")
    for i, c in enumerate(order):
        col, row = i // 5, i % 5
        x, yy = 0.031 + col * 0.320, ly - row * 0.024
        fig.patches.append(Rectangle((x, yy), 0.011, 0.014, transform=fig.transFigure,
                                     facecolor=STRUCTURE_COLOUR[CLASS_NAMES[c]],
                                     edgecolor="none"))
        fig.text(x + 0.017, yy + 0.002, CLASS_NAMES[c], fontsize=6.8, color=INK2)
        for j, r in enumerate(rows):
            s = r["dice"].get(c)
            fig.text(x + 0.236 + j * 0.044, yy + 0.002,
                     f"{s:.3f}" if s is not None else "—", fontsize=6.8,
                     color=INK if s is not None else MUTED, ha="right")

    fig.text(0.031, 0.043, "Whole-volume 3D segmentation, read off two slices. The model "
             "was fine-tuned on expert labels and never saw this brain.", fontsize=6.8,
             color=MUTED)
    fig.text(0.031, 0.028, "Healthy anatomy, for learning. Not a diagnosis, and nothing "
             "about any person. Mindboggle-101, expert subcortical labels "
             "doi:10.5281/zenodo.22071825.", fontsize=6.8, color=MUTED)
    fig.text(0.031, 0.013, "This image contains MRI pixels: it belongs with the run, "
             "never in a repository.", fontsize=6.8, color=MUTED)

    print(f"    {sub['name']}: axial slices {levels[0] + offset} and "
          f"{levels[1] + offset} of the volume", flush=True)
    path = out_dir / f"overlay_{sub['name']}.png"
    fig.savefig(path, dpi=200, facecolor="#0d0d0c")
    plt.close(fig)
    return path


# --------------------------------------------------------------------------- #
# 12. One training stage, fitted to a wall-clock budget
# --------------------------------------------------------------------------- #
def train_stage(model, train_set: PatchSet, val_fixed, cfg: Config, device, *,
                minutes: float, lr: float, label: str, fixed_steps: int | None = None,
                weight_boost: dict | None = None):
    """Train until the budget is spent, or for exactly `fixed_steps` steps.

    `val_fixed=None` means no validation and no model selection: the weights at the
    last step are the result. That is what stage 3 needs — with every subject in the
    training set there is nothing left to select on, and selecting on training data
    would quietly turn a fit into a reported score.
    """
    import torch

    # inverse-root of the class share, so the pallidum is not drowned by the cortex.
    # A class absent from this stage's targets gets weight 0: cross-entropy never uses
    # it, and leaving it at 1/sqrt(0) would distort every other weight.
    share = np.asarray(train_set.share, np.float64)
    loss_weights = np.zeros(N_CLASSES, np.float64)
    here = share > 0
    loss_weights[here] = 1.0 / np.sqrt(share[here])
    loss_weights[0] *= 0.5                                   # background needs no boost
    for c, m in (weight_boost or {}).items():                # the cold-start classes
        loss_weights[c] *= m
    loss_weights /= loss_weights[here].mean()
    class_weights = torch.tensor(loss_weights, dtype=torch.float32, device=device)
    loss_fn = make_loss(class_weights, cfg)

    opt = torch.optim.AdamW(model.parameters(), lr, weight_decay=cfg.weight_decay)
    scaler = torch.amp.GradScaler("cuda", enabled=(cfg.amp and device.type == "cuda"))
    gen = torch.Generator(device=device)
    gen.manual_seed(cfg.seed)

    budget = minutes * 60.0
    total = 10 ** 9                       # replaced once the speed is known
    warm, calib_steps = cfg.warmup_steps, cfg.warmup_steps + cfg.calib_steps
    t_warm = None
    history, best = [], dict(step=-1, score=-1.0, state=None)
    t0 = time.time()
    step = 0
    next_check = None
    plan = f"{fixed_steps} steps" if fixed_steps else f"budget {minutes:.1f} min"
    print(f"\n[{label}] {plan}, lr {lr:g}, {len(train_set.subjects)} subjects, "
          f"patch {cfg.patch}^3, selection "
          f"{'on a held-out set' if val_fixed else 'none (last step wins)'}", flush=True)

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
                logits = model(x)
                loss, _ = loss_fn(logits, y, w)
            scaler.scale(loss / cfg.accum).backward()
        scaler.step(opt)
        scaler.update()
        step += 1

        if step == warm:
            t_warm = time.time()                    # start the clock only now
        if step == calib_steps:
            # Timing the first steps measures cuDNN choosing its kernels, not training.
            # The previous run under-planned by 30 % that way and left 18 minutes of its
            # budget unused, so the rate is taken over the steps after the warm-up.
            rate = (calib_steps - warm) / max(time.time() - t_warm, 1e-9)
            remaining = budget - (time.time() - t0)
            total = max(calib_steps + 1, int(fixed_steps or calib_steps + rate * remaining))
            next_check = max(1, total // cfg.checks)
            print(f"[{label}] {rate:.2f} steps/s measured after a {warm}-step warm-up "
                  f"-> {total} steps planned ({total * cfg.batch_size * cfg.accum} patches), "
                  f"validating every {next_check} steps", flush=True)

        if step >= calib_steps:
            frac = step / max(total, 1)
            warm = cfg.warmup_frac
            scale = (frac / warm) if frac < warm else 0.5 * (1 + math.cos(
                math.pi * min((frac - warm) / max(1 - warm, 1e-9), 1.0)))
            for group in opt.param_groups:
                group["lr"] = lr * max(scale, 1e-3)

        if val_fixed and step >= calib_steps and (step % next_check == 0 or step >= total):
            score = patch_dice(model, val_fixed, cfg, device)
            history.append(dict(step=step, loss=float(loss.detach()), patch_dice=score,
                                seconds=time.time() - t0))
            flag = ""
            if score > best["score"]:
                best = dict(step=step, score=score,
                            state={k: v.detach().cpu().clone() for k, v in model.state_dict().items()})
                flag = "  <- best"
            print(f"[{label}] step {step:5d}/{total}  loss {float(loss.detach()):.4f}  "
                  f"val patch Dice {score:.4f}  {time.time() - t0:5.0f}s{flag}", flush=True)

        if step >= total:
            break
        if fixed_steps is None and time.time() - t0 > budget * 1.5:
            break                                   # the calibration was optimistic
        if fixed_steps is not None and time.time() - t0 > budget * 3:
            raise RuntimeError(f"[{label}] {step}/{total} steps in {time.time() - t0:.0f}s: "
                               "far slower than the folds, refusing to run away")

    if best["state"] is not None:
        model.load_state_dict(best["state"])
    return dict(steps=step, planned=total, seconds=time.time() - t0,
                selection="held-out patches" if val_fixed else "none, last step",
                best_step=best["step"], best_patch_dice=best["score"], history=history)


# --------------------------------------------------------------------------- #
# 13. Run both stages and write the record
# --------------------------------------------------------------------------- #
def main():
    cfg, args = parse_args()
    print(__doc__.strip().split("\n\n")[1], "\n", flush=True)

    import torch

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    name = torch.cuda.get_device_name(0) if device.type == "cuda" else "cpu"
    print(f"torch {torch.__version__} | device {device} | {name}", flush=True)
    print(f"this script: sha256 {sha256_of_self()}", flush=True)
    if device.type != "cuda":
        cfg.amp = False
        print("!! no GPU visible: only --smoke makes sense here", flush=True)

    random.seed(cfg.seed)
    np.random.seed(cfg.seed)
    torch.manual_seed(cfg.seed)
    torch.cuda.manual_seed_all(cfg.seed)
    torch.backends.cudnn.benchmark = True

    # ---- data -------------------------------------------------------------- #
    checksums = {}
    if args.data_root:
        volumes = Path(args.data_root)
        expert_dir = Path(args.expert_root) if args.expert_root else None
        print(f"using local data at {volumes} (checksums not re-read)", flush=True)
    elif args.reuse_data and (Path(args.work_dir) / "extracted" /
                              "Mindboggle101_release3" / "Mindboggle101_volumes").is_dir():
        work = Path(args.work_dir)
        volumes = work / "extracted" / "Mindboggle101_release3" / "Mindboggle101_volumes"
        expert_dir = work / "extracted-expert" / "OASIS-TRT-20_DKT31_CMA_labels_v2"
        if not expert_dir.is_dir():                     # 7 MB: cheap enough to be sure
            print("expert labels missing, fetching them", flush=True)
            checksums[EXPERT_DOI] = fetch_record(work, EXPERT_RECORD, EXPERT_FILES)
            expert_dir = extract_expert(work)
        n_sub = len([p for d in volumes.iterdir() if d.is_dir()
                     for p in d.iterdir() if p.is_dir()])
        print(f"reusing the data already on this runtime: {volumes} ({n_sub} subjects).\n"
              f"  checksums are NOT re-read; they were verified when it was fetched.",
              flush=True)
        checksums["note"] = ("data reused from the runtime; the record checksums were "
                             "verified when it was first fetched in this session, not again")
    else:
        work = Path(args.work_dir)
        print(f"fetching record {MAIN_RECORD} ({MAIN_DOI}) into {work}", flush=True)
        checksums[MAIN_DOI] = fetch_record(work, MAIN_RECORD, MAIN_FILES)
        print(f"fetching record {EXPERT_RECORD} ({EXPERT_DOI}) — the expert labels, "
              f"CC BY-NC-ND 4.0", flush=True)
        checksums[EXPERT_DOI] = fetch_record(work, EXPERT_RECORD, EXPERT_FILES)
        volumes = extract_main(work)
        expert_dir = extract_expert(work)
    assert volumes.is_dir(), f"no volumes at {volumes}"

    if args.inventory:
        inventory(volumes, expert_dir)
        return

    pre_train, pre_val, folds, expert = build_splits(volumes, cfg, smoke=args.smoke)
    print(f"\nsplit: {len(pre_train)} pre-train | {len(pre_val)} pre-val (aseg) | "
          f"{len(expert)} expert subjects in {cfg.folds} folds "
          f"({[len(f) for f in folds]})", flush=True)

    def expert_file(sub: Path):
        f = Path(expert_dir) / f"{sub.name}_DKT31_CMA_labels.nii.gz"
        if not f.exists():
            raise RuntimeError(f"no expert labels for {sub.name}")
        return f

    t_prep = time.time()
    prepared = {}
    todo = [(s, None) for s in pre_train + pre_val] + [(s, expert_file(s)) for s in expert]
    for n, (sub, ef) in enumerate(todo, 1):
        got = prepare_subject(sub, ef, cfg)
        if got is None:
            print(f"  {sub.name}: no brain voxels, skipped", flush=True)
            continue
        prepared[sub.name] = got
        if n % 10 == 0 or n == len(todo):
            print(f"  prepared {n}/{len(todo)} subjects ({time.time() - t_prep:.0f}s)", flush=True)

    pre_train_set = PatchSet([prepared[s.name] for s in pre_train], cfg, "pretrain")
    pre_val_set = PatchSet([prepared[s.name] for s in pre_val], cfg, "preval")
    print("\nclass share of the pre-training targets (aseg + manual cortex):")
    for c in range(N_CLASSES):
        note = "" if pre_train_set.share[c] > 0 else "   <- absent: learned only in stage 2"
        print(f"  {CLASS_NAMES[c]:24s} {100 * pre_train_set.share[c]:7.4f}%  "
              f"{CLASSES[c][3]}{note}", flush=True)

    # A class with no share of the pre-training targets cannot be learned in stage 1 at
    # all: aseg has no label for it, and stage 1 actively learns that its territory
    # belongs to the neighbour. Stage 2 has to undo that from a handful of brains, so it
    # draws those patches more often and weighs them more. Without this the outcome is a
    # coin toss: the same protocol gave 0.804 once and 0.000 the next time.
    cold = [c for c in range(1, N_CLASSES) if pre_train_set.share[c] == 0]
    sample_boost = {c: cfg.cold_sampling_boost for c in cold}
    weight_boost = {c: cfg.cold_weight_boost for c in cold}
    if cold:
        print(f"\ncold-start classes, absent from stage 1: "
              f"{', '.join(CLASS_NAMES[c] for c in cold)}")
        print(f"  in stage 2 they are sampled x{cfg.cold_sampling_boost:g} and weighed "
              f"x{cfg.cold_weight_boost:g}", flush=True)

    model = build_model(cfg).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"\nresidual 3D U-Net: {n_params:,d} parameters "
          f"({cfg.depth} downsamplings, {cfg.base_channels} channels at the top, "
          f"{N_CLASSES} outputs, patch {cfg.patch}^3)", flush=True)

    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- stage 1 ----------------------------------------------------------- #
    if args.resume:
        state = torch.load(args.resume, map_location=device, weights_only=False)
        model.load_state_dict(state["model"])
        stage1 = state.get("stage1", {"note": f"loaded from {args.resume}"})
        print(f"\nstage 1 skipped: weights loaded from {args.resume}", flush=True)
    else:
        stage1 = train_stage(model, pre_train_set, pre_val_set.fixed_set(cfg.val_patches),
                             cfg, device, minutes=cfg.pretrain_minutes,
                             lr=cfg.lr_pretrain, label="pre-train",
                             fixed_steps=(cfg.pretrain_steps or None))
        torch.save(dict(model=model.state_dict(), config=asdict(cfg),
                        classes=CLASS_NAMES, stage1=stage1), out_dir / "weights_best.pt")
    pretrain_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    if args.stage == "finetune" and not args.resume:
        raise SystemExit("--stage finetune needs --resume weights_best.pt")

    if args.stage == "pretrain":
        print("\nstage 1 only, as asked. Weights in weights_best.pt", flush=True)
        return

    # ---- the pre-trained model, measured against the expert labels ---------- #
    print("\nthe pre-trained model on the 20 expert brains "
          "(never trained on any of them):", flush=True)
    baseline = {}
    for sub in expert:
        s = prepared[sub.name]
        pred = predict_volume(model, s, cfg, device)
        baseline[sub.name] = dict(
            vs_manual=score_volume(pred, s["expert_target"], s["zooms"], MANUAL_CLASSES),
            vs_aseg=score_volume(pred, s["aseg_target"], s["zooms"],
                                 MANUAL_CLASSES + AUTO_CLASSES))
        print(f"  {sub.name}: done", flush=True)

    # ---- stage 2: one fine-tuning per fold --------------------------------- #
    tuned, fold_reports = {}, []
    to_draw = {}                    # predictions kept for the overlays, from fold 1 only:
                                    # a brain the model that segmented it never saw
    rng = random.Random(cfg.seed + 1)
    for k, test_subs in enumerate(folds):
        pool = [s for f, group in enumerate(folds) if f != k for s in group]
        pool = list(pool)
        rng.shuffle(pool)
        n_val = min(cfg.val_expert_subjects, max(1, len(pool) - 1))
        val_subs, train_subs = pool[:n_val], pool[n_val:]
        names = dict(train=[s.name for s in train_subs], val=[s.name for s in val_subs],
                     test=[s.name for s in test_subs])
        assert not set(names["test"]) & set(names["train"]), "a test subject is fine-tuned on"
        assert not set(names["test"]) & set(names["val"]), "a test subject is selected on"
        assert not set(names["train"]) & set(names["val"]), "a subject is both train and val"
        print(f"\n=== fold {k + 1}/{cfg.folds}: fine-tune on {len(train_subs)}, "
              f"select on {len(val_subs)}, test on {len(test_subs)} "
              f"({', '.join(names['test'])})", flush=True)

        model.load_state_dict(pretrain_state)             # every fold starts from stage 1
        ft_train = PatchSet([prepared[s.name] for s in train_subs], cfg, f"ft{k}",
                            boost=sample_boost)
        ft_val = PatchSet([prepared[s.name] for s in val_subs], cfg, f"fv{k}")
        report = train_stage(model, ft_train, ft_val.fixed_set(cfg.val_patches), cfg, device,
                             minutes=cfg.finetune_minutes, lr=cfg.lr_finetune,
                             label=f"fine-tune {k + 1}", weight_boost=weight_boost)
        report["subjects"] = names
        fold_reports.append(report)
        torch.save(dict(model=model.state_dict(), config=asdict(cfg), classes=CLASS_NAMES,
                        fold=k + 1, subjects=names), out_dir / f"weights_fold{k + 1}.pt")

        for sub in test_subs:
            s = prepared[sub.name]
            pred = predict_volume(model, s, cfg, device)
            tuned[sub.name] = dict(
                fold=k + 1,
                vs_manual=score_volume(pred, s["expert_target"], s["zooms"], MANUAL_CLASSES),
                vs_aseg=score_volume(pred, s["aseg_target"], s["zooms"],
                                     MANUAL_CLASSES + AUTO_CLASSES))
            if k == 0 and len(to_draw) < 2:
                to_draw[sub.name] = pred.copy()
            print(f"  {sub.name}: scored", flush=True)

    # ---- stage 3: the model delivered for this use ------------------------- #
    final, final_fit = None, {}
    if cfg.final_model:
        chosen = [r["best_step"] for r in fold_reports if r["best_step"] > 0]
        target = max(1, int(np.median(chosen))) if chosen else None
        print(f"\n=== the delivered model: fine-tuned on all {len(expert)} expert brains "
              f"for {target} steps, the median the folds selected.\n"
              f"    Nothing is held out from it. The numbers to quote for it are the "
              f"cross-validated ones above.", flush=True)
        model.load_state_dict(pretrain_state)
        all_expert = PatchSet([prepared[s.name] for s in expert], cfg, "final",
                              boost=sample_boost)
        final = train_stage(model, all_expert, None, cfg, device,
                            minutes=cfg.finetune_minutes, lr=cfg.lr_finetune,
                            label="final", fixed_steps=target, weight_boost=weight_boost)
        final["subjects"] = [s.name for s in expert]
        final["how_to_quote_it"] = (
            "Fine-tuned on all twenty expert brains, so no brain is left to test it. "
            "Its performance is the 4-fold cross-validated estimate in "
            "results.against_manual.after_finetune: an estimate, not a measurement on "
            "unseen brains. The figures below under fit_on_its_own_subjects are a fit, "
            "not a performance, and must never be quoted as one.")
        torch.save(dict(model=model.state_dict(), config=asdict(cfg), classes=CLASS_NAMES,
                        stage1=stage1, stage2=fold_reports, stage3=final),
                   out_dir / "weights_final.pt")
        for sub in expert:
            s = prepared[sub.name]
            pred = predict_volume(model, s, cfg, device)
            final_fit[sub.name] = dict(vs_manual=score_volume(
                pred, s["expert_target"], s["zooms"], MANUAL_CLASSES))
        print("    the delivered model was scored on its own training brains "
              "(a fit, kept apart in the record)", flush=True)

    # ---- summarise --------------------------------------------------------- #
    def summarise(rows: dict, key: str, classes):
        out = {}
        for c in classes:
            cn = CLASS_NAMES[c]
            for metric in ("dice", "hd95_mm", "assd_mm"):
                vals = [r[key][cn][metric] for r in rows.values()
                        if r[key].get(cn, {}).get(metric) is not None]
                out.setdefault(cn, dict(provenance=CLASSES[c][3], subjects=len(vals)))
                out[cn][metric] = dict(mean=float(np.mean(vals)) if vals else None,
                                       std=float(np.std(vals)) if vals else None,
                                       min=float(np.min(vals)) if vals else None,
                                       max=float(np.max(vals)) if vals else None)
        return out

    after_manual = summarise(tuned, "vs_manual", MANUAL_CLASSES)
    if final is not None:
        final["fit_on_its_own_subjects"] = summarise(final_fit, "vs_manual", MANUAL_CLASSES)
    before_manual = summarise(baseline, "vs_manual", MANUAL_CLASSES)
    after_aseg = summarise(tuned, "vs_aseg", MANUAL_CLASSES + AUTO_CLASSES)
    before_aseg = summarise(baseline, "vs_aseg", MANUAL_CLASSES + AUTO_CLASSES)

    print("\n" + "=" * 100)
    print("against the MANUAL labels — the expert truth. 'correct', for these structures.")
    print(f"{'structure':24s} {'Dice before':>11s} {'Dice after':>10s} {'delta':>7s} "
          f"{'HD95 mm':>8s} {'ASSD mm':>8s}  provenance")
    for c in MANUAL_CLASSES:
        cn = CLASS_NAMES[c]
        b = before_manual[cn]["dice"]["mean"]
        a = after_manual[cn]["dice"]["mean"]
        h = after_manual[cn]["hd95_mm"]["mean"]
        s = after_manual[cn]["assd_mm"]["mean"]
        fmt = lambda v, w=7, d=3: (f"{v:{w}.{d}f}" if v is not None else f"{'--':>{w}s}")
        print(f"{cn:24s} {fmt(b, 11)} {fmt(a, 10)} "
              f"{fmt((a - b) if (a is not None and b is not None) else None)} "
              f"{fmt(h, 8, 2)} {fmt(s, 8, 2)}  {CLASSES[c][3]}")
    print("\nagainst ASEG — 'agrees with FreeSurfer', not 'correct'. Never averaged with the above.")
    for c in MANUAL_CLASSES + AUTO_CLASSES:
        cn = CLASS_NAMES[c]
        b, a = before_aseg[cn]["dice"]["mean"], after_aseg[cn]["dice"]["mean"]
        fmt = lambda v: (f"{v:7.3f}" if v is not None else f"{'--':>7s}")
        print(f"  {cn:24s} before {fmt(b)}   after {fmt(a)}   {CLASSES[c][3]}")
    print("=" * 100, flush=True)

    report = dict(
        purpose="learning anatomy, never diagnosis",
        what_this_is="Version 2 of brain use 1: a 3D residual U-Net pre-trained on "
                     "FreeSurfer aseg labels, then fine-tuned and measured against "
                     "manually labelled subcortical structures.",
        records=dict(images_and_cortex=dict(doi=MAIN_DOI, licence="CC BY 4.0"),
                     expert_subcortex=dict(doi=EXPERT_DOI, licence="CC BY-NC-ND 4.0",
                                           note="no commercial use, no distribution of "
                                                "modified versions; the weights stay unpublished"),
                     checksums=checksums),
        environment=dict(torch=torch.__version__, cuda=torch.version.cuda, device=name,
                         python=sys.version.split()[0],
                         script_sha256=sha256_of_self()),
        config=asdict(cfg),
        model=dict(parameters=n_params, architecture="residual 3D U-Net",
                   depth=cfg.depth, base_channels=cfg.base_channels,
                   patch=cfg.patch, outputs=N_CLASSES),
        classes=[dict(index=i, name=n, truth=CLASSES[i][3]) for i, n in enumerate(CLASS_NAMES)],
        split=dict(pretrain=[s.name for s in pre_train], pretrain_val=[s.name for s in pre_val],
                   expert_folds=[[s.name for s in f] for f in folds],
                   rule="no OASIS-TRT-20 subject is in pre-training; each is tested once, "
                        "by a model that never saw it"),
        cold_start=dict(classes=[CLASS_NAMES[c] for c in cold],
                        sampling_boost=cfg.cold_sampling_boost,
                        weight_boost=cfg.cold_weight_boost,
                        why="absent from the pre-training labels, and stage 1 learns that "
                            "their territory belongs to a neighbour; stage 2 has to undo "
                            "that from twelve brains"),
        stage1=stage1,
        stage2=fold_reports,
        stage3=final,
        delivered_model=(None if final is None else dict(
            weights="weights_final.pt (not published: see the licences above)",
            trained_on=final["subjects"], steps=final["steps"],
            performance="the 4-fold cross-validated estimate in "
                        "results.against_manual.after_finetune",
            not_a_performance="stage3.fit_on_its_own_subjects")),
        results=dict(
            against_manual=dict(after_finetune=after_manual, before_finetune=before_manual,
                                per_subject=tuned, per_subject_pretrained=baseline),
            against_aseg=dict(after_finetune=after_aseg, before_finetune=before_aseg),
            read_this_first=[
                "Dice, HD95 and ASSD against the manual labels are the only 'correct' numbers here.",
                "The same metrics against aseg mean 'agrees with FreeSurfer', nothing more.",
                "Cerebral white matter has no manual labels in this dataset: it is an "
                "automatic class, reported apart, never counted as expert agreement.",
                "HD95 and ASSD are in millimetres taken from the NIfTI affine, and neither "
                "is ever optimised: the loss uses a boundary-weighted cross-entropy instead.",
                "Whole volumes, not sampled slices: these numbers are not comparable with "
                "version 1's.",
                "The twenty expert numbers come from four models, one per fold, each scoring "
                "the five brains it never saw. The single delivered model is fine-tuned on all "
                "twenty; its performance is this cross-validated estimate, not a measurement "
                "on brains held out from it.",
            ]),
    )
    payload = json.dumps(report, indent=2)
    report["fingerprint"] = hashlib.md5(payload.encode()).hexdigest()
    (out_dir / "results_v2.json").write_text(json.dumps(report, indent=2))
    print(f"\nresults: {out_dir / 'results_v2.json'}  "
          f"({(out_dir / 'results_v2.json').stat().st_size / 1e3:.0f} kB)")

    # ---- draw it, on brains the model that segmented them never saw --------- #
    print("\ndrawing the segmentation on the scans it came from:", flush=True)
    for subject_name, pred in to_draw.items():
        path = draw_overlays(prepared[subject_name], pred, out_dir)
        if path:
            print(f"  {path.name}  ({path.stat().st_size / 1e3:.0f} kB)", flush=True)

    # ---- one archive, so nothing is lost when the runtime goes -------------- #
    import shutil
    archive = shutil.make_archive(str(out_dir), "zip", root_dir=out_dir.parent,
                                  base_dir=out_dir.name)
    print(f"\n{'=' * 78}")
    print("EVERYTHING IS IN ONE FILE. Download it before tearing the runtime down:")
    print(f"  {archive}  ({Path(archive).stat().st_size / 1e6:.1f} MB)")
    for f in sorted(out_dir.iterdir()):
        print(f"    {f.name:34s} {f.stat().st_size / 1e6:8.2f} MB")
    print("=" * 78, flush=True)
    print("\nThe weights are not published: the expert labels are CC BY-NC-ND and the "
          "images carry OASIS, NKI and MMRR terms.")
    print("The overlay PNGs contain MRI pixels. They are for looking at, never for a "
          "repository.")


if __name__ == "__main__":
    main()
