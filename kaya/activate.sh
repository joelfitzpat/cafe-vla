#!/bin/bash
# =============================================================================
# Kaya HPC — Activate openvla-oft environment for interactive sessions
# =============================================================================
# Usage (must be sourced, not executed):
#   source kaya/activate.sh
#
# Use this for interactive work (testing, debugging, data prep).
# For training runs, submit kaya/train.slurm instead.
# =============================================================================

module load cuda/12.4.0    # adjust to match your Kaya module name
module load miniconda3      # adjust to match your Kaya module name

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate openvla-oft

export PYTHONPATH="${HOME}/openvla-oft:${PYTHONPATH:-}"

# Keep model weights off the home quota — scratch is larger and faster
export HF_HOME="/scratch/${USER}/.cache/huggingface"
mkdir -p "${HF_HOME}"

echo "openvla-oft environment active."
echo "  PYTHONPATH  -> ${HOME}/openvla-oft"
echo "  HF_HOME     -> ${HF_HOME}"
