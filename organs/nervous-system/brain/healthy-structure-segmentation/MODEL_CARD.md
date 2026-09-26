# Model card — brain, use 1: healthy structure segmentation

*A small U-Net that names eleven structures of a healthy brain on T1 MRI.*

> **For learning anatomy, never for diagnosis.** This model exists so that a student can
> see the structures of a healthy brain named on an image, beside the labels an expert
> (or a program) drew. It is not a diagnostic tool, it is not validated for clinical use,
> and nothing it produces may be used to say what a person has.

| | |
|---|---|
| **Version** | one run, 26 September 2026 |
| **Trained by** | [`colab_train.py`](colab_train.py), seed 20260926, on a Tesla T4 |
| **Data** | [Mindboggle-101](DATA.md), doi:10.5281/zenodo.22070005, eight files verified by MD5 |
| **Results of record** | [`results_t4.json`](results_t4.json) |
| **Weights** | **not published**, and not kept: see *Licence* below |

## Intended use

Teaching and learning anatomy: showing where the cortex, the deep grey nuclei, the
ventricles, the brainstem and the cerebellum are on a T1 slice, and showing the model's
output next to the dataset's own labels so that a learner can see where a model and a
reference disagree.

## Out of scope, all of it

- Any clinical use: diagnosis, triage, measurement for care, screening, or decisions
  about a person.
- Any use on an individual's own scan.
- Any claim of accuracy beyond the exact numbers below, which describe sampled axial
  slices of healthy adult brains from one dataset.
- Pathology of any kind. The model has never seen a lesion; it was trained only on
  healthy brains, and it will happily label a tumour as whatever structure it resembles.

## The model

A small U-Net: four levels, 16 channels at the top, **1,942,764 parameters**. Input is
2.5D — three adjacent axial slices, 192 × 192 at 1 mm — and the output is one of twelve
classes per pixel (eleven structures and background).

Training: 60 epochs, batch 32, AdamW at 3e-3 with three warm-up epochs then a cosine
schedule, mixed precision, loss = class-weighted cross-entropy + 0.5 × soft Dice.
Augmentation: left-right flip (safe here, since each class merges both hemispheres),
rotation ±12°, scale ±10 %, shift ±6 %, gamma 0.25, noise 0.02. Best epoch 47 of 60 by
validation Dice (0.9135); about 35 minutes of GPU.

## Data, and the provenance that matters

Mindboggle-101: 101 healthy adults from five cohorts. Split **by subject**, stratified by
cohort: 71 train, 15 validation, 15 held out (7,873 / 1,699 / 1,666 slices). No subject
appears in two splits.

**The labels do not all have the same provenance.** The cortex was labelled by hand
following the DKT protocol. Every other structure comes from FreeSurfer's automatic
segmentation (*aseg*). A score against those labels means **agreement with FreeSurfer**,
not correctness, and the model inherits FreeSurfer's mistakes wherever it makes them.

## Results

Dice on the held-out subjects, sampled axial slices. Full per-subject table in
[`results_t4.json`](results_t4.json).

| Structure | Provenance | Dice |
|---|---|---|
| cerebellum | automatic | 0.966 |
| brainstem | automatic | 0.937 |
| cerebral white matter | automatic | 0.935 |
| **cerebral cortex** | **manual (DKT)** | **0.928** |
| thalamus | automatic | 0.888 |
| hippocampus | automatic | 0.877 |
| caudate | automatic | 0.874 |
| putamen | automatic | 0.855 |
| lateral ventricle | automatic | 0.848 |
| amygdala | automatic | 0.825 |
| pallidum | automatic | 0.758 |

By provenance: manual (the cortex alone) 0.9284; automatic (ten structures) 0.8764.

![Dice per structure on fifteen held-out brains, each subject a dot, provenance shown](../../../docs/figures/png/brain/03_use1_results.png)

## Limits, in plain terms

- **One subject is far outside the rest.** `Colin27-1` averages 0.459 where the next
  worst subject averages 0.853. Colin27 is a *template*, built by averaging many scans of
  one person, so it looks like no individual brain. It is kept in the table rather than
  dropped. Without it, the cortex averages 0.966 instead of 0.928.
- **Small and deep structures are the weakest.** The pallidum is last at 0.758, and one
  subject scores 0.390 on it while scoring above 0.85 nearly everywhere else.
- **Dice is computed on sampled axial slices**, not whole volumes, so these numbers are
  not comparable with volume-level benchmarks.
- **One dataset, five cohorts, healthy adults.** Nothing here says how the model behaves
  on children, on other scanners or sequences, or on any brain that is not healthy.
- **The validation curve was not kept** beyond three points (0.43 at epoch 1, a plateau
  near 0.91, best 0.9135 at epoch 47): the per-epoch history stayed on the runtime.

## Licence of the weights

**Held back, and the weights were not kept.** Mindboggle-101's record is CC BY 4.0, but
the T1 images carry the terms of the projects that acquired them — OASIS and NKI
(non-commercial) and MMRR (a data use agreement) — and the record's own note says those
terms govern. Under the project rule for conflicting terms, read at the most restrictive
statement, weights trained on these images are not published until the image owners
confirm otherwise. See [`DATA.md`](DATA.md) and the
[licence rule](../../../../CATALOGUE.md#two-licences-kept-apart).

The notebook and the training script are part of the repository and carry its licence.

## Reproducing this run

```sh
pip install nibabel torch
python colab_train.py          # seed and configuration are in the script
```

It fetches the data itself, checks all eight MD5 sums against the record before starting,
and writes `weights_best.pt`, `metrics.json` and `curves.png`. A GPU is expected; on a
Tesla T4 the run takes about 35 minutes, plus the download.

The notebook in this folder is a demonstrator, not this model: it trains about 30,000
parameters on 15 subjects in a minute of CPU, to show the pipeline end to end.
