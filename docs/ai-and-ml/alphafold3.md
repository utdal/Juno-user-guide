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

AlphaFold 3 runs in two sequential stages. The `af3-run` wrapper executes both stages back-to-back in a single job, so you don't manage them separately — the diagram below is just to show what happens under the hood.

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

### The `af3-run` wrapper

You do not need to invoke the container, databases, or model weights directly. Juno provides an `af3-run` wrapper that bundles the shared AlphaFold 3 container image, the pre-downloaded genetic databases, and the centrally-maintained model parameters into a single command. It runs both the data pipeline and inference stages for you.

Load the two required modules to make the wrapper available:

```bash
module load apptainer
module load alphafold3
```

Once loaded, the entire pipeline is just:

```bash
af3-run --input_dir=<your_input_dir> --output_dir=<your_output_dir>
```

!!! note "Databases and weights are managed for you"
    The shared container and the ~600 GB genetic databases live on Juno and are protected from automatic scratch purging. The model parameters are maintained centrally under UT Dallas's institutional access — you do **not** download or decompress any weights yourself. The wrapper points to all of these automatically.

### Directory Structure

Set up this layout in your work or scratch directory before submitting:

```
alphafold3/
├── af_input/
│   └── fold_input.json      # your query (see below)
└── af_output/               # results written here
```

```bash
mkdir -p ~/work/alphafold3/{af_input,af_output}
```

The model weights are supplied by the `af3-run` wrapper, so you do not need a `model_parameter/` directory.

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

## Batch Job

The `af3-run` wrapper handles the full pipeline — data pipeline and inference — in a single GPU job. Save the following as `af3_full.sh`, edit the `--mail-user` and paths for your account, and submit with `sbatch af3_full.sh`.

```bash
#!/bin/bash
#SBATCH -J af3_full
#SBATCH -o logs/af3_full_%j.out
#SBATCH -e logs/af3_full_%j.err
#SBATCH -p h100
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64GB
#SBATCH -t 14:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=netID@utdallas.edu

mkdir -p logs

WORK_DIR=${HOME}/work/alphafold3

module load apptainer
module load alphafold3

af3-run --input_dir=${WORK_DIR}/af_input --output_dir=${WORK_DIR}/af_output
```

Submit it:

```bash
sbatch af3_full.sh
```

The job runs the CPU-bound data pipeline followed by GPU inference in one allocation. Because the pipeline stage can take several hours, keep the walltime generous (14 hours above is a safe upper bound for most inputs).

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

### Trying Multiple Seeds

To sample several predictions, list the seeds you want in the `modelSeeds` field of your `fold_input.json` (e.g. `"modelSeeds": [1, 2, 3, 4, 5]`). AlphaFold 3 reuses the results of the data-pipeline stage across all seeds, so the expensive database searches only run once per input.

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
