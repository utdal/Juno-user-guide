# AlphaFold 3
 
## Overview
 
AlphaFold 3, developed by Google DeepMind and Isomorphic Labs, predicts the 3D structures of proteins and their interactions with DNA, RNA, ligands, and ions. It is significantly more capable than AlphaFold 2, supporting a broader range of biomolecular complexes in a single model.
 
---
 
## Before You Start
 
### Licensing and access model
 
AlphaFold 3 has two licensing layers, and the access path on Juno reflects this:
 
- **Source code** is open-source (Apache 2.0) and freely installed system-wide. No user action required.
- **Model parameters (weights)** are gated by Google DeepMind's [Model Parameters Terms of Use](https://github.com/google-deepmind/alphafold3/blob/main/WEIGHTS_TERMS_OF_USE.md) and may only be obtained directly from Google.
!!! info "UT Dallas holds institutional access"
    An authorized representative of UT Dallas has obtained the AlphaFold 3 model parameters under Google DeepMind's organizational access provision and agreed to the Terms on behalf of the institution. The weights are maintained centrally on Juno and made available to UTD researchers who meet the eligibility criteria and complete the UT Dallas user agreement.
 
    **Do not submit a personal request to Google DeepMind.** Doing so is unnecessary, may conflict with our institutional agreement, and creates governance ambiguity. Follow the UTD process below.
 
### Eligibility
 
To use AlphaFold 3 on Juno you must confirm **all** of the following:
 
- You are affiliated with UT Dallas as a faculty member, staff member, postdoc, graduate student, or approved collaborator.
- You are conducting **non-commercial research**. AlphaFold 3 must not be used on behalf of a commercial organization, including sponsored research where the sponsor is a commercial entity and would obtain rights to the outputs.
- You are not a resident of a country subject to U.S. embargo and you are not otherwise restricted by U.S. export controls.
- You will not use AlphaFold 3 or its outputs for clinical decision-making or medical advice.
- You will not use AlphaFold 3 outputs to train, fine-tune, or distill machine learning models for biomolecular structure prediction.
### Required reading
 
You must read the following documents before requesting access:
 
