# AlphaFold 3

AlphaFold 3, developed by Google DeepMind and Isomorphic Labs, predicts the 3D structures of proteins and their interactions with DNA, RNA, ligands, and ions. It is significantly more capable than AlphaFold 2, supporting a broader range of biomolecular complexes in a single model.

---

## Before You Start

### Licensing and Model Weights

!!! warning "Model weights require a separate request"
    The AlphaFold 3 model parameters are **not bundled with the software**. You must request them directly from Google DeepMind before you can run inference on Juno. Approval is at Google DeepMind's sole discretion.

**Step 1 — Read the policy documents**

Before filling out the form, read all three documents:

- [AlphaFold 3 Weights Terms of Use](https://github.com/google-deepmind/alphafold3/blob/main/WEIGHTS_TERMS_OF_USE.md)
- [Prohibited Use Policy](https://github.com/google-deepmind/alphafold3/blob/main/PROHIBITED_USE_POLICY.md)
- [Output Terms of Use](https://github.com/google-deepmind/alphafold3/blob/main/OUTPUT_TERMS_OF_USE.md)

**Step 2 — Fill out the [model request form](https://forms.gle/svvpY4u2jsHEwWYS6)**

The form has three pages:

*Page 1*

| Field | What to enter |
|---|---|
| Email | Your UT Dallas email (`netID@utdallas.edu`) |
| Google account email | A **personal Gmail address** ending in `@gmail.com` |
| Organization website | `https://www.utdallas.edu` |

!!! danger "Do not use your UT Dallas email as the Google account"
    The second email field must be a `@gmail.com` address. Using your institutional address here will result in your request being rejected. If you don't have a personal Gmail account, create one at [gmail.com](https://gmail.com) before starting the form.

*Page 2*

A single question asks whether you will share access to the model parameters with other researchers. **Select No.**

*Page 3*

Review the summary, confirm you understand the terms, and submit.

**Step 3 — Wait for approval and download**

You will receive two emails:

1. An immediate acknowledgment confirming your submission was received.
2. A second email (within a few hours to several days) containing a **Google Drive download link**.

!!! warning "Download within 7 days"
    The download link expires **7 days** after the approval email arrives. Download the file promptly and save it to a backed-up location.

The weights file is named `af3.bin.zstd` and is approximately **1 GB** compressed. Place it at:

```
~/work/alphafold3/model_parameter/af3.bin.zstd
```

### GPU Requirements

AlphaFold 3 inference requires a GPU with **at least 80 GB of VRAM**. On Juno, use the `h100` or `h200` partitions.

| Partition | GPU | VRAM | Suitable? |
|---|---|---|---|
| `h100` | NVIDIA H100 | 80–94 GB | Yes (recommended) |
| `h200` | NVIDIA H200 SXM5 | 141 GB | Yes |
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
AF3_CONTAINER=/groups/shared/containers/alphafold3.sif

# Shared genetic databases (~600 GB)
AF3_DB=/groups/shared/alphafold3/databases
```

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
        "sequence": "MAHHHHHHVGTLSDKPQGPGQRPPSTSPQPASESSQDGSMTPRQPPTSLVDKIGGPQRAALDFLSSLQAAAGKSDQKVLQKLPEPRSLLKSFKASQTDLRRELNLADRQKLWKEVKDHIEALGPEVSLEEVLEAMLKAANSGCSEENPDAVMESLKKLHGELANACETVSQALDKQNLHLHALDQTRALKAYIQEQELAIGAESKVLLYINQTQSIFQKLAQALQSVLQQQGSSEDTLHDFFQDFHEGKQ"
      }
    }
  ],
  "modelSeeds": [1]
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

AF3_CONTAINER=/groups/shared/containers/alphafold3.sif
AF3_DB=/groups/shared/alphafold3/databases
WORK_DIR=~/work/alphafold3

module load apptainer/1.3.4

apptainer exec \
  --bind ${WORK_DIR}:/af3_work \
  --bind ${AF3_DB}:/databases:ro \
  ${AF3_CONTAINER} \
  python /app/alphafold3/run_alphafold.py \
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

AF3_CONTAINER=/groups/shared/containers/alphafold3.sif
AF3_DB=/groups/shared/alphafold3/databases
WORK_DIR=~/work/alphafold3

module load apptainer/1.3.4

apptainer exec --nv \
  --bind ${WORK_DIR}:/af3_work \
  --bind ${AF3_DB}:/databases:ro \
  ${AF3_CONTAINER} \
  python /app/alphafold3/run_alphafold.py \
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

AF3_CONTAINER=/groups/shared/containers/alphafold3.sif
AF3_DB=/groups/shared/alphafold3/databases
WORK_DIR=~/work/alphafold3

module load apptainer/1.3.4

apptainer exec --nv \
  --bind ${WORK_DIR}:/af3_work \
  --bind ${AF3_DB}:/databases:ro \
  ${AF3_CONTAINER} \
  python /app/alphafold3/run_alphafold.py \
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
python /app/alphafold3/run_alphafold.py \
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
