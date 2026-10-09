# Brain · 2. Healthy: the cerebral vessel network

*Part of the [brain module](../README.md). Status: dataset selected and verified, data
fetched locally, no model trained.*

**What it teaches.** Where the cerebral arteries run on a TOF-MRA of a healthy adult, as
one connected network traced through the brain — the shape of the circulation before any
disease has touched it.

**Dataset.** The **IXI vessel annotations** (Bernadotte, Elfimov & Menshikov 2025),
doi:10.5281/zenodo.17393202: 100 TOF-MRA of healthy adults from the IXI cohort, with
vessel masks refined by hand under three neurovascular surgeons. Companion: the healthy
subsets of **COSTA** for scanner variety; stress test: **SMILE-UHURA** at 7 T. Full
reasons, alternatives and access terms: [DATASETS.md](../DATASETS.md#2-healthy-the-cerebral-vessel-network).

**Weights ceiling.** Share-alike. The labels are CC BY 4.0, but the IXI images they
annotate are CC BY-SA 3.0, and the stricter of the two governs. This is the first use of
the atlas whose weights could be published rather than held back — provided nothing with
heavier terms is mixed into the training set.

**The labels are binary.** Vessel or not vessel. They do not name the arteries, and
neither will this model.

**Stated limit, and it is the point of this use.** No public dataset today carries
*named* artery labels on healthy subjects. The only source of named circle-of-Willis
labels, TopCoW, was built from patients admitted to a stroke centre. So the atlas can
show the healthy vessel network and measure it, but cannot yet put a name on each artery
of a healthy brain. Naming is deferred to a separate use, which will be called what it
is: anatomy learned from patients.

For learning anatomy and pathology from labelled public cases, never to say what a
person has. `DATA.md`, `MODEL_CARD.md` and the notebook arrive when this use is built.