- [AlphaFold 3 Model Parameters Terms of Use](https://github.com/google-deepmind/alphafold3/blob/main/WEIGHTS_TERMS_OF_USE.md)
- [AlphaFold 3 Model Parameters Prohibited Use Policy](https://github.com/google-deepmind/alphafold3/blob/main/WEIGHTS_PROHIBITED_USE_POLICY.md)
- [AlphaFold 3 Output Terms of Use](https://github.com/google-deepmind/alphafold3/blob/main/OUTPUT_TERMS_OF_USE.md)
### Requesting access on Juno
 
**Step 1 — Submit the UT Dallas user agreement**
 
Complete the UT Dallas AlphaFold 3 user agreement form:
 
> 🔗 **[UT Dallas AlphaFold 3 User Agreement Form](https://forms.office.com/r/ydg8jCDL2G)**
>
> *Replace this link with the published form URL before deploying these docs.*
 
The form captures your eligibility attestation, intended use, and acknowledgment of the Google DeepMind Terms. Graduate students and postdocs must have their PI co-sign.
 
**Step 2 — Wait for approval**
 
The HPC team will review your submission. Approval typically takes **1–3 business days**. You will receive an email confirming your account has been added to the `af3_users` group.
 
**Step 3 — Activate group membership**
 
After approval, log out of Juno and log back in (or run `newgrp af3_users`) for the new group membership to take effect. Verify with:
 
```bash
id -nG | tr ' ' '\n' | grep af3_users
```
 
If the command prints `af3_users`, you are ready to run AlphaFold 3.
 
---

### GPU Requirements

AlphaFold 3 inference requires a GPU with **at least 80 GB of VRAM**. On Juno, use the `h100` partition. (The higher-VRAM `h200` partition is coming soon — see [GPU Computing on Juno](index.md).)

| Partition | GPU | VRAM | Suitable? |
|---|---|---|---|
| `h100` | NVIDIA H100 | 80–94 GB | Yes (recommended) |
| `h200` | NVIDIA H200 NVL | 141 GB | Yes — coming soon |
| `a30` | NVIDIA A30 | 24 GB | No — insufficient VRAM |

---

## How AlphaFold 3 Works

AlphaFold 3 runs in two sequential stages. You can submit these as separate SLURM jobs or combine them into a single script.

```
  Stage 1: Data Pipeline (CPU)          Stage 2: Inference (GPU)
  ┌─────────────────────────────┐        ┌─────────────────────────────┐
  │  Input: fold_input.json     │        │  Input: MSAs + templates    │
  │                             │        │         (from Stage 1)      │
  │  - MSA search (jackhmmer,   │──────► │                             │
  │    nhmmer, hmmbuild)        │        │  - Neural network           │
  │  - Template search          │        │    inference                │
  │  - Database lookups         │        │  - Structure prediction     │
  │                             │        │                             │
  │  Resources: CPU + RAM       │        │  Resources: H100/H200 GPU   │
  │  Duration: several hours    │        │  Duration: minutes to hours │
  └─────────────────────────────┘        └─────────────────────────────┘
```

---

## Setup

### Container and Databases

Juno provides a shared AlphaFold 3 container image and pre-downloaded databases. Contact [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu) to confirm the current paths and check that you have access.

Typical locations (verify before use):

```bash
# Shared container image
AF3_CONTAINER=/scratch/alphafold3/sif/alphafold3.sif

# Shared genetic databases (~600 GB)
AF3_DB=/scratch/alphafold3/data
```

!!! note "These files are not subject to scratch purge"
    Although the container and databases reside in `/scratch`, they are protected from automatic purging. Administrators have set a higher-priority retention policy on these paths, so you do not need to copy them elsewhere.

Load Apptainer before running any AlphaFold 3 commands:

```bash
module load apptainer/1.3.4
```

### Directory Structure

Set up this layout in your work or scratch directory before submitting:

```
alphafold3/
├── af_input/
│   └── fold_input.json      # your query (see below)
├── af_output/               # results written here
└── model_parameter/
    └── af3.bin.zstd         # weights you downloaded from Google
```

```bash
mkdir -p ~/work/alphafold3/{af_input,af_output,model_parameter}
```

### Input File

AlphaFold 3 takes a JSON file describing the sequences you want to fold. A minimal example for a single protein:

```json
{
  "name": "my_protein",
  "sequences": [
    {
      "protein": {
        "id": "A",
        "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGGSSDKLLDFLREKGAVVDDIIFTAGKLEGYRGITLVNRQGHFAVQHATKLAEIIGLPESHAVKVDISGKVDTPGGITYAVVLKDPSGRYAVRGIDIPMNALDRGIDLELLAEKLGLEPGVTYAALDLLGGGPADSEGTRVTFKLVNSQRRELLPESQFTPMENAAYRAVKEAYAGAKLTAQELAERLGISPAQVSNWFINKRMRQNRPQHQAKIKQPTLLMQGGVDKSVAEILDRAEEAGISVLALKGAIDPDAIVKHIDDAGISPHQVAGYAVANARGITPDQVARWLGLSPETVRGLLAEKGFTVQELAERLGISPAQVSNWFINKRMRQNRPQHQAKIKQPTLLMQGGVDKSVAEILDRAEEAGISVLALKGAIDPDAIVKHIDDAGISPHQVAGYAVANARGITPDQVARWLGLSPETVRGLLAEKGFTVQGADLSGLSGGQRQRVAIARALAMEPDVLLLDEPTSALDPELVGEVLDVIRGLAEEGRTVVVVTHEMGFARHVSSHVVFLHQGKIEEEGAPEQVFGAPQHPRTQQFLAQVLHHHHHHGEFTPPVQAAYQKVVAGVANALAHKYHGSGPGSGSGGSGSGGSMKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGGSSDKLLDFLREKGAVVDDIIFTAGKLEGYRGITLVNRQGHFAVQHATKLAEIIGLPESHAVKVDISGKVDTPGGITYAVVLKDPSGRYAVRGIDIPMNALDRGIDLELLAEKLGLEPGVTYAALDLLGGGPADSEGTRVTFKLVNSQRRELLPESQFTPMENAAYRAVKEAYAGAKLTAQELAERLGISPAQVSNWFINKRMRQNRPQHQAKIKQPTLLMQGGVDKSVAEILDRAEEAGISVLALKGAIDPDAIVKHIDDAGISPHQVAGYAVANARGITPDQVARWLGLSPETVRGLLAEKGFTVQELAERLGISPAQVSNWFINKRMRQNRPQHQAKIKQPTLLMQGGVDKSVAEILDRAEEAGISVLALKGAIDPDAIVKHIDDAGISPHQVAGYAVANARGITPDQVARWLGLSPETVRGLLAEKGFTVQGADLSGLSGGQRQRVAIARALAMEPDVLLLDEPTSALDPELVGEVLDVIRGLAEEGRTVVVVTHEMGFARHVSSHVVFLHQGKIEEEGAPEQVFGAPQHPRTQQFLAQVLHHHHHHGEFTPPVQAAYQKVVAGVANALAHKYHGSGPGSGSGGSGSGGSMKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGGSSDKLLDFLREKGAVVDDIIFTAGKLEGYRGITLVNRQGHFAVQHATKLAEIIGLPESHAVKVDISGKVDTPGGITYAVVLKDPSGRYAVRGIDIPMNALDRGIDLELLAEKLGLEPGVTYAALDLLGGGPADSEGT"
      }
    }
  ],
  "modelSeeds": [1],
  "dialect": "alphafold3",
  "version": 1
}
```

For protein–ligand, protein–DNA, or other complex inputs, see the [AlphaFold 3 input documentation](https://github.com/google-deepmind/alphafold3/blob/main/docs/input.md).

---

## Batch Jobs

### Option 1: Two Separate Jobs (Recommended)

Split the pipeline and inference stages to make better use of the queue. The CPU stage can run on any node while the GPU stage waits for an H100/H200.

**Stage 1 — Data Pipeline (CPU)**

```bash
#!/bin/bash
#SBATCH -J af3_pipeline
#SBATCH -o logs/af3_pipeline_%j.out
#SBATCH -e logs/af3_pipeline_%j.err
#SBATCH -p normal
#SBATCH -N 1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64GB
#SBATCH -t 12:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=netID@utdallas.edu

mkdir -p logs

AF3_CONTAINER=/scratch/alphafold3/sif/alphafold3.sif
AF3_DB=/scratch/alphafold3/data
WORK_DIR=${HOME}/work/alphafold3

module load apptainer/1.3.4

apptainer exec \
    --bind ${WORK_DIR}:/af3_work \
    --bind ${AF3_DB}:/databases:ro \
    ${AF3_CONTAINER} \
    python /app/alphafold/run_alphafold.py \
        --input_dir=/af3_work/af_input \
        --output_dir=/af3_work/af_output \
        --db_dir=/databases \
        --run_data_pipeline=true \
        --run_inference=false \
        --jackhmmer_n_cpu=${SLURM_CPUS_PER_TASK} \
        --nhmmer_n_cpu=${SLURM_CPUS_PER_TASK}
```

**Stage 2 — Inference (GPU)**

```bash
#!/bin/bash
#SBATCH -J af3_inference
#SBATCH -o logs/af3_inference_%j.out
#SBATCH -e logs/af3_inference_%j.err
#SBATCH -p h100
#SBATCH -N 1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64GB
#SBATCH -t 2:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=netID@utdallas.edu

mkdir -p logs

AF3_CONTAINER=/scratch/alphafold3/sif/alphafold3.sif
AF3_DB=/scratch/alphafold3/data
WORK_DIR=${HOME}/work/alphafold3

module load apptainer/1.3.4

# Decompress model params if needed (only run once)
if [ ! -f "${WORK_DIR}/model_parameter/af3.bin" ]; then
    zstd -d "${WORK_DIR}/model_parameter/af3.bin.zstd" \
         -o "${WORK_DIR}/model_parameter/af3.bin"
fi

apptainer exec --nv \
    --bind ${WORK_DIR}:/af3_work \
    --bind ${AF3_DB}:/databases:ro \
    ${AF3_CONTAINER} \
    python /app/alphafold/run_alphafold.py \
        --input_dir=/af3_work/af_input \
        --output_dir=/af3_work/af_output \
        --model_dir=/af3_work/model_parameter \
        --db_dir=/databases \
        --run_data_pipeline=false \
        --run_inference=true
```

Submit the pipeline job first, then the inference job with a dependency:

```bash
JID=$(sbatch af3_pipeline.sh | awk '{print $NF}')
sbatch --dependency=afterok:${JID} af3_inference.sh
```

---

### Option 2: Single Combined Job

If you prefer to run everything in one step, request an H100 node and let it handle both stages. This is simpler but ties up a GPU while the CPU-only pipeline stage runs (which can take several hours).

```bash
#!/bin/bash
#SBATCH -J af3_full
#SBATCH -o logs/af3_full_%j.out
#SBATCH -e logs/af3_full_%j.err
#SBATCH -p h100
#SBATCH -N 1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64GB
#SBATCH -t 14:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=netID@utdallas.edu

mkdir -p logs

AF3_CONTAINER=/scratch/alphafold3/sif/alphafold3.sif
AF3_DB=/scratch/alphafold3/data
WORK_DIR=${HOME}/work/alphafold3

module load apptainer/1.3.4

# Decompress model params if needed (only run once)
if [ ! -f "${WORK_DIR}/model_parameter/af3.bin" ]; then
    zstd -d "${WORK_DIR}/model_parameter/af3.bin.zstd" \
         -o "${WORK_DIR}/model_parameter/af3.bin"
fi

apptainer exec --nv \
    --bind ${WORK_DIR}:/af3_work \
    --bind ${AF3_DB}:/databases:ro \
    ${AF3_CONTAINER} \
    python /app/alphafold/run_alphafold.py \
        --input_dir=/af3_work/af_input \
        --output_dir=/af3_work/af_output \
        --model_dir=/af3_work/model_parameter \
        --db_dir=/databases \
        --run_data_pipeline=true \
        --run_inference=true \
        --jackhmmer_n_cpu=${SLURM_CPUS_PER_TASK} \
        --nhmmer_n_cpu=${SLURM_CPUS_PER_TASK}
```

---

## Output

Results are written to `af_output/`. For each input, AlphaFold 3 produces:

| File | Description |
|---|---|
| `*_model.cif` | Predicted structure in mmCIF format |
| `*_summary_confidences.json` | Per-residue pLDDT and PAE scores |
| `*_confidences.json` | Full confidence data |
| `*_data.json` | All input features used |

The `model.cif` file can be opened directly in [PyMOL](https://pymol.org/), [ChimeraX](https://www.cgl.ucsf.edu/chimerax/), or [RCSB Mol*](https://molstar.org/).

---

## Tips

### Reusing Pipeline Results

Once Stage 1 completes, you can re-run Stage 2 with different random seeds without redoing the expensive database searches:

```bash
# Add --model_seeds to try multiple seeds in one inference run
python /app/alphafold/run_alphafold.py \
  --run_data_pipeline=false \
  --run_inference=true \
  --model_seeds=1,2,3,4,5 \
  ...
```

### Monitoring GPU Usage

SSH to the allocated node and watch GPU utilization during inference:

```bash
watch -n 2 nvidia-smi
```

Target: GPU utilization should be consistently **> 80%** during inference.

### Storage Considerations

The genetic databases are large (~600 GB). Use the shared databases provided on Juno rather than downloading your own copy. Your output and model weights should live in `~/work` (1 TB quota, backed up). Use `~/scratch` for temporary intermediate files if needed.

---

## Related Pages

- [GPU Computing on Juno](index.md) — GPU partitions and VRAM sizes
- [Containers](../advanced/containers.md) — how Apptainer works on Juno
- [Storage & Data Transfer](../getting-started/storage.md) — where to store large files
- [SLURM Job Scheduler](../running-programs/slurm.md) — job dependency syntax and options
