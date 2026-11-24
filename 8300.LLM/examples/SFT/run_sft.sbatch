#!/usr/bin/env bash
#SBATCH --job-name=SFT
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=04:00:00
#SBATCH --output=slurm-%j.out
set -euo pipefail

cd "${SLURM_SUBMIT_DIR:?Submit from the repository root}"
source "$(conda info --base)/etc/profile.d/conda.sh"
if [[ -d "$PWD/.conda-envs/SFT/conda-meta" ]]; then
    conda activate "$PWD/.conda-envs/SFT"
else
    conda activate SFT
fi
export PYTHONNOUSERSITE=1
export TOKENIZERS_PARALLELISM=false
sft_python="$CONDA_PREFIX/bin/python"

run_dir="$PWD/runs/${SLURM_JOB_ID}"
mkdir -p "$PWD/runs"
mkdir "$run_dir"
"$sft_python" -m pip freeze > "$run_dir/packages.txt"
"$sft_python" experiment.py train answer_only "$run_dir"
"$sft_python" experiment.py train worked "$run_dir"
for condition in baseline answer_only worked; do
    "$sft_python" experiment.py evaluate "$condition" "$run_dir"
done
