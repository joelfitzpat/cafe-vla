#!/bin/bash
# =============================================================================
# Kaya HPC — One-time conda environment setup
# =============================================================================
# Run once from a Kaya LOGIN NODE:
#   bash kaya/setup.sh
#
# After setup, use kaya/activate.sh for interactive sessions, or
# submit kaya/train.slurm to run a training job.
#
# Notes:
#   - flash-attn compiles from source and needs CUDA headers. This script
#     runs it here on the login node, which is slow but avoids needing a
#     separate interactive GPU session. If login node compilation is
#     restricted, comment out the flash-attn line and run it inside
#     an salloc session with a GPU.
#   - Module names (cuda/12.4.0, miniconda3) are guesses — run
#     `module avail cuda` and `module avail conda` on Kaya to confirm.
# =============================================================================

set -euo pipefail

ENV_NAME="openvla-oft"
OPENVLA_DIR="${HOME}/openvla-oft"

# ── 1. Load modules ────────────────────────────────────────────────────────────
echo "[1/6] Loading modules..."
module load cuda/12.4.0      # adjust to match: module avail cuda
module load miniconda3        # adjust to match: module avail conda

# ── 2. Create conda environment ────────────────────────────────────────────────
echo "[2/6] Creating conda environment '${ENV_NAME}'..."
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "  Environment already exists — skipping creation."
    echo "  To rebuild from scratch: conda env remove -n ${ENV_NAME}"
else
    conda create -n "${ENV_NAME}" python=3.10 -y
fi

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "${ENV_NAME}"

# ── 3. PyTorch with CUDA 12.4 ─────────────────────────────────────────────────
echo "[3/6] Installing PyTorch (cu124)..."
pip install --no-cache-dir \
    torch torchvision \
    --index-url https://download.pytorch.org/whl/cu124

# ── 4. Clone and install openvla-oft ──────────────────────────────────────────
echo "[4/6] Setting up openvla-oft..."
if [ ! -d "${OPENVLA_DIR}" ]; then
    git clone https://github.com/moojink/openvla-oft.git "${OPENVLA_DIR}"
else
    echo "  ${OPENVLA_DIR} already exists — skipping clone."
fi
cd "${OPENVLA_DIR}"
pip install --no-cache-dir -e .

# Custom transformers fork (required for bidirectional attention in OFT)
pip install --no-cache-dir \
    git+https://github.com/moojink/transformers-openvla-oft.git

# ── 5. Remaining ML dependencies ───────────────────────────────────────────────
echo "[5/6] Installing ML dependencies..."
pip install --no-cache-dir \
    huggingface_hub \
    accelerate \
    "timm==0.9.10" \
    einops \
    pillow \
    draccus \
    json-numpy \
    jsonlines \
    rich \
    "sentencepiece==0.1.99" \
    "peft==0.11.1" \
    protobuf \
    requests \
    "tensorflow>=2.16.0" \
    "tensorflow-datasets>=4.9.4"

# dlimp: install without deps to skip its tensorflow==2.15.0 pin (incompatible
# with Python 3.10 on newer CUDA stacks). Its data-loading code is what we use.
pip install --no-cache-dir --no-deps \
    git+https://github.com/moojink/dlimp_openvla

pip install --no-cache-dir "diffusers==0.30.3" bitsandbytes

# ── 6. Flash Attention 2 (compiles from source) ────────────────────────────────
echo "[6/6] Building flash-attn (this takes 10-20 min)..."
pip install --no-cache-dir packaging ninja
ninja --version  # sanity check — should print a version and exit 0
pip install --no-cache-dir "flash-attn==2.5.5" --no-build-isolation

echo ""
echo "============================================================"
echo " Setup complete."
echo " Conda environment '${ENV_NAME}' is ready on Kaya."
echo ""
echo " Next steps:"
echo "   Interactive:  source kaya/activate.sh"
echo "   Training job: sbatch kaya/train.slurm"
echo "============================================================"
