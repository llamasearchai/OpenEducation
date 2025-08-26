#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

echo "For FAISS on macOS, install via conda-forge:"
echo "  micromamba create -n oe -c conda-forge python=3.11 faiss-cpu"
echo "  micromamba activate oe"
echo ""
echo "Setup complete! Activate the environment with:"
echo "  source .venv/bin/activate"
