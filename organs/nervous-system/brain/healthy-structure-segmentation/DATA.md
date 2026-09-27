# Brain · 1. Healthy structure segmentation · data

*How the data for this use is fetched, what it really contains, and under which terms.*

This use draws on **two Zenodo records**, and they do not carry the same licence:

| Record | What it gives | Licence |
|---|---|---|
| [22070005](#dataset) | the T1 images, the manual **cortical** labels, and FreeSurfer's automatic labels for everything else | CC BY 4.0 |
| [22071825](#the-second-record-the-subcortical-labels-a-person-drew) | the **subcortical** labels a person drew, for 20 of the 101 brains | **CC BY-NC-ND 4.0** |

> **The data is never redistributed in this repository.** Each user fetches it from the
> provider, under the provider's terms. The local folder `data/` is ignored by git and
> refused by the pre-commit guard.

## Dataset

**Mindboggle-101**, Zenodo record **doi:10.5281/zenodo.22070005** (version 3, published
2016-08-09, uploaded to Zenodo 2026-08-24). Record opened and files verified on
**19 September 2026**.

Cite: Arno Klein, Jason Tourville. *101 labeled brain images and a consistent human
cortical labeling protocol.* Frontiers in Brain Imaging Methods 6:171 (2012).
doi:10.3389/fnins.2012.00171.

## What the archive really contains

**Both the T1 MRI and the labels.** The record's own `LICENSE` file says the source MRIs
"are not included in this record"; the files say otherwise. Inside
`Mindboggle101_release3.zip`, each cohort has a `<COHORT>_volumes.tar.gz`, and each
subject folder holds:

| File | What it is |
|---|---|
| `t1weighted.nii.gz` | T1-weighted MRI, whole head, native space (the model's input) |
| `t1weighted_brain.nii.gz` | the same, skull removed |
| `t1weighted.MNI152.nii.gz`, `t1weighted_brain.MNI152.nii.gz` | the same, affine-registered to MNI152 |
| `t1weighted_brain.MNI152.affine.txt` | the affine transform to MNI152 |
| `labels.DKT31.manual.nii.gz` (+ `.MNI152`) | **cortical labels, manually edited**: 31 regions per hemisphere, DKT protocol |
| `labels.DKT31.manual+aseg.nii.gz` (+ `.MNI152`) | the manual cortical labels **plus FreeSurfer "aseg" labels for the non-cortical structures**, which are **automatic**, not manual |

**This record holds no manual labels below the cortex, for any subject.** Checked on
26 September 2026 by reading all 101 `labels.DKT31.manual.nii.gz` volumes: every one
contains only codes ≥ 1000, that is cortical codes, and nothing else. The record's own
README says as much — the subcortical labels are in a companion record "which carries a
more restrictive license". That record is [below](#the-second-record-the-subcortical-labels-a-person-drew).

So every target structure of this use has a label in the data: the cortex from manual
editing, and white matter, deep grey nuclei, hippocampus, ventricles, brainstem and
cerebellum from FreeSurfer's automatic segmentation. The notebook must treat the two
kinds differently and say so: the non-cortical labels are a machine's output, not an
expert's.

Cohorts (101 healthy adults): OASIS-TRT-20, NKI-TRT-20, NKI-RS-22, MMRR-21, and Extra-18
(HLN-12, Twins-2, MMRR-3T7T-2, Colin27, Afterthought). Surfaces (`.vtk`) come in
`<COHORT>_surfaces.zip`. The manually labelled subcortical structures of OASIS-TRT-20
are **not** in this record: they are a separate record (doi:10.5281/zenodo.22071825)
under CC BY-NC-ND 4.0, and this use does not fetch it.

## Files, sizes and checksums (from the Zenodo record)

| File | Bytes | MD5 |
|---|---:|---|
| `Mindboggle101_release3.zip` | 5,232,272,873 | `7178353814033f9f56dc97bdef2d68e4` |
| `Mindboggle101_templates.zip` | 245,621,865 | `004cf36fb3e04da8c25f3aef73c85fad` |
| `DKT_classifier_evaluation.zip` | 39,525,815 | `6449062bf5f103ed094178669ffeb4ac` |
| `Mindboggle101_atlases.zip` | 26,370,639 | `adb803397b873c5d99abcec61ba9b1de` |
| `docs.zip` | 20,140,530 | `67aed2e5ae669a920e99a144165a3c17` |
| `DKT_labeling_protocol.zip` | 206,199 | `30b13f370e10a0282250e636e6b475b5` |
| `README.md` | 7,190 | `3c0077a03eda0f6ed59323e69459805b` |
| `LICENSE` | 861 | `c57007ca73fcacb52613233c0386c8af` |
| **Total** | **5,564,145,972** (5.56 GB) | |

**Verified on 19 September 2026: all 8 files match the published size and MD5.**
The download (5,564,145,972 bytes) was checked file by file against the checksums above,
which are the ones the Zenodo record publishes.

## What was checked after extraction

All **101 subjects** (Extra-18: 18, MMRR-21: 21, NKI-RS-22: 22, NKI-TRT-20: 20,
OASIS-TRT-20: 20) have the three files a segmentation model needs: `t1weighted.nii.gz`,
`labels.DKT31.manual.nii.gz` and `labels.DKT31.manual+aseg.nii.gz`.

Example subject, `OASIS-TRT-20-1`, read from the NIfTI headers:

| File | Shape | Voxel | Type | Label values |
|---|---|---|---|---|
| `t1weighted.nii.gz` | 256 × 256 × 160 | 1.0 mm isotropic | int16 | (image) |
| `labels.DKT31.manual.nii.gz` | 256 × 256 × 160 | 1.0 mm | float32 | 62 cortical regions (1000s left, 2000s right) |
| `labels.DKT31.manual+aseg.nii.gz` | 256 × 256 × 160 | 1.0 mm | float32 | 64 cortical codes and 43 non-cortical codes |

The 43 non-cortical codes follow FreeSurfer's colour table (`FreeSurferColorLUT.txt`,
FreeSurfer repository, checked 19 September 2026). The dataset's own label table does
not name them. They include, per hemisphere where it applies: **cerebral white matter**
(2, 41), **lateral and inferior lateral ventricles** (4, 5, 43, 44), **third, fourth and
fifth ventricles** (14, 15, 72), **thalamus** (10, 49), **caudate** (11, 50), **putamen**
(12, 51), **pallidum** (13, 52), **hippocampus** (17, 53), **amygdala** (18, 54),
**accumbens** (26, 58), **ventral diencephalon** (28, 60), **brainstem** (16),
**cerebellar white matter and cortex** (7, 8, 46, 47), **corpus callosum** in five parts
(251 to 255), plus CSF, vessels, choroid plexus, optic chiasm and white-matter
hypointensities.

> **Manual and automatic labels are not the same thing.** The cortical labels were
> edited by hand following the DKT protocol. Every non-cortical label above comes from
> FreeSurfer's automatic segmentation ("aseg"). A model trained on them learns to
> reproduce FreeSurfer, not an expert. The notebook keeps the two apart when it trains
> and evaluates, and says so wherever a non-cortical structure is shown.

## How to fetch it

```sh
cd organs/nervous-system/brain/healthy-structure-segmentation
mkdir -p data/zenodo-22070005 && cd data/zenodo-22070005
for f in Mindboggle101_release3.zip Mindboggle101_templates.zip Mindboggle101_atlases.zip \
         DKT_classifier_evaluation.zip DKT_labeling_protocol.zip docs.zip README.md LICENSE; do
  curl -L --fail -C - -o "$f" "https://zenodo.org/api/records/22070005/files/$f/content"
done
md5 *            # compare with the table above (md5sum on Linux)
```

## Terms: read them before using the data

The terms are not one licence but several, and they do not all agree:

| Source | What it says |
|---|---|
| Zenodo record 22070005, `LICENSE` | CC BY 4.0 for the record |
| Original release notes (2012), in `docs/subjects/subject_sources_Mindboggle101.txt` | "Creative Commons License", linking CC BY-NC-SA 3.0 |
| Mindboggle-101 source-data record | the originating projects' terms govern the source images where they conflict |
| OASIS | non-commercial, academic research only |
| NKI | Creative Commons Attribution-NonCommercial |
| MMRR (Kirby) | BIRN data use agreement |

What this means here:

- **Using the data to learn and teach is within all of these terms.**
- **The labels** are offered under CC BY 4.0 by this record.
- **The T1 images** remain under the terms of the projects that acquired them, which are
  non-commercial or under agreement.
- **Weights trained on these images** therefore follow the project rule for
  conflicting terms: they are **held back**, read at the most restrictive statement,
  until the image owners confirm otherwise ([rule](../../../../CATALOGUE.md#two-licences-kept-apart)).
  The notebook may be published; the weights are not published under a permissive
  licence.

## The second record: the subcortical labels a person drew

**Zenodo record doi:10.5281/zenodo.22071825**, *Mindboggle-101: 20 human brain atlases
with subcortical and cortical labels*, version 3, published 2016-08-09. Record read and
files verified on **26 September 2026**. Licence **CC BY-NC-ND 4.0** — not the CC BY 4.0
of the main record.

It covers the **20 OASIS-TRT-20 subjects** only: their subcortical structures were
labelled by hand following the CMA protocol, then converted from Neuromorphometrics
BrainCOLOR numbers to FreeSurfer numbering (documented in record 22070005's own
`docs/labels/label_definitions.txt`).

### What is fetched, and what is not

| File | Bytes | MD5 | Used |
|---|---:|---|---|
| `OASIS-TRT-20_DKT31_CMA_labels_v2.zip` | 6,117,496 | `ca7652287d266a002a9ae8170611006c` | **yes**: the 20 label volumes |
| `README.md` | 3,263 | `c21ecd209b595d3306fa15ff875853b2` | yes, kept for provenance |
| `README_subcortical_labels.txt` | 903 | `e5effa6a758ad8996ce42bad4d4ec78e` | yes, kept for provenance |
| `LICENSE` | 779 | `1e332ad1e6a5a6dcccd5a2ec8b82825e` | yes, kept for provenance |
| `OASIS-TRT-20_BrainCOLOR_labels_noncortex.zip` | 1,092,892 | `b81b3dcd3e294cd3d28cabfc22d9d423` | fetched once, inspected, **set aside** — see the traps below |
| `OASIS-TRT-20_DKT31_CMA_labels_in_MNI152_v2.zip` | 134,868,870 | `ae4642d9b6dce2a09cc7545c046c6903` | no: MNI152 space is not needed here |

**Both fetched archives matched their published MD5.** 7.2 MB in all, against the 5.2 GB
of the main record.

```sh
cd organs/nervous-system/brain/healthy-structure-segmentation
mkdir -p data/zenodo-22071825 && cd data/zenodo-22071825
for f in OASIS-TRT-20_DKT31_CMA_labels_v2.zip README.md README_subcortical_labels.txt LICENSE; do
  curl -L --fail -C - -o "$f" "https://zenodo.org/api/records/22071825/files/$f/content"
done
md5 *            # compare with the table above (md5sum on Linux)
```

### Three things that make it usable at all

Checked on the 20 subjects, on disk:

1. **Same grid as the images we already have.** 20/20 subjects: the label volume's shape
   and affine are identical to `t1weighted.nii.gz` and `t1weighted_brain.nii.gz` of
   record 22070005. No registration, no resampling.
2. **The cortex is the same cortex.** Dice **1.000** between this record's cortical
   labels and release3's, with the *same code* on 100.0 % of the shared voxels (a
   handful of voxels differ per subject, e.g. 443,308 against 443,307). The record is
   from 2016 and release3 from 2019, and on these 20 brains the cortex did not change.
3. **No collision.** Not one subcortical voxel of this record falls inside release3's
   cortex.

### The 36 structures labelled by hand, present in all 20 subjects

Mean voxel count per subject in brackets, left/right where the structure is paired.

| Group | Structures (FreeSurfer codes) |
|---|---|
| Deep grey nuclei | thalamus 10/49 (8,474 / 8,211) · caudate 11/50 (3,467 / 3,546) · putamen 12/51 (4,797 / 4,606) · **pallidum 13/52 (1,571 / 1,606)** · accumbens 26/58 (570 / 524) · ventral diencephalon 28/60 (5,143 / 4,930) |
| Limbic | hippocampus 17/53 (3,599 / 3,750) · **amygdala 18/54 (987 / 1,000)** · basal forebrain 91/92 (401 / 465) |
| Ventricles and CSF | lateral 4/43 · inferior horn 5/44 (324 / 371) · third 14 (642) · fourth 15 (1,891) · CSF 24 (1,009) |
| Brainstem and cerebellum | brainstem 16 (18,426) · cerebellar exterior 6/45 (≈53,540) · cerebellar white matter 7/46 (≈15,000) · **vermis 630 / 631 / 632 (4,848 / 2,169 / 2,858)** |
| Other | optic chiasm 85 (83) · vessel 30/62 (≈32) |

Plus the **fifth ventricle (72)** in **4 subjects only**, about 11 voxels each: a normal
anatomical variant, not an error.

### Three traps, and what was done about each

**The BrainCOLOR archive is not interchangeable with the CMA volumes, and is not used.**
It is on another grid (256 × 256 × 264) and carries the **original Neuromorphometrics
numbers, unconverted**. Those numbers collide with FreeSurfer's while meaning other
structures — 41, 47, 57 and 63 all appear in it with different meanings. Mixing the two
would produce labels that are silently wrong. The record's README announces 21 volumes;
the archive holds 20. The `DKT31_CMA` volumes are already converted and suffice.

**A stray label, excluded.** `OASIS-TRT-20-3` carries code **74** on 522 voxels: an
isolated block of 12 × 11 × 8, surrounded by background on all sides, which release3's
own `manual+aseg` volume calls background throughout, and which record 22070005's list
of non-cortical codes does not define. It is mapped to ignore, never to a structure.

**Cerebral white matter has no manual labels anywhere in this dataset.** Codes 2 and 41
are absent from all 20 volumes. It is the one structure that can only ever be measured
against FreeSurfer, and it is reported that way — see the model card.

### Every code accounted for

Both sources were read end to end (101 aseg volumes, 20 manual volumes) and every label
code present is either mapped to a class or ignored on purpose: **43 codes in the aseg
volumes, 38 in the manual volumes, zero unaccounted**. The structures deliberately left
out are the ones too small or too inconsistent to measure at 1 mm — CSF 24, vessel 30/62,
optic chiasm 85 (83 voxels), fifth ventricle 72, the stray 74, hypointensities 77–80, and
the basal forebrain 91/92 (≈430 voxels, and absent from aseg, so nothing could pre-train
it). They are marked *ignore*, never relabelled as background: something is there, it is
simply not taught.

### Terms, and what they change

`LICENSE` in the record, read on 26 September 2026:

| Clause | What it forbids |
|---|---|
| **NonCommercial** | any commercial use of the material |
| **NoDerivatives** | distributing the material in modified form |

Learning from it and measuring against it are within these terms; **the data is not
redistributed here** in any form, modified or not. What this record changes is the
conclusion on the weights, and it changes it in one direction only: the weights were
already held back because of the OASIS, NKI and MMRR terms on the images, and this record
makes that **stricter, not looser**. Under the project rule, read at the most restrictive
statement ([rule](../../../../CATALOGUE.md#two-licences-kept-apart)), weights trained with
these labels are **not published**.

## Where it sits locally

```text
healthy-structure-segmentation/
  data/                                        ignored by git, refused by the guard
    zenodo-22070005/                           the eight files above, as downloaded (5.2 GB)
    zenodo-22071825/                           the expert labels, 7.2 MB, CC BY-NC-ND 4.0
    extracted-22071825/
      OASIS-TRT-20_DKT31_CMA_labels_v2/        20 volumes, one per OASIS-TRT-20 subject
    extracted/                                 the unpacked archives (8.4 GB)
      Mindboggle101_release3/
        Mindboggle101_volumes/<COHORT>_volumes/<SUBJECT>/   T1 and labels, per subject
        Mindboggle101_surfaces/<COHORT>_surfaces.zip        left zipped until the 3D use
      Mindboggle101_templates/, DKT_labeling_protocol/, docs/
```

About 14 GB on disk in all, once extracted. The training script for version 2 fetches
**only** `Mindboggle101_release3.zip` from the first record and the four small files from
the second, which is 5.24 GB rather than 5.56 GB.
