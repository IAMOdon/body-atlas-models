# Brain · 1. Healthy: structure segmentation (MRI)

*Part of the [brain module](../README.md). Status: dataset selected, no model trained, no data downloaded.*

**What it teaches.** Names and outlines the healthy brain's structures on MRI: cortex, cerebral white matter, deep grey nuclei, hippocampus, ventricles, brainstem, cerebellum. It is the reference every later use is compared against.

**Dataset.** **Mindboggle-101** (manual cortical labels, 101 healthy brains), with the **Medical Segmentation Decathlon** hippocampus task. The SPL/NAC atlas serves as a one-subject reference for the full structure list. Full reasons, alternatives and access terms: [DATASETS.md](../DATASETS.md).

**Weights ceiling.** Set by the source MRIs of Mindboggle-101 (OASIS, NKI, MMRR terms); share-alike (CC BY-SA 4.0) for a hippocampus model.

**Stated limit.** Coverage of white matter, deep grey nuclei, ventricles, brainstem and cerebellum in the Mindboggle files is confirmed before training (see the gap noted in DATASETS.md).

For learning anatomy and pathology from labelled public cases, never to say what a
person has. `DATA.md`, `MODEL_CARD.md` and the notebook arrive when this use is built.
