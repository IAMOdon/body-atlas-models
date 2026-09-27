# Model card — brain, use 1: healthy structure segmentation

*A small 3D specialist that names seventeen structures of a healthy brain on T1 MRI,
trained toward the labels a person drew.*

> **For learning anatomy, never for diagnosis.** This model exists so that a student can
> see the structures of a healthy brain named on an image, beside the labels an expert
> (or a program) drew, and see where the two disagree. It is not a diagnostic tool, it is
> not validated for clinical use, and nothing it produces may be used to say what a
> person has.

| | |
|---|---|
| **Version** | **2**, 27 September 2026 — a 3D model measured against expert labels |
| **Trained by** | [`colab_train_v2.py`](colab_train_v2.py), seed 20260927, on a Tesla T4 |
| **Data** | [Mindboggle-101](DATA.md): images and cortex from doi:10.5281/zenodo.22070005 (CC BY 4.0), expert subcortical labels from doi:10.5281/zenodo.22071825 (**CC BY-NC-ND 4.0**) |
| **Results of record** | [`results_v2.json`](results_v2.json) — the run's own file, with every score per structure **and per subject** |
| **Weights** | **not published**: see *Licence* below |
| **Previous version** | [version 1](#version-1-superseded) — 2D, eleven structures, measured only against FreeSurfer |

## What version 2 changes, and why it matters

Version 1 learned eleven structures from FreeSurfer's automatic segmentation (*aseg*).
It could therefore only ever be measured against a program: a high score meant "agrees
with FreeSurfer", never "correct".

Version 2 is trained in stages so that it can be measured against labels a person drew:

| Stage | Data | What it learns |
|---|---|---|
| 1. pre-training | 81 subjects, aseg labels + manual cortex. **No OASIS-TRT-20 subject.** | every structure, from the automatic labels |
| 2. fine-tuning | the 20 OASIS-TRT-20 subjects, whose subcortical structures were labelled by hand | the expert's boundaries |
| 3. the delivered model | one last fine-tuning on all twenty | the model of record for this use |

The two provenances are **never mixed for one structure**. Where the expert is silent and
aseg is not, the voxel teaches nothing at all: it is marked *ignore*, not background.

## Intended use

Teaching and learning anatomy: showing where the cortex, the deep grey nuclei, the
ventricles, the brainstem, the cerebellum and its vermis are on a T1 volume, and showing
the model's output next to the dataset's own labels so that a learner can see where a
model and a reference disagree — and what "disagree" costs in millimetres.

## Out of scope, all of it

- Any clinical use: diagnosis, triage, measurement for care, screening, or decisions
  about a person.
- Any use on an individual's own scan.
- Any claim of accuracy beyond the exact numbers below, which describe healthy adult
  brains from one dataset.
- Pathology of any kind. The model has never seen a lesion; it was trained only on
  healthy brains, and it will label a tumour as whatever structure it resembles.

## The model

A residual 3D U-Net: four downsamplings, 12 channels at the top, **3,225,966
parameters**, 18 outputs (seventeen structures and background). Input is a **96 × 96 × 96
patch at 1 mm**; a whole brain is segmented with a sliding window at 50 % overlap under a
gaussian weight.

Training: AdamW, mixed precision, cosine schedule after a short warm-up, batch 2 with
gradient accumulation 2. Loss = class-weighted cross-entropy **multiplied by a boundary
weight** `1 + 4·exp(−d/2 mm)`, plus soft Dice; both ignore the *ignore* voxels. Patches
are drawn 80 % of the time on a uniformly chosen present class, so the pallidum is
sampled as often as the cortex. Augmentation: left-right flip (safe: every class merges
both sides), rotation ±10°, scale ±10 %, shift ±5 %, gamma 0.25, noise 0.02.

Stage 1 was **pinned to 6,157 steps** rather than fitted to a clock, so the run
does not depend on how fast the GPU felt that day: 45 minutes, best
validation patch Dice 0.9059. Each fold then ran about
1,145 steps in 10 minutes, and the
delivered model 902 steps — the median the four folds selected.

**One class needs help, and gets it.** The cerebellar vermis is absent from the
pre-training labels: FreeSurfer has no vermis class and folds that tissue into the
cerebellar cortex, so stage 1 actively learns the wrong thing about it. Stage 2 therefore
draws patches centred on such a *cold-start* class **3x** more
often and weighs it **2x** more in the loss. This is not a knob found
by trial and error: without it the same protocol gave 0.804 once and **0.000** the next
time. With it, the vermis is found on every held-out brain.

## Data, and the provenance that matters

**101 healthy adults, five cohorts.** The cortex is manual (DKT protocol) for all 101.
The subcortical structures are manual for the **20 OASIS-TRT-20 subjects** (CMA protocol)
and automatic (*aseg*) for the other 81.

**Cerebral white matter has no manual labels anywhere in this dataset.** It is kept as a
class — the model needs it, and the image is mostly made of it — supervised from aseg in
both stages, marked `automatic` everywhere, and **never counted in an expert average**.

**The cerebellar vermis has no automatic counterpart.** FreeSurfer does not separate it;
it sits inside the cerebellar cortex label. So the vermis is absent from stage 1 (0 % of
the pre-training voxels) and is learned entirely in stage 2, from twelve brains.

## Results

Whole volumes, cross-validated over the 20 expert brains: four folds, each subject scored
exactly once by a model that never saw it. Means over the twenty; the per-subject values
are all in the record.

### Against the manual labels — the expert truth

| Structure | Dice, stage 1 | Dice, fine-tuned | gain | HD95 mm | ASSD mm |
|---|---:|---:|---:|---:|---:|
| cerebral cortex | 0.964 | **0.966** | +0.002 | 1.00 | 0.11 |
| putamen | 0.903 | **0.961** | +0.058 | 1.00 | 0.18 |
| brainstem | 0.890 | **0.944** | +0.054 | 1.29 | 0.44 |
| thalamus | 0.911 | **0.933** | +0.022 | 1.43 | 0.46 |
| caudate | 0.905 | **0.933** | +0.028 | 1.00 | 0.28 |
| cerebellar cortex | 0.876 | **0.927** | +0.052 | 1.58 | 0.54 |
| lateral ventricle | 0.911 | **0.921** | +0.010 | 1.02 | 0.29 |
| hippocampus | 0.882 | **0.913** | +0.031 | 1.19 | 0.33 |
| pallidum | 0.884 | **0.911** | +0.027 | 1.08 | 0.32 |
| cerebellar white matter | 0.857 | **0.897** | +0.040 | 1.46 | 0.50 |
| ventral diencephalon | 0.804 | **0.897** | +0.093 | 1.46 | 0.52 |
| amygdala | 0.827 | **0.894** | +0.066 | 1.30 | 0.33 |
| accumbens | 0.751 | **0.861** | +0.110 | 1.31 | 0.34 |
| fourth ventricle | 0.800 | **0.822** | +0.022 | 1.48 | 0.55 |
| **cerebellar vermis** | 0.000 | **0.809** | +0.809 | 2.50 | 0.90 |
| third ventricle | 0.765 | **0.804** | +0.038 | 1.04 | 0.39 |
| *mean of the 16* | *0.808* | ***0.900*** | *+0.091* | | |

The gain column is the difference of the two columns beside it, so every row can be
checked by eye.

Fine-tuning on expert labels improved **every one of the sixteen structures**. Without
the vermis, which starts at zero by construction, the mean goes 0.862 → 0.906.

### Against aseg — "agrees with FreeSurfer", not "correct"

Never averaged with the table above.

| Structure | before | after | | Structure | before | after |
|---|---:|---:|---|---|---:|---:|
| cerebral cortex | 0.963 | 0.965 || hippocampus | 0.896 | 0.872 |
| cerebral white matter *(automatic only)* | 0.960 | 0.959 || pallidum | 0.853 | 0.861 |
| brainstem | 0.958 | 0.911 || amygdala | 0.861 | 0.832 |
| caudate | 0.915 | 0.904 || fourth ventricle | 0.871 | 0.823 |
| lateral ventricle | 0.910 | 0.890 || ventral diencephalon | 0.869 | 0.764 |
| thalamus | 0.921 | 0.881 || accumbens | 0.761 | 0.741 |
| putamen | 0.897 | 0.881 || third ventricle | 0.749 | 0.712 |
| cerebellar white matter | 0.920 | 0.878 || cerebellar vermis | — | 0.000 |
| cerebellar cortex | 0.963 | 0.873 || | |  |
| *mean of the 15 comparable* | *0.887* | *0.853* | | | | |

### The two readings that matter

**Learning the expert means leaving FreeSurfer.** Of the fifteen structures scored against
both references, **thirteen move away** from aseg as they move toward the expert — the
ventral diencephalon by 0.100, the cerebellar cortex by 0.092. Only the cortex and the
pallidum agree a little better with both. (The vermis has no FreeSurfer counterpart to
move away from, and cerebral white matter has no expert score; neither can be counted
here.) That is not a regression. Where a program and a person draw a
boundary differently, a model cannot agree with both, and this one was asked to follow the
person. The aseg column is kept precisely so that this trade is visible instead of hidden.

**The millimetres say what Dice hides.** The structures with the lowest Dice are the small
ones, where a one-voxel error costs a great deal of overlap: eroding the truth by a single
voxel already drops the pallidum to Dice 0.738. Yet **every average surface distance in
the table is under one voxel**, and the worst 95th-percentile Hausdorff distance in the
whole model is 2.57 mm, on the vermis. The accumbens sits at Dice 0.856 with its boundary
0.35 mm out on average. Read both columns, always.

**The vermis is the clearest result of the run, and the most fragile to obtain.** A
structure FreeSurfer cannot isolate at all, absent from every pre-training label, learned
from twelve brains in a few minutes, and placed with its boundary 0.90 mm out on average.

What matters is not its mean but its spread: **0.769 to 0.848 across the twenty
held-out brains, standard deviation 0.021, and a
vermis found on 20 of 20**. An earlier run of the same protocol without the cold-start help
scored 0.000 on every one of them — the model simply never proposed a vermis. The boost is
what turns a coin toss into a result.

It stays the weakest structure by HD95 (2.50 mm), as expected for a class learned from
scratch against what stage 1 taught, and it is **over-segmented by about 18 %** (233,188
voxels predicted against 197,499 in the truth, on almost every subject). That is the price
of doubling its weight in the loss, and it is why its boundary distance matters more than
its overlap.

## How to quote this model, exactly

The twenty expert numbers above come from **four models**, one per fold, each scoring the
five brains it never saw. The **delivered model is fine-tuned on all twenty**, so no brain
is held out from it: **its performance is estimated by this 4-fold cross-validation, not
measured on a held-out set.** That is the honest formulation, and it is the one to use.

The run also measured what the delivered model scores on its own twenty training brains.
That is a **fit, not a performance**, and it must never be quoted as a result.

## What this record holds

[`results_v2.json`](results_v2.json) is the file the run itself wrote, not a summary of
it. Besides the tables above it carries, for **each of the twenty held-out brains and each
structure**: Dice, HD95, ASSD, the plain Hausdorff distance, and the voxel counts of both
the truth and the prediction — which is how the vermis over-segmentation above is
measured rather than guessed. It also records the subject names of every split, the four
folds, the step counts, the environment, the checksums of both Zenodo records, and the
sha256 of the script that produced it.

It also holds what the delivered model scores on its own twenty training brains, under
`stage3.fit_on_its_own_subjects`. That is a **fit, not a performance**, it is labelled as
such in the file, and it must never be quoted as a result.

## Limits, in plain terms

- **The expert truth covers 20 brains of one cohort.** All from OASIS-TRT. Nothing here
  says how the model behaves on other scanners, other sequences, children, or any brain
  that is not healthy.
- **Cerebral white matter is never verified by a person.** Its 0.961 means "agrees with
  FreeSurfer".
- **Small structures stay the hardest.** The third ventricle (0.024 % of voxels),
  accumbens (0.032 %) and pallidum (0.087 %) are the rarest classes in the data, and the
  lowest scores are theirs.
- **The vermis rests on twelve training brains**, had to overcome what stage 1 taught it,
  and needs the cold-start boost to be learned at all. It is over-segmented by ~18 %: read
  its ASSD (0.90 mm), not its Dice.
- **The input is a skull-stripped T1** (`t1weighted_brain.nii.gz`), so using the model
  requires brain extraction first.
- **Version 1's numbers are not comparable**: 2D sampled slices against aseg, versus whole
  volumes against expert labels.
- **The basal forebrain, optic chiasm, CSF, vessels and fifth ventricle are labelled in
  the data but not modelled** — too small or too inconsistent to measure at 1 mm. Their
  voxels teach nothing rather than being called background.

## Licence of the weights

**Held back.** Two reasons, and the second is stricter than the first:

1. The T1 images carry the terms of the projects that acquired them — OASIS and NKI
   (non-commercial) and MMRR (a data use agreement).
2. The expert subcortical labels are **CC BY-NC-ND 4.0**: no commercial use, and no
   distribution of modified material.

Under the project rule for conflicting terms, read at the most restrictive statement, the
weights are not published until the owners confirm otherwise. See [`DATA.md`](DATA.md) and
the [licence rule](../../../../CATALOGUE.md#two-licences-kept-apart). The notebook and the
training script are part of the repository and carry its licence.

## Reproducing this run

```sh
pip install nibabel torch scipy
python colab_train_v2.py          # seed and configuration are in the script
```

It fetches both records itself, checks every MD5 against them before starting, and writes
`weights_pretrain.pt`, `weights_final.pt` and `results_v2.json`. A GPU is expected. The
script measures its own speed and fits the budget, so the step counts adapt to the
hardware; on a Tesla T4 the whole run — both stages, four folds and the delivered model —
took about two hours plus the download.

```sh
python colab_train_v2.py --inventory     # every label code in the data, and its fate
python colab_train_v2.py --smoke         # a few minutes on a CPU, to check the pipeline
```

## Version 1, superseded

Kept for the record; its results are in [`results_t4.json`](results_t4.json).

| | Version 1 | Version 2 |
|---|---|---|
| geometry | 2.5D, three axial slices, sampled | 3D patches, whole volumes |
| parameters | 1,942,764 | 3,225,966 |
| structures | 11 | 17 |
| subcortical truth | FreeSurfer *aseg* only | manual (CMA) for 20 brains |
| boundary metrics | none | HD95 and ASSD in mm |
| headline | cortex 0.928 against aseg-era labels | cortex 0.969 against manual labels |

Version 1 also carried a lesson worth keeping: `Colin27-1`, a *template* built by
averaging many scans of one person, scored 0.459 where the next worst subject scored
0.853. It is in version 2's pre-training pool, not in the expert evaluation.
