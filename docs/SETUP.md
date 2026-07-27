# Setup — Café VLA (Training Branch)

This branch targets **UWA's Kaya HPC** for fine-tuning OpenVLA-OFT.
The Docker/local dev setup lives on `master`.

---

## Environment overview

| Component       | Where it runs      | How                        |
|-----------------|--------------------|----------------------------|
| Fine-tuning     | Kaya HPC           | SLURM + conda              |
| Inference/ROS 2 | External server    | Stays on `master` branch   |
| Simulation      | Local dev machine  | Stays on `master` branch   |

Kaya has no Docker and no sudo. Everything here uses conda environments
and the SLURM job scheduler.

---

## First-time setup on Kaya

### 1. Clone the repo onto Kaya

```bash
# On a Kaya login node
git clone <repo-url> ~/cafe-vla
cd ~/cafe-vla
git checkout Training
```

### 2. Check available modules

```bash
module avail cuda
module avail conda   # look for miniconda3 or anaconda3
```

Update the `module load` lines in `kaya/setup.sh`, `kaya/activate.sh`,
and `kaya/train.slurm` to match what Kaya actually has.

### 3. Run the setup script

```bash
bash kaya/setup.sh
```

This script:
- Creates a conda environment named `openvla-oft` (Python 3.10)
- Installs PyTorch (CUDA 12.4) + all ML dependencies
- Clones `moojink/openvla-oft` to `~/openvla-oft` and installs it
- Installs the custom transformers fork required for OFT bidirectional attention
- Builds `flash-attn==2.5.5` from source (takes 10–20 min)

> **Note:** If Kaya's login nodes restrict long-running compilations,
> run the flash-attn build step inside an interactive GPU session:
> ```bash
> salloc --gres=gpu:1 --time=01:00:00
> source kaya/activate.sh
> pip install "flash-attn==2.5.5" --no-build-isolation
> ```

### 4. HuggingFace login (required before first model download)

```bash
source kaya/activate.sh
huggingface-cli login
```

Model weights (~15 GB) are cached to `/scratch/$USER/.cache/huggingface`
to avoid filling your home directory quota.

---

## Submitting a training job

Edit `kaya/train.slurm` to fill in:
- `--mail-user` — your UWA email
- `DATA_DIR` — path to your dataset on Kaya scratch
- GPU type/count if needed (check `sinfo` for partition details)

Then submit:

```bash
mkdir -p logs
sbatch kaya/train.slurm
```

Monitor the job:

```bash
squeue -u $USER
tail -f logs/train_<jobid>.out
```

---

## Interactive / debugging sessions

```bash
# Source (not execute) the activate script
source kaya/activate.sh

# Then work normally, e.g.:
python ~/openvla-oft/experiments/robot/finetune_openvla_oft.py --help
```

---

## Dataset preparation

The training script expects data in RLDS/OXE format, as consumed by
`dlimp_openvla`. How to get there from your raw café recordings is
documented separately (TBD — data collection is Semester 2 scope).

---

## Key paths on Kaya

| Path | Purpose |
|------|---------|
| `~/openvla-oft/` | openvla-oft repo (installed in editable mode) |
| `/scratch/$USER/.cache/huggingface/` | Model weight cache |
| `/scratch/$USER/datasets/` | Training datasets |
| `/scratch/$USER/runs/` | Checkpoints and training logs |
