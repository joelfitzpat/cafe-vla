#!/bin/bash
# =============================================================================
# Kaya HPC — SLURM training job for OpenVLA-OFT fine-tuning
# =============================================================================
# Submit with:
#   sbatch kaya/train.slurm
#
# Check status:
#   squeue -u $USER
#   tail -f logs/train_<jobid>.out
#
# Before submitting, fill in:
#   --mail-user    your UWA email
#   --partition    run `sinfo` on Kaya to see available GPU partitions
#   DATA_DIR       path to your prepared RLDS/OXE dataset on Kaya scratch
#   RUN_DIR        where checkpoints and logs should be saved
# =============================================================================

#SBATCH --job-name=cafe-vla-train
#SBATCH --partition=gpu                      # check with: sinfo
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1                         # request 1 GPU; add type if needed e.g. gpu:a100:1
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=logs/train_%j.out
#SBATCH --error=logs/train_%j.err
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=YOUR_EMAIL@student.uwa.edu.au

set -euo pipefail

# ── Modules ────────────────────────────────────────────────────────────────────
module load cuda/12.4.0
module load miniconda3

# ── Activate conda environment ─────────────────────────────────────────────────
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate openvla-oft

# ── Paths ──────────────────────────────────────────────────────────────────────
OPENVLA_DIR="${HOME}/openvla-oft"
export PYTHONPATH="${OPENVLA_DIR}:${PYTHONPATH:-}"

# Weights and datasets go to scratch — home quota is too small for 15GB+ models
export HF_HOME="/scratch/${USER}/.cache/huggingface"
DATA_DIR="/scratch/${USER}/datasets/cafe_robot"    # fill in your dataset path
RUN_DIR="/scratch/${USER}/runs/cafe-vla-$(date +%Y%m%d_%H%M%S)"

mkdir -p "${HF_HOME}" "${RUN_DIR}" logs

echo "Job ${SLURM_JOB_ID} starting on $(hostname)"
echo "GPUs: $(nvidia-smi --query-gpu=name --format=csv,noheader)"
echo "Run dir: ${RUN_DIR}"

# ── Training ───────────────────────────────────────────────────────────────────
cd "${OPENVLA_DIR}"

# Single-GPU fine-tuning with LoRA (rank 32).
# Adjust --num_processes for multi-GPU (e.g. 2 or 4).
accelerate launch \
    --num_processes=1 \
    --mixed_precision=bf16 \
    experiments/robot/finetune_openvla_oft.py \
        --vla_path "moojink/openvla-7b-oft" \
        --data_root_dir "${DATA_DIR}" \
        --dataset_name "cafe_robot" \
        --run_root_dir "${RUN_DIR}" \
        --use_l1_regression True \
        --use_diffusion False \
        --use_film False \
        --use_proprio True \
        --num_images_in_input 2 \
        --lora_rank 32 \
        --batch_size 1 \
        --grad_accumulation_steps 8 \
        --learning_rate 5e-4 \
        --num_steps 10000 \
        --save_freq 1000 \
        --image_aug True \
        --wandb_project "cafe-vla" \
        --use_wandb False    # set True and add --wandb_entity if you use W&B

echo "Training complete. Checkpoints saved to: ${RUN_DIR}"
