# Brain: the dataset chosen for each use

*Nervous system · brain. One table per use, in the order the module is built.*

> **Status: selection, 19 September 2026.** No model has been trained and no data has
> been downloaded. Every dataset below comes from the brain section of the
> [catalogue](../../../CATALOGUE.md#brain) and its [register](../../../CATALOGUE.md#dataset-register),
> checked on 17 September 2026. Identifiers, licences and weights ceilings are copied
> from the register; nothing here is new or unverified.

**How to read the tables.** *Retained* is the dataset a model for that use is built on.
*Companion* is a second dataset kept for a stated reason, usually a wider licence.
*Set aside* lists the other catalogue candidates and why they were not chosen. The
**weights ceiling** is the widest licence a model trained on that dataset can carry
([rule](../../../CATALOGUE.md#two-licences-kept-apart)); a model trained on several
datasets takes the most restrictive of them. "Not stated" means the size on disk was
not given on the provider's page when it was checked.

## 1. Healthy: structure segmentation (MRI)

Target structures: cortex, cerebral white matter, deep grey nuclei, hippocampus,
ventricles, brainstem, cerebellum.

| Role | Dataset | Why | Weights ceiling | Access | Size |
|---|---|---|---|---|---|
| **Retained** | **Mindboggle-101** · doi:10.5281/zenodo.22070005 | Manual cortical labels (DKT protocol) on 101 healthy brains from six cohorts; labels CC BY 4.0 | Depends on the source MRIs (OASIS, NKI, MMRR terms) | Open (labels); MRIs from the source projects | Not stated |
| **Companion** | **Medical Segmentation Decathlon**, Hippocampus task · medicaldecathlon.com | Expert-verified hippocampus labels, 394 MRI volumes (263 training, 131 test) | Share-alike (CC BY-SA 4.0) | Open | Not stated |
| Reference | Open Anatomy SPL/NAC brain atlas · openanatomy.org | One healthy brain, 300+ expert-labelled structures with 3D models: the full structure list in one subject, for checking and teaching, not for training at scale | Permissive, with attribution and changes marked | Open | Not stated |
| Set aside | IXI · AOMIC-ID1000 (ds003097) · NIMH Healthy Research Volunteers (ds005752) | Large healthy MRI pools (IXI nearly 600; AOMIC 928, about 97 GB) but no structure labels | IXI share-alike; AOMIC, NIMH permissive | Open | AOMIC about 97 GB |
| Set aside | HCP Young Adult | 1,113 healthy adults at 3T, no manual structure labels, and its terms carry over to derivatives | Only under the HCP Open Access Data Use Terms | Registration | Not stated |
| Set aside | OASIS-3 | Data use terms, non-commercial; labels are not manual | Not publishable without the provider's permission | DUA | Not stated |
| Set aside | OpenMind | 114k unlabelled MRI volumes: useful later for pretraining, not for structure labels | Permissive, with attribution | Open | Not stated |

**Gap, stated plainly.** The catalogue confirms manual labels for the **cortex**
(Mindboggle-101) and the **hippocampus** (Decathlon). Coverage of **white matter, deep
grey nuclei, ventricles, brainstem and cerebellum** in the Mindboggle files has not yet
been confirmed file by file, and no multi-subject dataset with manual whole-brain labels
and a clear licence is in the catalogue yet. This is checked before any training; until
then those structures are taught from the SPL/NAC reference atlas.

## 2. Healthy: the cerebral vessel network

*Binary segmentation of the cerebral arteries on TOF-MRA, on healthy subjects only.
Naming the individual arteries is a separate question, and the answer today is no: see
the end of this section.*

| Role | Dataset | Why | Weights ceiling | Access | Size |
|---|---|---|---|---|---|
| **Retained** | **IXI vessel annotations** (Bernadotte, Elfimov & Menshikov 2025) · doi:10.5281/zenodo.17393202 | 100 TOF-MRA of healthy adults from IXI with **binary** vessel masks: Frangi vesselness, then manual refinement by three annotators under three neurovascular surgeons. The only healthy, labelled, permissively licensed and directly downloadable set | **Share-alike** — the labels are CC BY 4.0, but the IXI images they annotate are CC BY-SA 3.0, and the stricter of the two governs | Open, direct | labels 6.6 MB; images from IXI |
| Companion | COSTA, healthy subsets · doi:10.5281/zenodo.11025761 | 8 centres, 4 vendors, all manually annotated. Of 423 volumes, about 267 accessible healthy ones: IXI-Guys 60, IXI-HH 60, IXI-IOP 50, ICBM 50, LocH1 25 of 27, ADAM 22 of 107. Buys scanner and vendor variety the socle lacks | Non-commercial — *"released for academic research use only"*, whatever the record's licence field says | **Restricted**, by request | not stated |
| Stress test | SMILE-UHURA · arXiv:2411.09593 | 18 annotated healthy volumes at **7 T, 300 µm isotropic** — an order of magnitude finer than the socle, and the honest way to show where a model trained at 0.47 mm stops working | No licence stated, so held back under the project rule | Synapse, by request | not stated |
| Set aside | Lausanne TOF-MRA cohort (ds003949) · doi:10.18112/openneuro.ds003949.v1.0.0 | 127 healthy controls under CC0, but **no vessel labels**: the derivatives give controls only a skull-stripped volume, and the manual masks are aneurysms, on patients | Permissive, if labels ever appear | Open | not stated |
| Set aside | CASILab / ITK-TubeTK (UNC) | About 100 healthy TOF-MRA, but the vascular models are centreline-and-radius tubes, not voxel masks, and there is no formal licence — *"may not be redistributed"*, and use outside the medical field needs written approval | No named licence, so held back | MIDAS / Kitware | not stated |
| Set aside | BraVa · 61 healthy adults | Names the six arterial trees of the circle of Willis, but distributes **reconstructions only** — SWC trees and morphometry, no images and no voxel labels. Nothing to train a segmentation model on | No licence stated | NITRC / cng.gmu.edu | not stated |

### What the retained set actually contains

Checked on the files, 9 October 2026: the archive's MD5 matches the record
(`96be3dd9d1413e8890f89721829a79f7`), it holds **100** NIfTI volumes, every one
**512 x 512 x 100**, voxel spacing 0.469 x 0.469 x 0.8 mm for 98 of them and
0.488 x 0.488 x 0.8 mm for the other two. Every volume takes **only the values 0 and 1**:
the labels are binary, there is no artery naming in them. None is empty. Vessels occupy
**0.261 % of the volume on average** (0.172 % to 0.421 %), which makes this a rarer class
than anything in use 1 except the cerebellar vermis — the sampling and the loss have to
be built for that from the start. One file is stored as float32 where the other 99 are
int16; the values are the same.

### The overlap trap, and the one case it catches

IXI subjects appear in **three** different label sets, and combining them without
checking subject identifiers would quietly put the same brain in training and in the
held-out set:

| Source | IXI subjects | Overlap with the retained 100 |
|---|---|---|
| Retained: Bernadotte 100 | IXI057 to IXI365 | — |
| TopCoW external testset `MRA_IXI_HH` | 20, all Hammersmith | **1: `IXI057`** |
| COSTA IXI-Guys, IXI-HH, IXI-IOP | 170 | unknown: the record is access-restricted, so the identifiers cannot be read without requesting it |

The TopCoW list was read from the remote archive's central directory
(IXI012, 013, 033, 034, 039, 048, 051, 052, 056, **057**, 614, 631, 632, 633, 636, 637,
638, 643, 646, 661). **`IXI057` must be excluded** from any evaluation that also uses
TopCoW labels. The COSTA identifiers have to be checked the day that access is granted,
before a single COSTA volume joins the training set.

### Naming the arteries is not possible on healthy subjects today

**TopCoW** · doi:10.5281/zenodo.15692630 is the only public source of *named* circle of
Willis labels: 13 vessel components, 125 paired CTA and MRA. But its cohort is not
healthy. The challenge paper states it plainly: *"The TopCoW challenge cohort was composed
of patients admitted to the Stroke Center of the University Hospital Zurich (USZ) in 2018
and 2019 with suspicion of stroke-related neurological conditions"* (arXiv:2312.17670v5,
section 2.1). Its external testsets do contain **40 healthy annotated cases** — 20 from
the Lausanne control group and 20 from IXI-HH — but 40 subjects is an evaluation set, not
a training set, and the labels carry TopCoW's own terms (*"Open use. Must provide the
source. Use for commercial purposes requires permission of the data owner"*) whatever the
licence of the underlying images.

So the atlas can show the vessel network on a healthy brain, and it can measure it. It
cannot yet put a name on each artery of a healthy brain. Naming is deferred to a separate
use, which will have to be called what it is: anatomy learned from patients.

## 3. Pathology: classification

### 3a. Tumour type (MRI)

| Role | Dataset | Why | Weights ceiling | Access | Size |
|---|---|---|---|---|---|
| **Retained** | **Brain Tumor Segmentation figshare (Cheng)** · doi:10.6084/m9.figshare.1512427 | 3,064 contrast-enhanced T1 slices from 233 patients: glioma 1,426, meningioma 708, pituitary 930. Tumour masks included, so a student can compare what the model looked at with the traced tumour; five-fold split indices provided | Permissive, with attribution | Open | Not stated |
| Set aside | Brain Tumor MRI Dataset (Kaggle, masoudnickparvar) | 7,200 images with a "no tumour" class, but it compiles three sources (including Cheng) whose licences are not reconciled | Undetermined: held back until confirmed | Kaggle account | Not stated |
| Set aside | BraTS | Best for segmentation (use 4), not built for slice-level type classification; non-commercial | Non-commercial (CC BY-NC) | Registration | Not stated |

The retained set has **no healthy class**. Adding healthy slices from another source
(different scanners and sequences) would let a model learn the source instead of the
tumour; any healthy class will be drawn from matched data or left out, and the choice is
documented in the model card.

### 3b. Intracranial haemorrhage, yes or no and subtype (CT)

| Role | Dataset | Why | Weights ceiling | Access | Size |
|---|---|---|---|---|---|
| **Retained** | **RSNA Intracranial Hemorrhage 2019** · kaggle.com/competitions/rsna-intracranial-hemorrhage-detection | The reference set for this task: labels for "any" haemorrhage and five subtypes (epidural, intraparenchymal, intraventricular, subarachnoid, subdural) | Non-commercial (competition rules) | Competition rules | Not stated |
| Set aside | CQ500 | 491 scans read by three radiologists: excellent labels, but far smaller; its official site no longer resolves and it adds an EULA | Non-commercial, share-alike, and the EULA | Form (archived page) | Not stated |

## 4. Pathology: segmentation

### 4a. Tumour (MRI)

| Role | Dataset | Why | Weights ceiling | Access | Size |
|---|---|---|---|---|---|
| **Retained** | **BraTS** (2023 adult glioma, current editions on Synapse) · syn51156910, syn74274097 | The reference benchmark: multi-sequence MRI, expert tumour sub-region labels; about 4,500 cases across the 2023 tasks | Non-commercial (CC BY-NC) | Registration | Not stated |
| **Companion** | **Medical Segmentation Decathlon**, Brain Tumours task | 750 volumes (484 training) taken from BraTS 2016/2017, under a wider licence: the route to a share-alike tumour model | Share-alike (CC BY-SA 4.0) | Open | Not stated |

Two models, two licences: one trained on BraTS (non-commercial), one on the Decathlon
task (share-alike). Neither mixes the two, since a mixed model would fall to the
narrower licence.

### 4b. Stroke (MRI)

| Role | Dataset | Why | Weights ceiling | Access | Size |
|---|---|---|---|---|---|
| **Retained** | **ISLES 2022** · doi:10.5281/zenodo.7153326 | 250 training cases, FLAIR, DWI and ADC, expert lesion masks from two centres | Permissive, with attribution | Open | Not stated |
| Set aside | ATLAS v2.0 (stroke) | 955 chronic-stroke T1 scans with manual masks, but under a data use agreement | Not publishable without the provider's permission | Request | Not stated |

### 4c. Multiple sclerosis (MRI)

| Role | Dataset | Why | Weights ceiling | Access | Size |
|---|---|---|---|---|---|
| **Retained** | **MSLesSeg** · doi:10.6084/m9.figshare.27919209 | 115 scans from 75 patients (1.5T and 3T, several timepoints), lesions validated by a neuroradiologist and an MS neurologist | Permissive, with attribution | Open | Not stated |
| **Companion** | **MS3SEG** · doi:10.6084/m9.figshare.30393475 | 100 patients labelled with three classes: ventricles, *normal* white-matter hyperintensities, and MS lesions. The normal class is what lets a student see a lesion against what is not one | Permissive, with attribution | Open | Not stated |
| Set aside | BONBID-HIE (neonatal injury) | Its licence statements conflict (CC BY-NC-ND 2.5 vs CC BY 4.0) | Undetermined: held back until confirmed | Open | Not stated |

### 4d. Lesions against the healthy brain

No catalogue dataset pairs lesions with healthy reference tissue directly. This use is
built by setting the lesion models of 4a to 4c against the healthy models of use 1 and
the healthy cohorts listed there.

## 5. 3D reconstruction (after 2D)

| Role | Dataset | Why | Weights ceiling | Access | Size |
|---|---|---|---|---|---|
| **Retained** | **MNI ICBM152 2009** · bic.mni.mcgill.ca/ServicesAtlases/ICBM152NLin2009 | Population-average healthy template with tissue probability maps: the reference space every reconstruction is compared in | Permissive, with the copyright notice | Open | Not stated |
| **Retained** | **Open Anatomy SPL/NAC brain atlas** · openanatomy.org | 300+ labelled structures with ready 3D models: the healthy 3D reference, structure by structure | Permissive, with attribution and changes marked | Open | Not stated |
| Companion | HRA 3D reference organs (brain) · lod.humanatlas.io/ref-organ | Male and female reference meshes, ontology-linked | Permissive, with attribution | Open | Not stated |
| Set aside | BigBrain | Unique 20 µm histological 3D brain, but non-commercial and share-alike | Non-commercial, share-alike (CC BY-NC-SA) | Open | Not stated |
| Set aside | MedShapeNet | Brain shapes whose licence changes with each source dataset | Depends on each source dataset | Open | Not stated |

The 3D stage reconstructs, in 3D, the structures and lesions segmented by uses 1 to 4,
and places them in the ICBM152 space against the healthy references above.
