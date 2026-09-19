# Brain

*Nervous system · brain. The first organ module of Body Atlas Models.*

> **Status: datasets selected, 19 September 2026.** No model has been trained and no data
> has been downloaded. For learning anatomy and pathology from labelled public cases,
> never to say what a person has (see the [root README](../../../README.md#learning-never-diagnosis)).

The brain is taught the way the whole atlas is: **healthy first, then disease**. Five
uses, built in this order, each in its own folder:

| # | Use | Folder | What a model adds for a learner | Dataset retained | Weights ceiling |
|---|---|---|---|---|---|
| 1 | Healthy: structure segmentation (MRI) | [`healthy-structure-segmentation/`](healthy-structure-segmentation/) | Names and outlines cortex, white matter, deep grey nuclei, hippocampus, ventricles, brainstem, cerebellum | Mindboggle-101, with the Decathlon hippocampus task | Set by the source MRIs; share-alike for the hippocampus |
| 2 | Healthy: vascular | [`healthy-vascular/`](healthy-vascular/) | Traces and names the arteries of the circle of Willis on MRA and CTA | TopCoW | Non-commercial unless the data owner permits |
| 3 | Pathology: classification | [`pathology-classification/`](pathology-classification/) | Tumour type on MRI; haemorrhage and its subtype on CT, with the expert label beside each output | Cheng figshare (tumour type); RSNA ICH 2019 (haemorrhage) | Permissive (tumour type); non-commercial (haemorrhage) |
| 4 | Pathology: segmentation | [`pathology-segmentation/`](pathology-segmentation/) | Outlines tumours, stroke lesions and MS lesions, set against the healthy brain of use 1 | BraTS and the Decathlon brain task (tumour); ISLES 2022 (stroke); MSLesSeg and MS3SEG (MS) | Non-commercial or share-alike (tumour); permissive (stroke, MS) |
| 5 | 3D reconstruction | [`reconstruction-3d/`](reconstruction-3d/) | Rebuilds structures and lesions in 3D and places them in a healthy reference space | MNI ICBM152 2009 and the Open Anatomy SPL/NAC brain atlas | Permissive |

The full selection, with the reasons, the alternatives set aside and the access terms,
is in **[DATASETS.md](DATASETS.md)**.

## One model per use, one licence per model

Each use gets its own model, and each model its own licence, set by the data it was
trained on and never wider (the [rule](../../../CATALOGUE.md#two-licences-kept-apart)).
Where the best dataset and the most open dataset differ, both are kept and trained
apart: the tumour segmentation use has a non-commercial model on BraTS and a
share-alike model on the Decathlon task.

## What each use folder will hold

```text
<use>/
  README.md        # what the use teaches, its dataset, its licence
  DATA.md          # how the data is fetched, under the provider's terms
  MODEL_CARD.md    # educational purpose, out-of-scope use, data, limits, weights licence
  notebook.ipynb   # healthy anatomy, data, training, evaluation, errors
```

Only `README.md` exists today. The rest comes use by use, in order. Data and weights are
never stored in this repository.
