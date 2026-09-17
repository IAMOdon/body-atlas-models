# Catalogue

*The index of Body Atlas Models, in the order anatomy is taught.*

> **Status: index, 17 September 2026.** Every dataset listed here was checked on that
> date against its provider's page, API or reference paper; entries marked **P** in the
> register name what could not be read. Nothing has been downloaded, and no model has
> been trained.

## How to read this index

The atlas runs **system → organ → structure**. Within each organ:

1. **Normal and anatomy** comes first: the structures, the imaging modalities, and the public
   datasets that show healthy anatomy or label its structures.
2. **Pathological** follows, by condition family: congenital, inflammatory and
   infectious, vascular, degenerative, traumatic, neoplastic. A family with no
   verified public dataset is kept and marked *no verified dataset*: the atlas
   describes what matters, not only what has data.
3. **AI** lists what a model can add at each level: *structure*, *organ*,
   *normal vs pathological*, *across cases*.

Datasets appear by name, alphabetically, and point to the [register](#dataset-register)
at the end, which gives the identifier, licence, access terms and verification status
of each. **Listing is not a recommendation or a ranking.** Licences differ widely, and
trained weights can never be more permissive than their data.

![The body, as it is taught: twelve chapters and forty organs, with the public data found for each](docs/figures/png/01_atlas_map.png)

![Healthy first, then disease: the order followed through every organ, and what a model adds at each step](docs/figures/png/02_learning_path.png)

## Contents

0. [Foundations](#0-foundations)
1. [Nervous system](#1-nervous-system)
2. [Special senses](#2-special-senses)
3. [Cardiovascular system](#3-cardiovascular-system)
4. [Respiratory system](#4-respiratory-system)
5. [Digestive system](#5-digestive-system)
6. [Urinary system](#6-urinary-system)
7. [Reproductive system](#7-reproductive-system)
8. [Endocrine system](#8-endocrine-system)
9. [Blood and lymphatic system](#9-blood-and-lymphatic-system)
10. [Musculoskeletal system](#10-musculoskeletal-system)
11. [Integumentary system](#11-integumentary-system)

[Dataset register](#dataset-register) · [Gaps](#gaps)

## 0. Foundations

Cells and basic tissues, how each modality renders healthy tissue, and whole-body reference anatomy. Every later chapter is read against this one.

### Cells and basic tissues

*Region: all.*

- **Structures:** epithelium; connective tissue; muscle tissue; nervous tissue; blood and haematopoietic cells.
- **Modalities:** light microscopy (H&E, special stains), immunohistochemistry.
- **1 · Normal and anatomy:** GTEx histology · HuBMAP + HPA Hacking the Human Body · HuBMAP Data Portal (histology) · Human Protein Atlas (tissue) · Michigan Histology · NuInsSeg.
- **2 · Pathological:**
  - Cross-organ pathology (nuclei, tumour tissue): PanNuke · TCGA slides (GDC).
- **AI:** *structure:* recognise tissue types and cell nuclei on a slide; *organ:* map a tissue to the organ it comes from; *normal vs pathological:* contrast normal and tumour tissue architecture; *across cases:* classify labelled tissue patches.

### Whole-body anatomy on CT and MRI

*Region: all.*

- **Structures:** organs, vessels, bones and muscles in their body regions; body composition layers.
- **Modalities:** CT, MRI, DXA.
- **1 · Normal and anatomy:** CT-ORG · Open Anatomy SPL atlases · Pediatric-CT-SEG · RADCURE · SAROS · TotalSegmentator CT · TotalSegmentator MRI · UK Biobank imaging.
- **2 · Pathological:** *not applicable (reference section)*.
- **AI:** *structure:* segment and name structures across the body; *organ:* reconstruct organs in 3D from volumes; *normal vs pathological:* show where a lesion sits relative to healthy anatomy; *across cases:* retrieve teaching cases by structure.

### 3D reference anatomy

*Region: all.*

- **Structures:** healthy organs and whole bodies as 3D models; sectional anatomy.
- **Modalities:** cryosection photography, 3D meshes.
- **1 · Normal and anatomy:** BodyParts3D · HRA 3D reference organs · MedShapeNet · NIH 3D · Visible Human Project · Z-Anatomy.
- **2 · Pathological:** *not applicable (reference section)*.
- **AI:** *structure:* name parts on a 3D model; *organ:* compare a reconstructed organ with a reference shape; *normal vs pathological:* compare reference and pathological shapes; *across cases:* match a 2D slice to its place in 3D.

### Cross-system teaching benchmarks

*Region: all.*

- **Structures:** small standardised images from several organs.
- **Modalities:** several.
- **1 · Normal and anatomy:** MedMNIST v2.
- **2 · Pathological:** *not applicable (reference section)*.
- **AI:** *across cases:* classify small labelled images across modalities.

## 1. Nervous system

Central nervous system first: brain, then spinal cord.

### Brain

*Region: head.*

- **Structures:** cerebral hemispheres and lobes; cortex and white matter; basal ganglia and thalamus; hippocampus; ventricles and CSF spaces; brainstem; cerebellum; meninges; circle of Willis and cerebral arteries.
- **Modalities:** MRI, CT, CT and MR angiography, PET, histology.
- **1 · Normal and anatomy:** AOMIC-ID1000 (ds003097) · AOMIC-PIOP1 (ds002785) · BigBrain · Brain Tumor MRI Dataset (Kaggle) · Cam-CAN · HCP Young Adult · IXI · Lausanne TOF-MRA aneurysm cohort (ds003949) · Mindboggle-101 · MNI ICBM152 2009 · NIMH Healthy Research Volunteers (ds005752) · OASIS-3 · OpenMind · TopCoW.
- **2 · Pathological:**
  - Perinatal (hypoxic-ischaemic injury): BONBID-HIE.
  - Inflammatory and demyelinating (multiple sclerosis): MS3SEG · MSLesSeg.
  - Vascular (ischaemic stroke): ATLAS v2.0 (stroke) · ISLES 2022.
  - Vascular (intracranial haemorrhage): CQ500 · RSNA Intracranial Hemorrhage 2019.
  - Vascular (aneurysm): Lausanne TOF-MRA aneurysm cohort (ds003949) · RSNA Intracranial Aneurysm 2025.
  - Degenerative (dementia): OASIS-3.
  - Traumatic: *no verified dataset*.
  - Neoplastic (glioma, meningioma, metastasis): Brain Tumor MRI Dataset (Kaggle) · Brain Tumor Segmentation figshare (Cheng) · BraTS · Medical Segmentation Decathlon.
- **AI:** *structure:* segment cortex, deep nuclei, hippocampus, ventricles and named arteries; *organ:* reconstruct the brain and circle of Willis in 3D; *normal vs pathological:* segment lesions and set them against healthy brains; *across cases:* classify labelled tumour and haemorrhage cases.

### Spinal cord

*Region: back.*

- **Structures:** cervical, thoracic and lumbar cord; grey and white matter; spinal canal; nerve rootlets; vertebral levels.
- **Modalities:** MRI.
- **1 · Normal and anatomy:** spine-generic.
- **2 · Pathological:**
  - Degenerative (cord compression, myelopathy): spine-generic.
  - Inflammatory and demyelinating: *no verified dataset*.
  - Neoplastic: *no verified dataset*.
- **AI:** *structure:* segment cord, canal and rootlets; *organ:* map cord segments to vertebral levels; *normal vs pathological:* compare compressed and healthy cords.

## 2. Special senses

Eye, then ear.

### Eye

*Region: head.*

- **Structures:** retina (macula, fovea, retinal layers, retinal vessels); optic disc and cup; choroid; lens; cornea; orbit.
- **Modalities:** fundus photography, OCT, OCT angiography.
- **1 · Normal and anatomy:** DRIVE · FIVES · Kermany OCT and chest X-ray · OCT5k · OCTA-500 · REFUGE.
- **2 · Pathological:**
  - Vascular and metabolic (diabetic retinopathy, macular oedema): APTOS 2019 · BRSET · Diabetic Retinopathy Detection 2015 (EyePACS) · FIVES · IDRiD · Kermany OCT and chest X-ray · OCT5k.
  - Degenerative (age-related macular degeneration): FIVES · Kermany OCT and chest X-ray · OCT5k.
  - Optic neuropathy (glaucoma): FIVES · REFUGE.
  - Neoplastic: *no verified dataset*.
- **AI:** *structure:* segment vessels, optic disc and cup, and retinal layers; *organ:* locate fovea and disc; measure layer thickness; *normal vs pathological:* show how layers and vessels change in disease; *across cases:* classify labelled fundus and OCT cases.

### Ear

*Region: head.*

- **Structures:** external acoustic meatus; tympanic membrane; ossicles; cochlea; vestibule and semicircular canals; internal acoustic meatus.
- **Modalities:** otoscopy, CT and micro-CT, MRI.
- **1 · Normal and anatomy:** Ear imagery database · Eardrum dataset (Van Akdamar) · HaN-Seg · Human bony labyrinth · Inner ear labelled volume CT · OpenEar · OtitisMediaKPJ · OtoMatch.
- **2 · Pathological:**
  - Inflammatory and infectious (otitis media, otitis externa): Ear imagery database · Eardrum dataset (Van Akdamar) · OtitisMediaKPJ · OtoMatch.
  - Degenerative (myringosclerosis, tympanosclerosis): Ear imagery database · Eardrum dataset (Van Akdamar).
  - Cholesteatoma and otosclerosis on imaging: *no verified dataset*.
  - Neoplastic (vestibular schwannoma): Vestibular-Schwannoma-MC-RC · Vestibular-Schwannoma-SEG.
- **AI:** *structure:* recognise eardrum landmarks; segment the labyrinth; *organ:* reconstruct the temporal bone and inner ear in 3D; *normal vs pathological:* compare healthy and inflamed eardrums; *across cases:* classify labelled otoscopy cases.

## 3. Cardiovascular system

Heart, then great and pulmonary vessels, then coronary arteries.

### Heart

*Region: thorax.*

- **Structures:** atria and ventricles; myocardium; valves; pericardium; left atrial appendage.
- **Modalities:** cine MRI, CT, echocardiography; ECG as the electrical counterpart.
- **1 · Normal and anatomy:** ACDC · CAMUS · EchoNet-Dynamic · HVSMR-2.0 · Medical Segmentation Decathlon · PTB-XL · TotalSegmentator CT · UK Biobank imaging.
- **2 · Pathological:**
  - Congenital heart disease: HVSMR-2.0 · ImageCHD.
  - Ischaemic (myocardial infarction): ACDC · PTB-XL.
  - Cardiomyopathies (dilated, hypertrophic): ACDC · EchoNet-LVH · M&Ms / M&Ms-2.
  - Valvular: TMED-2.
  - Ventricular function: CAMUS · EchoNet-Dynamic · EchoNet-Pediatric · MIMIC-IV-Echo.
- **AI:** *structure:* segment chambers and myocardium; *organ:* reconstruct the heart in 3D; follow it through the cardiac cycle; *normal vs pathological:* compare pathological and normal ventricles; *across cases:* classify labelled cardiac cases.

### Aorta, great and pulmonary vessels

*Region: thorax, abdomen.*

- **Structures:** aortic root, arch and branches; thoracic and abdominal aorta; venae cavae; pulmonary arteries and veins.
- **Modalities:** CT angiography, CT, MRI.
- **1 · Normal and anatomy:** AortaSeg24 · AVT (aortic vessel trees) · HiPaS artery-vein · PARSE 2022 · TotalSegmentator CT.
- **2 · Pathological:**
  - Aortic dissection and aneurysm: AVT (aortic vessel trees) · ImageTBAD.
  - Pulmonary embolism: RSNA STR Pulmonary Embolism.
- **AI:** *structure:* segment aortic branches, zones, pulmonary arteries and veins; *organ:* reconstruct vessel trees in 3D; *normal vs pathological:* show true and false lumens against a normal aorta; *across cases:* classify labelled embolism cases.

### Coronary arteries

*Region: thorax.*

- **Structures:** left main, anterior descending, circumflex and right coronary arteries and their segments.
- **Modalities:** coronary CT angiography, invasive X-ray angiography.
- **1 · Normal and anatomy:** ARCADE · ASOCA · ImageCAS.
- **2 · Pathological:**
  - Coronary artery disease (stenosis, calcification): ARCADE · ASOCA.
- **AI:** *structure:* segment and name coronary segments; *organ:* reconstruct the coronary tree in 3D; *normal vs pathological:* compare stenosed and normal segments.

## 4. Respiratory system

From the larynx down to the alveoli.

### Larynx and upper airway

*Region: neck.*

- **Structures:** glottis; vocal folds; supraglottis and subglottis.
- **Modalities:** laryngoscopy (including high-speed videoendoscopy).
- **1 · Normal and anatomy:** BAGLS · BAGLS-RT · BAGLS-VF.
- **2 · Pathological:**
  - Voice disorders and laryngeal lesions: *no verified dataset*.
- **AI:** *structure:* segment glottis and vocal folds; *organ:* follow vocal fold motion.

### Trachea and bronchi

*Region: neck, thorax.*

- **Structures:** trachea; carina; main, lobar and segmental bronchi.
- **Modalities:** CT.
- **1 · Normal and anatomy:** ATM'22 · RadGenome-ChestCT · TotalSegmentator CT.
- **2 · Pathological:**
  - Airway disease: *no verified dataset*.
- **AI:** *structure:* segment the airway tree; *organ:* reconstruct and name bronchial generations in 3D.

### Lungs and pleura

*Region: thorax.*

- **Structures:** lobes and fissures; bronchopulmonary segments; hila; pleura; mediastinum.
- **Modalities:** chest radiograph, CT, lung ultrasound, histology.
- **1 · Normal and anatomy:** Chest X-Ray Images (Pneumonia) · CheXmask · COVID-19 Radiography Database · HuBMAP + HPA Hacking the Human Body · LUNA16 · MIMIC-CXR-JPG · NIH ChestX-ray14 · OpenPOCUS · RadGenome-ChestCT · TotalSegmentator CT · VinDr-CXR · VinDr-PCXR.
- **2 · Pathological:**
  - Congenital: *no verified dataset*.
  - Infectious (pneumonia, COVID-19): Chest X-Ray Images (Pneumonia) · COVID-19 Radiography Database · COVID-BLUES · OpenPOCUS · RSNA Pneumonia Detection 2018.
  - Pleural (pneumothorax, effusion): OpenPOCUS · SIIM-ACR Pneumothorax.
  - Neoplastic (nodules, lung cancer): Duke Lung Cancer Screening 2024 · LC25000 · LIDC-IDRI · LUNA16 · LUNA25 · Medical Segmentation Decathlon.
  - Multiple findings on radiograph and CT: BRAX · CheXlocalize · CheXpert · CT-RATE · MIMIC-CXR-JPG · MS-CXR · NIH ChestX-ray14 · PadChest · ReXGroundingCT · VinDr-CXR · VinDr-PCXR.
- **AI:** *structure:* segment lungs, lobes and heart on radiograph and CT; *organ:* reconstruct lobes and fissures in 3D; *normal vs pathological:* localise findings and set them against normal radiographs; *across cases:* classify labelled radiographs, CT and ultrasound clips.

## 5. Digestive system

Mouth to rectum, then the liver, biliary tree and pancreas.

### Oral cavity, pharynx and teeth

*Region: head, neck.*

- **Structures:** teeth (by FDI number); maxilla and mandible; inferior alveolar canal; maxillary sinus; pharynx.
- **Modalities:** panoramic radiograph, cone-beam CT, PET/CT.
- **1 · Normal and anatomy:** Children's dental panoramic radiographs · DENTEX · ToothFairy2 · Tufts Dental Database.
- **2 · Pathological:**
  - Dental (caries, periapical lesions, impaction): Children's dental panoramic radiographs · DENTEX · Tufts Dental Database.
  - Neoplastic (head and neck cancer): HECKTOR.
- **AI:** *structure:* segment and number teeth; trace the alveolar canal; *organ:* reconstruct jaws and teeth in 3D; *normal vs pathological:* compare carious and healthy teeth; *across cases:* classify labelled dental findings.

### Oesophagus and stomach

*Region: thorax, abdomen.*

- **Structures:** oesophagus; Z-line; cardia; fundus; body; antrum; pylorus; duodenum.
- **Modalities:** endoscopy, CT.
- **1 · Normal and anatomy:** AMOS · GastroVision · HyperKvasir · Kvasir · TotalSegmentator CT.
- **2 · Pathological:**
  - Inflammatory (oesophagitis, gastritis, ulcer): GastroVision · HyperKvasir · Kvasir.
  - Neoplastic: GastroVision.
- **AI:** *structure:* recognise endoscopic landmarks; *organ:* segment oesophagus and stomach on CT; *normal vs pathological:* compare inflamed and normal mucosa; *across cases:* classify labelled endoscopy frames.

### Small and large bowel

*Region: abdomen, pelvis.*

- **Structures:** duodenum, jejunum, ileum; caecum and ileocaecal valve; colon; rectum; mucosa and its histology.
- **Modalities:** capsule endoscopy, colonoscopy, CT, histology.
- **1 · Normal and anatomy:** Galar · HuBMAP + HPA Hacking the Human Body · Kvasir-Capsule · LC25000 · NCT-CRC-HE-100K · SEE-AI.
- **2 · Pathological:**
  - Inflammatory and vascular lesions of the small bowel: Galar · Kvasir-Capsule · SEE-AI.
  - Polyps: CVC-ClinicDB · HyperKvasir · Kvasir-SEG · PolypGen · REAL-Colon · SUN Colonoscopy Video Database.
  - Neoplastic (colorectal cancer): LC25000 · Medical Segmentation Decathlon · NCT-CRC-HE-100K.
- **AI:** *structure:* recognise bowel segments and landmarks; *organ:* localise a capsule frame along the tract; *normal vs pathological:* segment polyps against normal mucosa; *across cases:* classify labelled frames and tissue patches.

### Liver and biliary tree

*Region: abdomen.*

- **Structures:** liver lobes and Couinaud segments; hepatic and portal veins; gallbladder; bile ducts.
- **Modalities:** CT, MRI, ultrasound.
- **1 · Normal and anatomy:** AbdomenAtlas · Abdominal ultrasound organ dataset (MSU) · AMOS · BTCV · CHAOS · CT-ORG · FLARE 2021 · Open Anatomy SPL atlases · TotalSegmentator CT · TotalSegmentator MRI · WORD.
- **2 · Pathological:**
  - Traumatic: RATIC (RSNA Abdominal Trauma 2023).
  - Focal lesions, benign and malignant: AbdomenAtlas · AbdomenCT-1K · ATLAS (liver MRI) · HCC-TACE-Seg · LiTS · LLD-MMRI · Medical Segmentation Decathlon.
- **AI:** *structure:* segment liver, gallbladder and vessels; *organ:* parcellate Couinaud segments; reconstruct in 3D; *normal vs pathological:* segment lesions within the healthy liver; *across cases:* classify labelled liver lesion types.

### Pancreas

*Region: abdomen.*

- **Structures:** head, neck, body, tail; pancreatic duct; peripancreatic vessels.
- **Modalities:** CT, MRI.
- **1 · Normal and anatomy:** AMOS · BTCV · NIH Pancreas-CT · PANORAMA · TotalSegmentator CT · WORD.
- **2 · Pathological:**
  - Neoplastic (pancreatic cancer): Medical Segmentation Decathlon · PANORAMA · PANTHER.
- **AI:** *structure:* segment pancreas, duct and vessels; *organ:* reconstruct the pancreas and its vascular relations in 3D; *normal vs pathological:* segment tumours against normal pancreas.

## 6. Urinary system

Kidneys, ureters, bladder.

### Kidneys

*Region: abdomen.*

- **Structures:** capsule; cortex; medulla and pyramids; renal sinus and pelvis; renal vessels.
- **Modalities:** ultrasound, CT, histology.
- **1 · Normal and anatomy:** AMOS · CT Kidney normal-cyst-tumour-stone · CT-ORG · HuBMAP Hacking the Kidney · Kidney ultrasound stone-no stone · KiTS23 · Open Kidney Ultrasound · TotalSegmentator CT · TRUSTED · URI-CAD · WORD.
- **2 · Pathological:**
  - Stones and obstruction: CT Kidney normal-cyst-tumour-stone · Kidney ultrasound stone-no stone · URI-CAD.
  - Cysts: CT Kidney normal-cyst-tumour-stone · KiTS23 · URI-CAD.
  - Chronic kidney disease: Open Kidney Ultrasound.
  - Traumatic: RATIC (RSNA Abdominal Trauma 2023).
  - Neoplastic: CT Kidney normal-cyst-tumour-stone · KiTS23.
- **AI:** *structure:* segment capsule, cortex, medulla and sinus; *organ:* reconstruct kidneys in 3D from CT; *normal vs pathological:* compare lesions with healthy kidneys; *across cases:* classify labelled ultrasound and CT cases.

### Ureters

*Region: abdomen, pelvis.*

- **Structures:** ureters; ureteral orifices.
- **Modalities:** CT, cystoscopy.
- **1 · Normal and anatomy:** *no verified dataset*.
- **2 · Pathological:**
  - All conditions: *no verified dataset*.
- **AI:** *to be defined once data exists*.

### Bladder

*Region: pelvis.*

- **Structures:** detrusor wall; trigone; ureteral orifices; mucosa.
- **Modalities:** cystoscopy, CT, MRI.
- **1 · Normal and anatomy:** AMOS · CT-ORG · CystoDS · Endoscopic bladder tissue classification · WORD.
- **2 · Pathological:**
  - Inflammatory (cystitis): Endoscopic bladder tissue classification.
  - Neoplastic (bladder cancer): CystoDS · Cystoscopy videos with bladder cancer · Endoscopic bladder tissue classification · FedBCa · TCGA-BLCA.
- **AI:** *structure:* recognise cystoscopic landmarks; segment the bladder on CT; *normal vs pathological:* segment tumours against normal mucosa; *across cases:* classify labelled cystoscopy frames.

## 7. Reproductive system

Male, then female organs, the breast, then pregnancy and the fetus.

### Prostate

*Region: pelvis.*

- **Structures:** peripheral, transition and central zones; anterior fibromuscular stroma; seminal vesicles; glandular histology.
- **Modalities:** MRI, histology.
- **1 · Normal and anatomy:** HuBMAP + HPA Hacking the Human Body · Medical Segmentation Decathlon · PI-CAI · Prostate158.
- **2 · Pathological:**
  - Neoplastic (prostate cancer): PANDA · PI-CAI · Prostate158 · PROSTATEx.
- **AI:** *structure:* segment zones; *organ:* reconstruct the gland in 3D; *normal vs pathological:* segment lesions against normal zones; *across cases:* grade labelled biopsies.

### Testes

*Region: pelvis.*

- **Structures:** testis; epididymis; spermatic cord.
- **Modalities:** ultrasound.
- **1 · Normal and anatomy:** *no verified dataset*.
- **2 · Pathological:**
  - All conditions: *no verified dataset*.
- **AI:** *to be defined once data exists*.

### Uterus, cervix and ovaries

*Region: pelvis.*

- **Structures:** uterine body and cavity; endometrium; myometrium; cervix; ovaries; fallopian tubes.
- **Modalities:** MRI, transvaginal ultrasound, cervix photography.
- **1 · Normal and anatomy:** FUGC 2025 (cervix ultrasound) · UT-EndoMRI · UterUS.
- **2 · Pathological:**
  - Benign uterine (fibroids): UMD (uterine myoma MRI).
  - Endometriosis: UT-EndoMRI.
  - Ovarian tumours: MMOTU.
  - Cervical transformation zone and screening: Intel-MobileODT Cervical Screening.
- **AI:** *structure:* segment uterus, cavity and ovaries; *organ:* reconstruct the uterus in 3D; *normal vs pathological:* segment fibroids and endometriomas against normal organs; *across cases:* classify labelled ovarian tumours.

### Breast

*Region: thorax.*

- **Structures:** fibroglandular tissue; fat; ducts and lobules; nipple-areolar complex; axillary nodes.
- **Modalities:** mammography, tomosynthesis, contrast-enhanced mammography, ultrasound, MRI, histology.
- **1 · Normal and anatomy:** Breast-Cancer-Screening-DBT · BUSI · Duke-Breast-Cancer-MRI · EMBED · KAU-BCMD · VinDr-Mammo.
- **2 · Pathological:**
  - Benign and malignant lesions on mammography: CBIS-DDSM · CDD-CESM · CMMD · EMBED · KAU-BCMD · RSNA Screening Mammography 2023 · VinDr-Mammo.
  - Lesions on tomosynthesis: Breast-Cancer-Screening-DBT.
  - Lesions on ultrasound: Breast-Lesions-USG · BUSI.
  - Cancer on MRI: Duke-Breast-Cancer-MRI · MAMA-MIA.
  - Histology: BreakHis.
- **AI:** *structure:* segment breast and fibroglandular tissue; grade density; *organ:* reconstruct the breast from MRI; *normal vs pathological:* segment lesions against normal parenchyma; *across cases:* classify labelled lesions with their descriptors.

### Pregnancy and fetus

*Region: pelvis.*

- **Structures:** standard fetal planes (brain, thorax, abdomen, femur); fetal head; fetal brain tissues; maternal cervix; pubic symphysis in labour.
- **Modalities:** obstetric ultrasound, fetal MRI.
- **1 · Normal and anatomy:** ACOUSLIC-AI · African fetal ultrasound planes · FeTA · FETAL_PLANES_DB · HC18 · PSFHS.
- **2 · Pathological:**
  - Fetal anomalies: *no verified dataset*.
- **AI:** *structure:* recognise standard planes; segment head, abdomen and brain tissues; *organ:* measure biometry (head and abdominal circumference); *across cases:* classify labelled planes.

## 8. Endocrine system

Thyroid, adrenal glands, pituitary, parathyroids.

### Thyroid

*Region: neck.*

- **Structures:** lobes; isthmus; nodules; cervical relations.
- **Modalities:** ultrasound, CT.
- **1 · Normal and anatomy:** SAROS.
- **2 · Pathological:**
  - Nodules, benign and malignant: Stanford Thyroid Ultrasound Cine-clip · Thyroid nodules with pathology (figshare) · TN3K · TN5000.
- **AI:** *structure:* segment the gland on CT; *normal vs pathological:* segment nodules against normal gland; *across cases:* classify labelled nodules.

### Adrenal glands

*Region: abdomen.*

- **Structures:** cortex; medulla; limbs of the gland.
- **Modalities:** CT.
- **1 · Normal and anatomy:** ALAN (adrenal shapes) · AMOS · BTCV · TotalSegmentator CT · WORD.
- **2 · Pathological:**
  - Neoplastic (adrenocortical carcinoma): Adrenal-ACC-Ki67-Seg.
  - Abnormal gland shape: ALAN (adrenal shapes).
- **AI:** *structure:* segment adrenal glands; *organ:* reconstruct gland shape in 3D; *normal vs pathological:* compare abnormal and normal gland shapes.

### Pituitary

*Region: head.*

- **Structures:** anterior and posterior lobes; stalk; sella turcica; cavernous sinuses.
- **Modalities:** MRI, CT.
- **1 · Normal and anatomy:** HaN-Seg.
- **2 · Pathological:**
  - Neoplastic (pituitary neuroendocrine tumours): Brain Tumor MRI Dataset (Kaggle) · Brain Tumor Segmentation figshare (Cheng) · Pituitary neuroendocrine tumour MRI.
- **AI:** *structure:* segment the gland; *normal vs pathological:* segment tumour and carotid arteries; *across cases:* classify labelled tumour slices.

### Parathyroids

*Region: neck.*

- **Structures:** superior and inferior parathyroid glands.
- **Modalities:** intraoperative imaging, ultrasound.
- **1 · Normal and anatomy:** IntraPG-HSI (sample).
- **2 · Pathological:**
  - Imaging of parathyroid disease: *no verified dataset*.
- **AI:** *to be defined once data exists*.

## 9. Blood and lymphatic system

Blood cells and marrow, spleen, lymph nodes.

### Blood cells and bone marrow

*Region: all.*

- **Structures:** erythrocytes; neutrophils, eosinophils, basophils, lymphocytes, monocytes; platelets; marrow precursors.
- **Modalities:** smear microscopy.
- **1 · Normal and anatomy:** AML-Cytomorphology_LMU · BCCD · C-NMC 2019 · PBC peripheral blood cells · Raabin-WBC.
- **2 · Pathological:**
  - Infectious (malaria): NLM malaria datasets.
  - Leukaemias and haematological neoplasms: AML-Cytomorphology_LMU · BM-Cells49 · Bone Marrow Cytomorphology (MLL) · C-NMC 2019 · MLL23 · SN-AM.
- **AI:** *structure:* recognise and count cell types; *normal vs pathological:* compare blasts and normal cells; *across cases:* classify labelled single cells.

### Spleen

*Region: abdomen.*

- **Structures:** capsule; red and white pulp; hilum and splenic vessels.
- **Modalities:** CT, MRI, histology.
- **1 · Normal and anatomy:** AMOS · BTCV · CHAOS · HuBMAP + HPA Hacking the Human Body · Medical Segmentation Decathlon · TotalSegmentator CT · WORD.
- **2 · Pathological:**
  - Traumatic: RATIC (RSNA Abdominal Trauma 2023).
  - Splenomegaly and focal lesions: *no verified dataset*.
- **AI:** *structure:* segment the spleen; *organ:* reconstruct in 3D; *normal vs pathological:* compare injured and normal spleens.

### Lymph nodes

*Region: neck, thorax, abdomen, axilla.*

- **Structures:** cervical, mediastinal, abdominal and axillary node stations.
- **Modalities:** CT, ultrasound, PET/CT, histology.
- **1 · Normal and anatomy:** LymphUs.
- **2 · Pathological:**
  - Lymphadenopathy: CT Lymph Nodes · Mediastinal-Lymph-Node-SEG (LNQ2023).
  - Metastatic disease: CAMELYON16/17 · HECKTOR · LymphUs · PatchCamelyon (PCam).
- **AI:** *structure:* segment nodes by station; *normal vs pathological:* compare metastatic and benign nodes; *across cases:* classify labelled node patches.

## 10. Musculoskeletal system

Axial skeleton, then limbs, then muscles.

### Spine

*Region: back.*

- **Structures:** vertebrae (C1 to S); intervertebral discs; spinal canal; posterior elements; sacrum.
- **Modalities:** radiograph, CT, MRI.
- **1 · Normal and anatomy:** BUU-LSPINE · CTSpine1K · SPIDER (lumbar spine MRI) · TotalSegmentator CT · VerSe.
- **2 · Pathological:**
  - Degenerative (disc degeneration, stenosis, listhesis): BUU-LSPINE · LSS MRI AISSLab · RSNA Lumbar Spine Degenerative 2024 · SPIDER (lumbar spine MRI).
  - Traumatic (fractures): RSNA Cervical Spine Fracture 2022.
- **AI:** *structure:* segment and label vertebrae and discs; *organ:* reconstruct the spine in 3D; *normal vs pathological:* grade degeneration against healthy discs; *across cases:* classify labelled spine studies.

### Upper limb

*Region: upper limb.*

- **Structures:** clavicle; scapula; humerus; radius and ulna; carpus; metacarpals and phalanges; shoulder, elbow and wrist joints.
- **Modalities:** radiograph, CT.
- **1 · Normal and anatomy:** MURA · TotalSegmentator CT.
- **2 · Pathological:**
  - Traumatic (fractures): AIDA SR2023 (shoulder) · GRAZPEDWRI-DX · MURA · PediURF.
  - Degenerative (shoulder): AIDA SR2023 (shoulder).
- **AI:** *structure:* recognise bones and views; *normal vs pathological:* localise fractures against normal radiographs; *across cases:* classify labelled studies.

### Pelvis and lower limb

*Region: pelvis, lower limb.*

- **Structures:** hip bones; sacrum; femur; knee (bones, cartilage, menisci, ligaments); tibia and fibula; hip and knee joints.
- **Modalities:** radiograph, CT, MRI.
- **1 · Normal and anatomy:** CTPelvic1K · Knee osteoarthritis severity grading · OAI (Osteoarthritis Initiative) · OAIZIB-CM · Open Anatomy SPL atlases · SKM-TEA · TotalSegmentator CT.
- **2 · Pathological:**
  - Developmental (hip dysplasia): MTDDH (hip dysplasia).
  - Traumatic (pelvic fractures, ligament and meniscal tears): MRNet · PENGWIN.
  - Degenerative (osteoarthritis): Knee osteoarthritis severity grading · OAI (Osteoarthritis Initiative) · SKM-TEA.
- **AI:** *structure:* segment bones and cartilage; place hip landmarks; *organ:* reconstruct pelvis and knee in 3D; *normal vs pathological:* compare arthritic or fractured joints with healthy ones; *across cases:* grade labelled knee radiographs.

### Across the skeleton

*Region: all.*

- **Structures:** skeletal maturation; bone texture.
- **Modalities:** radiograph.
- **1 · Normal and anatomy:** BTXRD (bone tumours) · FracAtlas · RSNA Pediatric Bone Age 2017.
- **2 · Pathological:**
  - Traumatic (fractures): FracAtlas.
  - Neoplastic (primary bone tumours): BTXRD (bone tumours).
- **AI:** *organ:* estimate skeletal age from the hand; *normal vs pathological:* localise tumours and fractures against normal bone; *across cases:* classify labelled bone lesions.

### Skeletal muscles

*Region: all.*

- **Structures:** gluteal muscles; iliopsoas; paraspinal muscles; thigh and shoulder muscles; muscle tissue.
- **Modalities:** CT, MRI, histology.
- **1 · Normal and anatomy:** GTEx histology · SAROS · TotalSegmentator CT.
- **2 · Pathological:**
  - Myopathies and muscle injury: *no verified dataset*.
- **AI:** *structure:* segment named muscles; *organ:* measure muscle volume.

## 11. Integumentary system

Skin and its appendages.

### Skin

*Region: all.*

- **Structures:** epidermis; dermis; subcutis; hair follicles; sebaceous and sweat glands; nails; mucosal margins.
- **Modalities:** dermoscopy, clinical and total-body photography, histology.
- **1 · Normal and anatomy:** GTEx histology · HRA 3D reference organs · Human Protein Atlas (tissue) · SPIDER-Skin / HISTAI.
- **2 · Pathological:**
  - Inflammatory and infectious: Fitzpatrick 17k · PASSION · SCIN.
  - Nail conditions: BCN20000 · Onychomycosis nail photographs.
  - Neoplastic, melanocytic and keratinocytic: BCN20000 · DDI (Diverse Dermatology Images) · Derm7pt · HAM10000 · ISIC 2020 · ISIC Archive · MILK10k · MRA-MIDAS · PAD-UFES-20 · SLICE-3D (ISIC 2024).
  - Histology of skin tumours: MoNuSeg · PUMA · SPIDER-Skin / HISTAI.
- **AI:** *structure:* recognise skin layers and adnexa on histology; *normal vs pathological:* segment lesions; compare with normal skin structures; *across cases:* classify labelled lesions across skin tones.

## Dataset register

All entries consulted **17 September 2026**. Coverage: **N** healthy subjects or a
documented normal class · **A** anatomical structure labels · **P** pathology.
Status: **V** verified (official page opened, identifier resolved) · **P** partially
verified, with the missing field named. Licences are given as stated by the provider;
where two official statements disagree, both are shown. Always read the provider's
current terms before downloading.

| Dataset | Cov. | Modality | Identifier | Licence (as stated) | Access | Status | Consulted |
|---|---|---|---|---|---|---|---|
| AbdomenAtlas | A P | CT | huggingface.co/AbdomenAtlas | CC BY-NC-SA 4.0 (1.0 Mini: no redistribution) | Open (3.0 Mini) / gated (1.0 Mini) | V | 2026-09-17 |
| AbdomenCT-1K | A P | CT | github.com/JunMa11/AbdomenCT-1K | No data licence stated | Form | P: no data licence | 2026-09-17 |
| Abdominal ultrasound organ dataset (MSU) | N P | Ultrasound | scholarsjunction.msstate.edu/research-data/5 | CC BY 4.0 | Open | V | 2026-09-17 |
| ACDC | N A P | Cine MRI | creatis.insa-lyon.fr/Challenge/acdc | CC BY-NC-SA 4.0 | Open | V | 2026-09-17 |
| ACOUSLIC-AI | N A | Obstetric ultrasound sweeps | doi:10.5281/zenodo.12697994 | CC BY-NC-SA 4.0 | Open | V | 2026-09-17 |
| Adrenal-ACC-Ki67-Seg | P | CT | doi:10.7937/1FPG-VM46 | CC BY 4.0 | Open | V | 2026-09-17 |
| African fetal ultrasound planes | N A | Obstetric ultrasound | doi:10.5281/zenodo.7540448 | CC BY 4.0 | Open | V | 2026-09-17 |
| AIDA SR2023 (shoulder) | P | Radiograph | doi:10.23698/aida/sr2023 | Controlled access | Application | V | 2026-09-17 |
| ALAN (adrenal shapes) | N A P | 3D shapes from CT | github.com/HINTLab/NeAR · doi:10.1007/978-3-031-16440-8_48 | No data licence stated | Open | P: no data licence | 2026-09-17 |
| AML-Cytomorphology_LMU | N P | Blood smear microscopy | doi:10.7937/tcia.2019.36f5o9ld | CC BY 3.0 | Open | V | 2026-09-17 |
| AMOS | A | CT, MRI | doi:10.5281/zenodo.7262581 | CC BY 4.0 | Open | V | 2026-09-17 |
| AOMIC-ID1000 (ds003097) | N | MRI | doi:10.18112/openneuro.ds003097.v1.2.1 | CC0 | Open | V | 2026-09-17 |
| AOMIC-PIOP1 (ds002785) | N | MRI | openneuro.org/datasets/ds002785 | CC0 | Open | V | 2026-09-17 |
| AortaSeg24 | A | CTA | aortaseg24.grand-challenge.org | Not seen | Signed agreement | P: data licence not seen | 2026-09-17 |
| APTOS 2019 | N P | Fundus photography | kaggle.com/competitions/aptos2019-blindness-detection | Competition rules, non-commercial | Competition | V | 2026-09-17 |
| ARCADE | A P | X-ray coronary angiography | doi:10.5281/zenodo.10390295 | CC0 | Open | V | 2026-09-17 |
| ASOCA | N A P | Coronary CTA | doi:10.5255/UKDA-SN-855916 | Conflicting: CC BY 4.0 (paper) vs UK Data Service End User Licence | On request | V | 2026-09-17 |
| ATLAS (liver MRI) | A P | MRI | atlas-challenge.u-bourgogne.fr · doi:10.3390/data8050079 | CC BY-NC-SA 4.0 | Registration | V | 2026-09-17 |
| ATLAS v2.0 (stroke) | P | MRI | doi:10.3886/ICPSR36684.v4 · fcon_1000.projects.nitrc.org/indi/retro/atlas.html | Data use agreement, research only | Request | P: ICPSR page returned 403; INDI now serves R3.0 | 2026-09-17 |
| ATM'22 | A | CT | doi:10.5281/zenodo.7949571 (and batches) · atm22.grand-challenge.org | Conflicting: CC BY 4.0 (Zenodo) vs no redistribution (challenge page) | Open (Zenodo) | V | 2026-09-17 |
| AVT (aortic vessel trees) | A P | CTA | doi:10.6084/m9.figshare.14806362 | CC BY 4.0 | Open | V | 2026-09-17 |
| BAGLS | A | High-speed laryngoscopy | doi:10.5281/zenodo.3762320 | CC BY-NC-SA 4.0 | Open | V | 2026-09-17 |
| BAGLS-RT | A | High-speed laryngoscopy | doi:10.5281/zenodo.7113473 | CC BY 4.0 | Open | V | 2026-09-17 |
| BAGLS-VF | A | High-speed laryngoscopy | doi:10.5281/zenodo.19593658 | CC BY-NC-SA 4.0 | Open | V | 2026-09-17 |
| BCCD | A | Blood smear microscopy | github.com/Shenggan/BCCD_Dataset | MIT | Open | V | 2026-09-17 |
| BCN20000 | P | Dermoscopy | doi:10.6084/m9.figshare.24140028 | CC BY 4.0 | Open | V | 2026-09-17 |
| BigBrain | N | 3D histology | bigbrainproject.org · doi:10.1126/science.1235381 | CC BY-NC-SA 4.0 | Open | V | 2026-09-17 |
| BM-Cells49 | P | Bone marrow smear microscopy | doi:10.6084/m9.figshare.33238200 | CC BY 4.0 | Open | V | 2026-09-17 |
| BodyParts3D | N | 3D meshes | doi:10.18908/lsdba.nbdc00837-000 | CC BY 4.0 (licence page updated 2025-02-27; earlier CC BY-SA 2.1 JP) | Open | V | 2026-09-17 |
| BONBID-HIE | P | Diffusion MRI (neonatal) | doi:10.5281/zenodo.10602767 | Conflicting: CC BY-NC-ND 2.5 (metadata) vs CC BY 4.0 (description) | Open | V | 2026-09-17 |
| Bone Marrow Cytomorphology (MLL) | P | Bone marrow smear microscopy | doi:10.7937/TCIA.AXH3-T579 | CC BY 4.0 | Open | V | 2026-09-17 |
| Brain Tumor MRI Dataset (Kaggle) | N P | MRI | kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset | CC BY 4.0 as uploaded; upstream licences not reconciled | Kaggle account | V | 2026-09-17 |
| Brain Tumor Segmentation figshare (Cheng) | P | MRI | doi:10.6084/m9.figshare.1512427 | CC BY 4.0 | Open | V | 2026-09-17 |
| BraTS | P | MRI | Synapse syn74274097 (2026); syn51156910 (2023) | CC BY-NC | Registration | V | 2026-09-17 |
| BRAX | P | Chest radiograph | doi:10.13026/grwk-yh18 | PhysioNet credentialed licence | Credentialed | V | 2026-09-17 |
| BreakHis | P | Histology | web.inf.ufpr.br/vri/databases/breast-cancer-histopathological-database-breakhis | Conflicting: non-commercial research vs CC BY 4.0 | Open | V | 2026-09-17 |
| Breast-Cancer-Screening-DBT | N P | Tomosynthesis | doi:10.7937/E4WT-CD02 | CC BY-NC 4.0 | Open | V | 2026-09-17 |
| Breast-Lesions-USG | P | Ultrasound | doi:10.7937/9WKK-Q141 | CC BY 4.0 | Open | V | 2026-09-17 |
| BRSET | N P | Fundus photography | doi:10.13026/1pht-2b69 | PhysioNet Credentialed Health Data License 1.5.0 | Credentialed | V | 2026-09-17 |
| BTCV | A | CT | Synapse syn3193805 | Not stated | Registration | V | 2026-09-17 |
| BTXRD (bone tumours) | N P | Radiograph | doi:10.6084/m9.figshare.27865398 | CC BY 4.0 | Open | V | 2026-09-17 |
| BUSI | N P | Ultrasound | scholar.cu.edu.eg/?q=afahmy/pages/dataset · doi:10.1016/j.dib.2019.104863 | Not stated | Open | V | 2026-09-17 |
| BUU-LSPINE | A P | Radiograph | services.informatics.buu.ac.th/spine | Custom end-user licence | Open (400) / form | V | 2026-09-17 |
| C-NMC 2019 | N P | Blood smear microscopy | doi:10.7937/tcia.2019.dc64i46r | CC BY 3.0 | Open | V | 2026-09-17 |
| Cam-CAN | N | MRI, MEG | opendata.mrc-cbu.cam.ac.uk/projects/camcan | Project terms, non-commercial | Application | V | 2026-09-17 |
| CAMELYON16/17 | P | Histology (WSI) | doi:10.5524/100439 | CC0 | Open | V | 2026-09-17 |
| CAMUS | A P | Echocardiography | creatis.insa-lyon.fr/Challenge/camus | CC BY-NC-SA 4.0 | Open | V | 2026-09-17 |
| CBIS-DDSM | P | Mammography | doi:10.7937/K9/TCIA.2016.7O02S9CY | CC BY 3.0 | Open | V | 2026-09-17 |
| CDD-CESM | P | Contrast-enhanced mammography | doi:10.7937/29kw-ae92 | CC BY 4.0 | Open | V | 2026-09-17 |
| CHAOS | N A | CT, MRI | doi:10.5281/zenodo.3362844 (record 3431873) | CC BY-NC-SA 4.0 | Open | V | 2026-09-17 |
| Chest X-Ray Images (Pneumonia) | N P | Chest radiograph (paediatric) | doi:10.17632/rscbjbr9sj.2 · kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia | CC BY 4.0 | Open | V | 2026-09-17 |
| CheXlocalize | P | Chest radiograph | doi:10.71718/hap9-kn94 | Not visible | Registration | P: licence wording not visible | 2026-09-17 |
| CheXmask | A | Chest radiograph masks | doi:10.13026/3705-zg36 | CC BY 4.0 (masks); images under source terms | Open | V | 2026-09-17 |
| CheXpert | P | Chest radiograph | doi:10.71718/y7pj-4v93 | Stanford research use agreement | Registration | V | 2026-09-17 |
| Children's dental panoramic radiographs | A P | Panoramic radiograph | doi:10.6084/m9.figshare.21621705 | CC0 | Open | V | 2026-09-17 |
| CMMD | P | Mammography | doi:10.7937/tcia.eqde-4b16 | CC BY 4.0 | Open | V | 2026-09-17 |
| COVID-19 Radiography Database | N P | Chest radiograph | kaggle.com/datasets/tawsifurrahman/covid19-radiography-database | Data files © original authors | Kaggle account | V | 2026-09-17 |
| COVID-BLUES | P | Lung ultrasound | github.com/NinaWie/COVID-BLUES | CC BY-NC-ND 4.0 | Open | V | 2026-09-17 |
| CQ500 | P | CT | academictorrents.com 47e9d8aab761e75fd0a81982fa62bddf3a173831 | CC BY-NC-SA 4.0 + EULA | Form (archived) | P: official domain no longer resolves | 2026-09-17 |
| CT Kidney normal-cyst-tumour-stone | N P | CT slices | kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone | CC BY 4.0 | Kaggle account | V | 2026-09-17 |
| CT Lymph Nodes | P | CT | doi:10.7937/K9/TCIA.2015.AQIIDCNM | CC BY 3.0 | Open | V | 2026-09-17 |
| CT-ORG | A | CT | doi:10.7937/tcia.2019.tt7f4v7o | CC BY 3.0 | Open | V | 2026-09-17 |
| CT-RATE | P | CT, reports | huggingface.co/datasets/ibrahimhamamci/CT-RATE | CC BY-NC-SA 4.0 | Gated | V | 2026-09-17 |
| CTPelvic1K | A | CT | doi:10.5281/zenodo.4588403 | CC BY 4.0 (annotations); source images under their terms | Open | V | 2026-09-17 |
| CTSpine1K | A | CT | github.com/MIRACLE-Center/CTSpine1K | CC BY-NC-SA | Open | V | 2026-09-17 |
| CVC-ClinicDB | P | Colonoscopy | polyp.grand-challenge.org/CVCClinicDB | Research and education only | Unclear | P: download link has no URL | 2026-09-17 |
| CystoDS | N A P | Cystoscopy | doi:10.17605/OSF.IO/XVDHY | CC BY 4.0 | Open | V | 2026-09-17 |
| Cystoscopy videos with bladder cancer | P | Cystoscopy video | doi:10.5281/zenodo.19002839 | CC BY-SA 4.0 | Open | V | 2026-09-17 |
| DDI (Diverse Dermatology Images) | P | Clinical photos | ddi-dataset.github.io · doi:10.1126/sciadv.abq6147 | Stanford research use agreement, non-commercial, no derivatives | Registration | V | 2026-09-17 |
| DENTEX | A P | Panoramic radiograph | huggingface.co/datasets/ibrahimhamamci/DENTEX | CC BY-NC-SA 4.0 | Open | V | 2026-09-17 |
| Derm7pt | P | Clinical + dermoscopy | derm.cs.sfu.ca · doi:10.1109/JBHI.2018.2824327 | Not seen | Not seen | P: licence and download not seen | 2026-09-17 |
| Diabetic Retinopathy Detection 2015 (EyePACS) | N P | Fundus photography | kaggle.com/competitions/diabetic-retinopathy-detection | Competition rules, use limited to the competition | Competition | V | 2026-09-17 |
| DRIVE | A | Fundus photography | drive.grand-challenge.org | Not stated | Challenge registration | V | 2026-09-17 |
| Duke Lung Cancer Screening 2024 | P | Low-dose CT | doi:10.5281/zenodo.13799069 | CC BY-NC-ND 4.0 | On request | V | 2026-09-17 |
| Duke-Breast-Cancer-MRI | A P | DCE-MRI | doi:10.7937/TCIA.e3sv-re93 | CC BY-NC 4.0 | Open | V | 2026-09-17 |
| Ear imagery database | N P | Otoscopy | doi:10.6084/m9.figshare.11886630 | CC0 | Open | V | 2026-09-17 |
| Eardrum dataset (Van Akdamar) | N P | Otoscopy | kaggle.com/datasets/erdalbasaran/eardrum-dataset-otitis-media | Unknown | Kaggle account | P: licence unknown | 2026-09-17 |
| EchoNet-Dynamic | A P | Echocardiography | doi:10.71718/yqp5-y078 | Stanford research use agreement, non-commercial | Registration | V | 2026-09-17 |
| EchoNet-LVH | A P | Echocardiography | echonet.github.io/lvh | Research use agreement, non-commercial | Registration | V | 2026-09-17 |
| EchoNet-Pediatric | A P | Echocardiography | echonet.github.io/pediatric | Research use agreement, non-commercial | Registration | V | 2026-09-17 |
| EMBED | N P | Mammography | registry.opendata.aws/emory-breast-imaging-dataset-embed · doi:10.1148/ryai.220047 | Research use agreement; no public release of model weights without permission | Registration | V | 2026-09-17 |
| Endoscopic bladder tissue classification | N P | Cystoscopy | doi:10.5281/zenodo.7741476 | CC BY 4.0 | Open | V | 2026-09-17 |
| FedBCa | P | MRI | doi:10.5281/zenodo.10409145 | CC BY 4.0 | Open | V | 2026-09-17 |
| FeTA | A | Fetal MRI | Synapse syn25649159 | Research and education only (custom) | Request | P: custom licence | 2026-09-17 |
| FETAL_PLANES_DB | N A | Obstetric ultrasound | doi:10.5281/zenodo.3904280 | CC BY 4.0 | Open | V | 2026-09-17 |
| Fitzpatrick 17k | P | Clinical photos (atlases) | github.com/mattgroh/fitzpatrick17k | CC BY-NC-SA 3.0 | Open (labels) / form (images) | V | 2026-09-17 |
| FIVES | N A P | Fundus photography | doi:10.6084/m9.figshare.19688169 | CC BY 4.0 | Open | V | 2026-09-17 |
| FLARE 2021 | A | CT | zenodo.org/records/5903672 | CC BY 4.0 | Open | V | 2026-09-17 |
| FracAtlas | N P | Radiograph | doi:10.6084/m9.figshare.22363012 | CC BY 4.0 | Open | V | 2026-09-17 |
| FUGC 2025 (cervix ultrasound) | A | Transvaginal ultrasound | zenodo.org/records/14305302 | Data sharing agreement | Signed agreement | V | 2026-09-17 |
| Galar | A P | Capsule endoscopy | doi:10.25452/figshare.plus.25304616 | CC BY 4.0 | Open | V | 2026-09-17 |
| GastroVision | N A P | Endoscopy | osf.io/84e7f | CC BY 4.0 | Open | V | 2026-09-17 |
| GRAZPEDWRI-DX | P | Radiograph (paediatric) | doi:10.6084/m9.figshare.14825193 | CC BY 4.0 | Open | V | 2026-09-17 |
| GTEx histology | N | Histology (WSI) | gtexportal.org · dbGaP phs000424 | GTEx Portal data licence (attribution) | Open (bulk: requester-pays) | V | 2026-09-17 |
| HAM10000 | P | Dermoscopy | doi:10.7910/DVN/DBW86T | CC BY-NC 4.0 | Open | V | 2026-09-17 |
| HaN-Seg | A | CT, MRI | doi:10.5281/zenodo.7442914 | CC BY-NC-ND 4.0 | Open | V | 2026-09-17 |
| HC18 | N A | Obstetric ultrasound | doi:10.5281/zenodo.1327317 | CC BY 4.0 | Open | V | 2026-09-17 |
| HCC-TACE-Seg | A P | Multiphase CT | doi:10.7937/TCIA.5FNA-0924 | CC BY 4.0 | Open | V | 2026-09-17 |
| HCP Young Adult | N | MRI, MEG | humanconnectome.org/study/hcp-young-adult | HCP Open Access Data Use Terms | Registration | V | 2026-09-17 |
| HECKTOR | P | PET/CT | hecktor26.grand-challenge.org | CC BY-NC-SA | Application | V | 2026-09-17 |
| HiPaS artery-vein | A | CT, CTPA | doi:10.5281/zenodo.14879605 | MIT | Open | V | 2026-09-17 |
| HRA 3D reference organs | N | 3D meshes (GLB) | lod.humanatlas.io/ref-organ | CC BY 4.0 | Open | V | 2026-09-17 |
| HuBMAP + HPA Hacking the Human Body | N A | Histology, IHC | doi:10.5281/zenodo.7545744 | CC BY 4.0 | Open | V | 2026-09-17 |
| HuBMAP Data Portal (histology) | N | Histology, multiplexed imaging | portal.hubmapconsortium.org | Permissive, e.g. CC BY 4.0 (check per dataset) | Open | V | 2026-09-17 |
| HuBMAP Hacking the Kidney | N A | Histology (PAS WSI) | doi:10.35079/HBM925.SGXL.596 | CC BY 4.0 | Open | V | 2026-09-17 |
| Human bony labyrinth | N A | CT, micro-CT | doi:10.5281/zenodo.3355272 | CC BY 4.0 | Open | V | 2026-09-17 |
| Human Protein Atlas (tissue) | N | Immunohistochemistry | proteinatlas.org/humanproteome/tissue | CC BY 4.0 | Open | V | 2026-09-17 |
| HVSMR-2.0 | A P | 3D cardiac MRI | doi:10.6084/m9.figshare.c.7074755 | CC BY 4.0 | Open | V | 2026-09-17 |
| HyperKvasir | A P | Endoscopy (images, video) | doi:10.17605/OSF.IO/MH9SJ | CC BY 4.0 | Open | V | 2026-09-17 |
| IDRiD | A P | Fundus photography | doi:10.21227/H25W98 | Not stated | IEEE DataPort login | V | 2026-09-17 |
| ImageCAS | A | Coronary CTA | kaggle.com/datasets/xiaoweixumedicalai/imagecas | CC BY-NC 4.0 | Kaggle account | V | 2026-09-17 |
| ImageCHD | A P | CT | kaggle.com/datasets/xiaoweixumedicalai/imagechd | CC BY-NC 4.0 | Kaggle account | V | 2026-09-17 |
| ImageTBAD | A P | CTA | kaggle.com/datasets/xiaoweixumedicalai/imagetbad | CC BY-NC 4.0 | Kaggle account | V | 2026-09-17 |
| Inner ear labelled volume CT | N A | Flat-panel volume CT | doi:10.5281/zenodo.8277159 | CC BY 4.0 | Open | V | 2026-09-17 |
| Intel-MobileODT Cervical Screening | P | Cervix photographs | kaggle.com/competitions/intel-mobileodt-cervical-cancer-screening | Competition rules, use limited to the competition | Competition | P: counts not stated | 2026-09-17 |
| IntraPG-HSI (sample) | A | Intraoperative hyperspectral | doi:10.5281/zenodo.20341870 | CC BY 4.0 (sample) | Sample open; full set controlled | P: only 5 sample cases public | 2026-09-17 |
| ISIC 2020 | P | Dermoscopy | doi:10.34970/2020-ds01 | CC BY-NC 4.0 | Open | V | 2026-09-17 |
| ISIC Archive | P | Dermoscopy, clinical, total-body photography | isic-archive.com | Per image: CC BY, CC BY-NC or CC0 | Open | V | 2026-09-17 |
| ISLES 2022 | P | MRI | doi:10.5281/zenodo.7153326 | CC BY 4.0 | Open | V | 2026-09-17 |
| IXI | N | MRI, MRA, DTI | brain-development.org/ixi-dataset | CC BY-SA 3.0 | Open | V | 2026-09-17 |
| KAU-BCMD | N P | Mammography | doi:10.21227/a4cs-ax02 · kaggle asmaasaad/king-abdulaziz-university-mammogram-dataset | Conflicting: CC0 (Kaggle) vs subscription (DataPort) | Kaggle account | P: counts differ between copies | 2026-09-17 |
| Kermany OCT and chest X-ray | N P | OCT, chest radiograph | doi:10.17632/rscbjbr9sj.3 | CC BY 4.0 (description also says research use) | Open | V | 2026-09-17 |
| Kidney ultrasound stone-no stone | N P | Ultrasound | doi:10.17632/h6jc4xm4py.1 | CC BY 4.0 | Open | V | 2026-09-17 |
| KiTS23 | A P | CT | github.com/neheller/kits23 | CC BY-NC-SA | Open | V | 2026-09-17 |
| Knee osteoarthritis severity grading | N P | Knee radiograph | doi:10.17632/56rmx5bjcr.1 | CC BY 4.0 | Open | P: image count not stated | 2026-09-17 |
| Kvasir | A P | Endoscopy | datasets.simula.no/kvasir · doi:10.1145/3083187.3083212 | Research and education only | Open | P: total count not stated | 2026-09-17 |
| Kvasir-Capsule | N A P | Capsule endoscopy | osf.io/dv2ag | CC BY 4.0 | Open | V | 2026-09-17 |
| Kvasir-SEG | P | Colonoscopy | datasets.simula.no/kvasir-seg | Research and education only | Open | V | 2026-09-17 |
| Lausanne TOF-MRA aneurysm cohort (ds003949) | N P | TOF-MRA, MRI | doi:10.18112/openneuro.ds003949.v1.0.1 | CC0 | Open | V | 2026-09-17 |
| LC25000 | N P | Histology | arXiv:1912.12142 · github.com/tampapath/lung_colon_image_set | Not stated | Open | V | 2026-09-17 |
| LIDC-IDRI | P | CT | doi:10.7937/K9/TCIA.2015.LO9QL9SX | CC BY 3.0 | Open | V | 2026-09-17 |
| LiTS | A P | CT | codalab competition 17094 · doi:10.1016/j.media.2022.102680 | Not readable (also in MSD, CC BY-SA 4.0) | Registration | P: terms not readable without sign-in | 2026-09-17 |
| LLD-MMRI | P | Multiphase MRI | github.com/LMMMEng/LLD-MMRI-Dataset | CC BY-NC 4.0 | Open | V | 2026-09-17 |
| LSS MRI AISSLab | A P | MRI | doi:10.17632/rgb77xm3jf.4 | Conflicting: CC BY 4.0 vs non-commercial description | Open | V | 2026-09-17 |
| LUNA16 | A P | CT | doi:10.5281/zenodo.2595812 · doi:10.5281/zenodo.2596478 | CC BY 4.0 | Open | V | 2026-09-17 |
| LUNA25 | P | Low-dose CT | doi:10.5281/zenodo.14223624 · doi:10.5281/zenodo.14673658 | Images CC BY 4.0; annotations CC BY-NC 4.0 | Open | V | 2026-09-17 |
| LymphUs | N P | Ultrasound | kaggle aliabbasianardakani/a-multicenter-lymph-node-ultrasound-image-database · doi:10.1016/j.dib.2026.112694 | CC BY 4.0 (Kaggle); original host not checked | Open | P: original host licence not checked | 2026-09-17 |
| M&Ms / M&Ms-2 | A P | Cine MRI | ub.edu/mnms · doi:10.1109/TMI.2021.3090082 | Not readable | Not readable | P: landing pages unavailable on consultation | 2026-09-17 |
| MAMA-MIA | P | DCE-MRI | doi:10.7303/syn60868042 | CC BY-NC | Synapse account | V | 2026-09-17 |
| Mediastinal-Lymph-Node-SEG (LNQ2023) | P | CT | doi:10.7937/QVAZ-JA09 | CC BY 4.0 | Open | V | 2026-09-17 |
| Medical Segmentation Decathlon | A P | CT, MRI | medicaldecathlon.com · doi:10.1038/s41467-022-30695-9 | CC BY-SA 4.0 | Open | V | 2026-09-17 |
| MedMNIST v2 | N A P | Multi-modality, small images | doi:10.5281/zenodo.10519652 | CC BY 4.0; DermaMNIST CC BY-NC 4.0 | Open | V | 2026-09-17 |
| MedShapeNet | A | 3D meshes | doi:10.1515/bmt-2024-0396 | Varies by source dataset | Open | P: no collection-wide licence | 2026-09-17 |
| Michigan Histology | N | Micrographs, virtual slides | histology.medicine.umich.edu | Conflicting: CC BY-NC-SA 4.0 vs 3.0; AI use for commercial purposes prohibited | Open | P: image count not seen | 2026-09-17 |
| MILK10k | P | Clinical + dermoscopy pairs | doi:10.34970/648456 | CC BY-NC | Open | V | 2026-09-17 |
| MIMIC-CXR-JPG | N P | Chest radiograph | doi:10.13026/jsn5-t979 | PhysioNet Credentialed Health Data License 1.5.0 | Credentialed | V | 2026-09-17 |
| MIMIC-IV-Echo | P | Echocardiography | doi:10.13026/307c-mr50 | PhysioNet Credentialed Health Data License 1.5.0 | Credentialed | V | 2026-09-17 |
| Mindboggle-101 | N A | MRI-derived cortical labels | doi:10.5281/zenodo.22070005 | CC BY 4.0 (labels; source MRIs under their own terms) | Open | V | 2026-09-17 |
| MLL23 | P | Blood smear microscopy | doi:10.5281/zenodo.14277609 | CC BY 4.0 | Open | V | 2026-09-17 |
| MMOTU | A P | Ultrasound, CEUS | arXiv:2207.06799 · github.com/cv516Buaa/MMOTU_DS2Net | Not specified by authors | Open | P: no data licence | 2026-09-17 |
| MNI ICBM152 2009 | N | MRI template | bic.mni.mcgill.ca/ServicesAtlases/ICBM152NLin2009 | Permissive notice (copyright retained) | Open | V | 2026-09-17 |
| MoNuSeg | A | Histology (H&E) | monuseg.grand-challenge.org | CC BY-NC-SA 4.0 | Open | V | 2026-09-17 |
| MRA-MIDAS | P | Clinical photos + dermoscopy | doi:10.71718/15nz-jv40 | Not visible | Registration | P: licence and counts not visible | 2026-09-17 |
| MRNet | P | Knee MRI | stanfordmlgroup.github.io/projects/mrnet | Non-commercial research (AIMI); exact terms not read | Registration | P: licence terms not read | 2026-09-17 |
| MS-CXR | P | Chest radiograph | doi:10.13026/9g2z-jg61 | PhysioNet credentialed licence | Credentialed | V | 2026-09-17 |
| MS3SEG | A P | MRI | doi:10.6084/m9.figshare.30393475 | CC BY 4.0 (repository) | Open | V | 2026-09-17 |
| MSLesSeg | P | MRI | doi:10.6084/m9.figshare.27919209 | CC BY 4.0 (repository) | Open | V | 2026-09-17 |
| MTDDH (hip dysplasia) | A P | Pelvic radiograph (paediatric) | doi:10.57760/sciencedb.24372 | CC BY 4.0 | Open | V | 2026-09-17 |
| MURA | N P | Radiograph | doi:10.71718/cwh3-0p32 · stanfordmlgroup.github.io/competitions/mura | Non-commercial research (AIMI); exact terms not read | Registration | P: licence terms not read | 2026-09-17 |
| NCT-CRC-HE-100K | N P | Histology (H&E) | doi:10.5281/zenodo.1214456 | CC BY 4.0 | Open | V | 2026-09-17 |
| NIH 3D | N | 3D models | 3d.nih.gov | Varies by model | Open | P: per-model licences not opened | 2026-09-17 |
| NIH ChestX-ray14 | N P | Chest radiograph | nihcc.app.box.com/v/ChestXray-NIHCC · doi:10.1109/CVPR.2017.369 | Not stated on NIH pages | Open | P: no licence on NIH pages | 2026-09-17 |
| NIH Pancreas-CT | N A | CT | doi:10.7937/K9/TCIA.2016.tNB1kqBU | CC BY 3.0 | Open | V | 2026-09-17 |
| NIMH Healthy Research Volunteers (ds005752) | N | MRI, MEG | doi:10.18112/openneuro.ds005752.v2.1.0 | CC0 | Open | V | 2026-09-17 |
| NLM malaria datasets | N P | Blood smear microscopy | lhncbc.nlm.nih.gov/LHC-downloads/downloads.html | Not stated | Open | P: no licence on NLM pages | 2026-09-17 |
| NuInsSeg | N A | Histology (H&E) | doi:10.5281/zenodo.10518968 | CC BY 4.0 | Open | V | 2026-09-17 |
| OAI (Osteoarthritis Initiative) | N P | Radiograph, MRI | nda.nih.gov/oai | Registration terms (research and education) | Credentialed | P: no named licence | 2026-09-17 |
| OAIZIB-CM | N A | Knee MRI | doi:10.5281/zenodo.14934086 | CC BY-NC 4.0 | Open | V | 2026-09-17 |
| OASIS-3 | N P | MRI, PET | oasis-brains.org · medRxiv 10.1101/2019.12.13.19014902 | Data use terms, non-commercial | DUA | V | 2026-09-17 |
| OCT5k | N A P | OCT | doi:10.5522/04/22128671 | CC0 (repository) | Open | V | 2026-09-17 |
| OCTA-500 | N A P | OCT, OCT angiography | ieee-dataport.org/open-access/octa-500 | Not found | Login and application | P: licence wording not found | 2026-09-17 |
| Onychomycosis nail photographs | P | Clinical photos (nails) | doi:10.6084/m9.figshare.5398573 | CC BY 4.0 | Open | V | 2026-09-17 |
| Open Anatomy SPL atlases | N A | CT, MRI, 3D models | openanatomy.org | 3D Slicer licence, section B | Open | V | 2026-09-17 |
| Open Kidney Ultrasound | A P | Ultrasound | github.com/rsingla92/kidneyUS | CC BY-NC-SA | Registration | V | 2026-09-17 |
| OpenEar | N A | Cone-beam CT, micro-slicing, 3D | doi:10.5281/zenodo.1473724 | CC BY 4.0 | Open | V | 2026-09-17 |
| OpenMind | N | MRI, unlabelled | huggingface.co/datasets/MIC-DKFZ/OpenMind | CC BY 4.0 | Open | V | 2026-09-17 |
| OpenPOCUS | N P | Lung ultrasound | github.com/kumarandre/OpenPOCUS · doi:10.24908/pocusj.v11i01.19439 | CC BY 4.0 (article); data licence unclear | Unclear | P: image access and data licence unclear | 2026-09-17 |
| OtitisMediaKPJ | N P | Otoscopy | doi:10.6084/m9.figshare.33127385 | Conflicting: CC BY 4.0 (figshare) vs CC BY-NC-SA 4.0 (Kaggle) | Open | P: per-class counts not seen | 2026-09-17 |
| OtoMatch | N P | Otoscopy | doi:10.5281/zenodo.4558155 | CC BY 4.0 | Open | V | 2026-09-17 |
| PAD-UFES-20 | P | Smartphone clinical photos | doi:10.17632/zr7vgbcyr2.1 | CC BY 4.0 | Open | V | 2026-09-17 |
| PadChest | P | Chest radiograph | bimcv.cipf.es/bimcv-projects/padchest · doi:10.1016/j.media.2020.101797 | Research use agreement | On request | V | 2026-09-17 |
| PANDA | P | Histology (WSI) | kaggle.com/competitions/prostate-cancer-grade-assessment | CC BY-SA-NC 4.0 (as stated) | Competition | V | 2026-09-17 |
| PanNuke | A P | Histology (H&E) | arXiv:2003.10778 | CC BY-NC-SA 4.0 | Open | V | 2026-09-17 |
| PANORAMA | A P | CT | doi:10.5281/zenodo.10998331 (batches) · github.com/DIAGNijmegen/panorama_labels | CC BY-NC 4.0 | Open | V | 2026-09-17 |
| PANTHER | A P | MRI | doi:10.5281/zenodo.15192302 | CC BY-NC 4.0 | On request | V | 2026-09-17 |
| PARSE 2022 | A | CTPA | parse2022.grand-challenge.org | Not stated for the data | Open | V | 2026-09-17 |
| PASSION | P | Clinical photos | passionderm.github.io | PASSION data licence, non-commercial | On request | V | 2026-09-17 |
| PatchCamelyon (PCam) | P | Histology patches | github.com/basveeling/pcam | CC0 (README); MIT on Zenodo mirror | Open | V | 2026-09-17 |
| PBC peripheral blood cells | N | Blood smear microscopy | doi:10.17632/snkd93bnjr.1 | CC BY 4.0 | Open | V | 2026-09-17 |
| Pediatric-CT-SEG | N A | CT | doi:10.7937/TCIA.X0H0-170 | CC BY 4.0 | Open | P: structure list not seen | 2026-09-17 |
| PediURF | P | Radiograph (paediatric) | doi:10.6084/m9.figshare.29998954 | CC BY 4.0 | Open | V | 2026-09-17 |
| PENGWIN | A P | CT, synthetic radiograph | doi:10.5281/zenodo.10927452 · doi:10.5281/zenodo.10913196 | CC BY 4.0 | Open | V | 2026-09-17 |
| PI-CAI | N A P | Biparametric MRI | doi:10.5281/zenodo.6624726 | CC BY-NC 4.0 | Open | V | 2026-09-17 |
| Pituitary neuroendocrine tumour MRI | A P | MRI | doi:10.6084/m9.figshare.27894084 | CC BY 4.0 | Open | V | 2026-09-17 |
| PolypGen | N P | Colonoscopy | doi:10.7303/syn26376615 | Conflicting: CC BY (paper) vs no redistribution (Synapse) | Synapse account | V | 2026-09-17 |
| Prostate158 | A P | MRI | doi:10.5281/zenodo.6481141 | Not stated | Open | P: no licence on records | 2026-09-17 |
| PROSTATEx | P | MRI | doi:10.7937/K9TCIA.2017.MURS5CL | CC BY 3.0 | Open | V | 2026-09-17 |
| PSFHS | N A | Intrapartum ultrasound | doi:10.5281/zenodo.10969427 | CC BY 4.0 | Open | V | 2026-09-17 |
| PTB-XL | N P | ECG (signal) | doi:10.13026/kfzx-aw45 | CC BY 4.0 | Open | V | 2026-09-17 |
| PUMA | A P | Histology (H&E) | doi:10.5281/zenodo.14213079 | CC0 (v3); earlier version CC BY 4.0 | Open | V | 2026-09-17 |
| Raabin-WBC | N | Blood smear microscopy | raabindata.com · doi:10.1038/s41598-021-04426-x | No formal licence (free for commercial and non-commercial use, as stated) | Open | P: no formal licence | 2026-09-17 |
| RADCURE | A P | CT | doi:10.7937/J47W-NM11 | TCIA restricted | Signed agreement | V | 2026-09-17 |
| RadGenome-ChestCT | A | CT, reports | huggingface.co/datasets/RadGenome/RadGenome-ChestCT | CC BY 4.0 (masks); images under CT-RATE terms | Open | V | 2026-09-17 |
| RATIC (RSNA Abdominal Trauma 2023) | N A P | CT | kaggle.com/competitions/rsna-2023-abdominal-trauma-detection · doi:10.1148/ryai.240101 | Non-commercial (paper wording) | Competition | P: rules not readable without login | 2026-09-17 |
| REAL-Colon | P | Colonoscopy video | doi:10.25452/figshare.plus.22202866 | CC BY 4.0 | Open | V | 2026-09-17 |
| REFUGE | N A P | Fundus photography | doi:10.21227/tz6e-r977 | Not stated | Subscription / challenge | V | 2026-09-17 |
| ReXGroundingCT | P | CT | huggingface.co/datasets/rajpurkarlab/ReXGroundingCT | CC BY-NC-SA 4.0 | Gated | V | 2026-09-17 |
| RSNA Cervical Spine Fracture 2022 | A P | CT | kaggle.com/competitions/rsna-2022-cervical-spine-fracture-detection | Competition rules, non-commercial, no redistribution | Competition | V | 2026-09-17 |
| RSNA Intracranial Aneurysm 2025 | P | CTA, MRA | doi:10.1148/dataset.ica.2025 | Non-commercial, no redistribution | Registration | P: counts and access partly read | 2026-09-17 |
| RSNA Intracranial Hemorrhage 2019 | P | CT | kaggle.com/competitions/rsna-intracranial-hemorrhage-detection | Competition rules, non-commercial | Competition | V | 2026-09-17 |
| RSNA Lumbar Spine Degenerative 2024 | P | MRI | kaggle.com/competitions/rsna-2024-lumbar-spine-degenerative-classification | Competition rules, non-commercial, no redistribution | Competition | P: study count not stated | 2026-09-17 |
| RSNA Pediatric Bone Age 2017 | N | Hand radiograph (paediatric) | rsna.org · doi:10.1148/radiol.2018180736 | Academic research and education, non-commercial | Open | V | 2026-09-17 |
| RSNA Pneumonia Detection 2018 | P | Chest radiograph | kaggle.com/competitions/rsna-pneumonia-detection-challenge | Competition rules, attribution (commercial allowed) | Competition | V | 2026-09-17 |
| RSNA Screening Mammography 2023 | P | Mammography | kaggle.com/competitions/rsna-breast-cancer-detection | Not readable | Competition | P: counts and rules not readable | 2026-09-17 |
| RSNA STR Pulmonary Embolism | P | CTPA | kaggle.com/competitions/rsna-str-pulmonary-embolism-detection | Competition rules, non-commercial | Competition | V | 2026-09-17 |
| SAROS | A | CT | doi:10.25737/SZ96-ZG60 | Labels CC BY 4.0; source images vary | Open labels; some images restricted | V | 2026-09-17 |
| SCIN | P | Consumer photos | doi:10.5281/zenodo.10819504 | SCIN Data Use License (attribution, no re-identification) | Open | V | 2026-09-17 |
| SEE-AI | N P | Capsule endoscopy | doi:10.34740/kaggle/ds/1516536 | CC BY 4.0 | Kaggle account | V | 2026-09-17 |
| SIIM-ACR Pneumothorax | P | Chest radiograph | kaggle.com/competitions/siim-acr-pneumothorax-segmentation | Competition rules, any purpose | Competition (stage 2 only) | V | 2026-09-17 |
| SKM-TEA | A P | Knee MRI (k-space, DICOM) | doi:10.71718/2ghb-nv62 | Not stated | Registration | P: licence not stated | 2026-09-17 |
| SLICE-3D (ISIC 2024) | P | Total-body photography crops | doi:10.34970/2024-slice-3d | CC BY-NC; Permissive subset CC BY | Open | V | 2026-09-17 |
| SN-AM | P | Bone marrow aspirate microscopy | doi:10.7937/tcia.2019.of2w8lxr | CC BY 3.0 | Open | V | 2026-09-17 |
| SPIDER (lumbar spine MRI) | A P | MRI | doi:10.5281/zenodo.10159290 | CC BY 4.0 | Open | V | 2026-09-17 |
| SPIDER-Skin / HISTAI | N A P | Histology | huggingface.co/datasets/histai/SPIDER-skin | CC BY-NC 4.0 | Gated | V | 2026-09-17 |
| spine-generic | N A P | MRI | doi:10.5281/zenodo.4299140 · openneuro ds002902 | Conflicting: CC BY 4.0 vs CC0 | Open | V | 2026-09-17 |
| Stanford Thyroid Ultrasound Cine-clip | A P | Thyroid ultrasound video | doi:10.71718/7m5n-rh16 | Not readable | Registration | P: licence not readable | 2026-09-17 |
| SUN Colonoscopy Video Database | N P | Colonoscopy video | sundatabase.org | Non-commercial research and education | On request | V | 2026-09-17 |
| TCGA slides (GDC) | P | Histology (WSI), unlabelled | portal.gdc.cancer.gov | Not seen | Open | P: licence text not opened | 2026-09-17 |
| TCGA-BLCA | P | CT, MRI, PET | doi:10.7937/K9/TCIA.2016.8LNG8XDR | CC BY 3.0 | Open | P: no annotations stated | 2026-09-17 |
| Thyroid nodules with pathology (figshare) | P | Thyroid ultrasound | doi:10.6084/m9.figshare.27021604 | CC BY 4.0 | Open | P: label format not confirmed | 2026-09-17 |
| TMED-2 | P | Echocardiography | tmed.cs.tufts.edu | Not stated | On request | P: licence and terms not stated | 2026-09-17 |
| TN3K | P | Thyroid ultrasound | github.com/haifangong/TRFE-Net-for-thyroid-nodule-segmentation | Data licence not stated (code MIT) | Open | V | 2026-09-17 |
| TN5000 | P | Thyroid ultrasound | doi:10.6084/m9.figshare.28455641 | CC BY 4.0 | Open | V | 2026-09-17 |
| ToothFairy2 | A | Dental CBCT | toothfairy2.grand-challenge.org | CC BY-SA | Free sign-up | V | 2026-09-17 |
| TopCoW | N A | CTA, TOF-MRA | doi:10.5281/zenodo.15692630 | Open use with attribution; commercial use needs permission | Open | V | 2026-09-17 |
| TotalSegmentator CT | N A P | CT | doi:10.5281/zenodo.6802613 (v3.0.0: doi:10.5281/zenodo.22688904) | CC BY 4.0 | Open | V | 2026-09-17 |
| TotalSegmentator MRI | N A P | MRI | doi:10.5281/zenodo.11367004 (v3.0.0: doi:10.5281/zenodo.22688334) | CC BY 4.0 (v3.0.0); v2.0.0 was CC BY-NC-SA 2.0 | Open | V | 2026-09-17 |
| TRUSTED | A | 3D ultrasound, CT | doi:10.1038/s41597-025-04467-1 | Not seen | Signed DUA | P: data repository not opened | 2026-09-17 |
| Tufts Dental Database | A P | Panoramic radiograph | tdd.ece.tufts.edu · doi:10.1109/JBHI.2021.3117575 | Not stated | On request | V | 2026-09-17 |
| UK Biobank imaging | N P | MRI, DXA, ultrasound | ukbiobank.ac.uk | Application-based | Application | P: official access page returned 403 | 2026-09-17 |
| UMD (uterine myoma MRI) | A P | MRI | doi:10.6084/m9.figshare.23541312 | CC BY 4.0 | Open | V | 2026-09-17 |
| URI-CAD | N A P | Ultrasound | doi:10.21950/0E0CTF | CC BY-NC 4.0 | Open | V | 2026-09-17 |
| UT-EndoMRI | A P | MRI | doi:10.5281/zenodo.15750762 | Conflicting: CC BY 4.0 badge vs non-commercial description | Open | V | 2026-09-17 |
| UterUS | A | 3D transvaginal ultrasound | github.com/UL-FRI-LGM/UterUS | CC BY-NC-SA 4.0 | Open | V | 2026-09-17 |
| VerSe | A | CT | github.com/anjany/verse · doi:10.1016/j.media.2021.102166 | CC BY-SA 4.0 | Open | V | 2026-09-17 |
| Vestibular-Schwannoma-MC-RC | P | MRI | doi:10.7937/HRZH-2N82 | CC BY 4.0 | Open | V | 2026-09-17 |
| Vestibular-Schwannoma-SEG | P | MRI | doi:10.7937/TCIA.9YTJ-5Q73 | CC BY 4.0 | Open | V | 2026-09-17 |
| VinDr-CXR | N P | Chest radiograph | doi:10.13026/3akn-b287 | PhysioNet Credentialed Health Data License 1.5.0 | Credentialed | V | 2026-09-17 |
| VinDr-Mammo | N P | Mammography | doi:10.13026/br2v-7517 | PhysioNet Restricted Health Data License 1.5.0 | DUA | V | 2026-09-17 |
| VinDr-PCXR | N P | Chest radiograph (paediatric) | doi:10.13026/k8qc-na36 | PhysioNet Restricted Health Data License 1.5.0 | DUA | V | 2026-09-17 |
| Visible Human Project | N | Cryosection photographs, CT, MRI | nlm.nih.gov/research/visible · NLM data ux2j-9i9a | NLM terms and conditions (credit line) | Open | V | 2026-09-17 |
| WORD | A | CT | github.com/HiLab-git/WORD · doi:10.1016/j.media.2022.102642 | GPL-3.0; stated not for clinical or commercial use | Open | V | 2026-09-17 |
| Z-Anatomy | N | 3D meshes (Blender) | github.com/Z-Anatomy/Models-of-human-anatomy | CC BY-SA 4.0; some credited parts NC | Open | V | 2026-09-17 |

## Gaps

Places where no public dataset could be verified on 17 September 2026. They stay in the
atlas; they are where contributions matter most.

- Brain: traumatic
- Spinal cord: inflammatory and demyelinating
- Spinal cord: neoplastic
- Eye: neoplastic
- Ear: cholesteatoma and otosclerosis on imaging
- Larynx and upper airway: voice disorders and laryngeal lesions
- Trachea and bronchi: airway disease
- Lungs and pleura: congenital
- Ureters: normal
- Ureters: all conditions
- Testes: normal
- Testes: all conditions
- Pregnancy and fetus: fetal anomalies
- Parathyroids: imaging of parathyroid disease
- Spleen: splenomegaly and focal lesions
- Skeletal muscles: myopathies and muscle injury

Datasets looked for but not listed, because they could not be verified or are no longer
obtainable: DDTI (thyroid ultrasound, no live dataset page), SegRap2023 (sharing stopped
after the challenge), CANDID-PTX (not accessible outside Health New Zealand).
