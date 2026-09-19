# Brain · 3. Pathology: classification

*Part of the [brain module](../README.md). Status: dataset selected, no model trained, no data downloaded.*

**What it teaches.** Classifies labelled teaching cases, with the expert label always beside the output: tumour type on MRI (glioma, meningioma, pituitary tumour), and intracranial haemorrhage with its subtype on CT.

**Dataset.** **Cheng figshare brain tumour set** for tumour type; **RSNA Intracranial Hemorrhage 2019** for haemorrhage. Full reasons, alternatives and access terms: [DATASETS.md](../DATASETS.md).

**Weights ceiling.** Permissive, with attribution, for the tumour-type model; non-commercial (competition rules) for the haemorrhage model. They are two separate models.

**Stated limit.** The tumour set has no healthy class; mixing in healthy slices from another source would let a model learn the source rather than the tumour.

For learning anatomy and pathology from labelled public cases, never to say what a
person has. `DATA.md`, `MODEL_CARD.md` and the notebook arrive when this use is built.
