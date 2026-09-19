# Brain · 1. Healthy structure segmentation · data

*How the data for this use is fetched, what it really contains, and under which terms.*

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

## Where it sits locally

```text
healthy-structure-segmentation/
  data/                                        ignored by git, refused by the guard
    zenodo-22070005/                           the eight files above, as downloaded (5.2 GB)
    extracted/                                 the unpacked archives (8.4 GB)
      Mindboggle101_release3/
        Mindboggle101_volumes/<COHORT>_volumes/<SUBJECT>/   T1 and labels, per subject
        Mindboggle101_surfaces/<COHORT>_surfaces.zip        left zipped until the 3D use
      Mindboggle101_templates/, DKT_labeling_protocol/, docs/
```

About 14 GB on disk in all, once extracted.
