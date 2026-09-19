# Brain · 4. Pathology: segmentation

*Part of the [brain module](../README.md). Status: dataset selected, no model trained, no data downloaded.*

**What it teaches.** Outlines lesions and sets them against the healthy brain of use 1: tumour sub-regions, ischaemic stroke lesions, multiple sclerosis lesions.

**Dataset.** Tumour: **BraTS** (non-commercial model) and the **Decathlon brain tumour task** (share-alike model), trained apart. Stroke: **ISLES 2022**. MS: **MSLesSeg**, with **MS3SEG** for its normal-hyperintensity class. Full reasons, alternatives and access terms: [DATASETS.md](../DATASETS.md).

**Weights ceiling.** Tumour: non-commercial (BraTS) or share-alike (Decathlon), one model each. Stroke and MS: permissive, with attribution.

**Stated limit.** No catalogue dataset pairs lesions with healthy reference tissue directly; that comparison is built from uses 1 and 4 together.

For learning anatomy and pathology from labelled public cases, never to say what a
person has. `DATA.md`, `MODEL_CARD.md` and the notebook arrive when this use is built.
