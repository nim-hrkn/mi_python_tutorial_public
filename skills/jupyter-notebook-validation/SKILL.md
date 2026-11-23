---
name: jupyter-notebook-validation
description: Validate numbered materials informatics tutorial notebooks with the Miniforge pymc_env Jupyter kernel, preserve intended teaching failures, and save outputs when requested. Use for chapter-wide execution, notebook error diagnosis, or stale kernel references in this tutorial.
---

# Jupyter Notebook Validation

## Select and verify the environment

- Use the requested Conda environment, normally `pymc_env` with Python 3.14. Check `conda run -n pymc_env python -V` and `conda run -n pymc_env python -m jupyterlab --version`. A shell may find user-installed Jupyter launchers before the environment's executables.
- Check both the notebook's `metadata.kernelspec.name` and the registered spec's `argv`. A successful JupyterLab launch does not establish which Python a notebook uses. To verify the selected kernel, execute a cell that prints `sys.executable` and `sys.version`.
- Use an absolute environment interpreter in the kernel spec or launch from the activated environment. If CPU PyTorch loads the system C++ runtime before NumPy, reproduce the import in a fresh kernel and inspect the environment's activation settings before changing package versions.

## Execute and inspect

- Inventory the requested numbered chapters and their notebooks. Exclude `junk/` and `.ipynb_checkpoints/` from normal chapter sweeps unless requested. Count Markdown-only or empty notebooks separately.
- Start a fresh kernel for each notebook and use the notebook's parent as the execution directory. Run in chapter order when earlier lessons generate data for later lessons. For validation only, use a temporary copy with the same directory structure, including shared data and chapter assets.
- When the user requests saved outputs, write the executed notebook after a successful run. Executing with `nbclient` alone keeps the result in memory. For failures, record the notebook path, first failing cell, exception, and elapsed time. Report cell numbers as one-based positions including Markdown cells, and record timeouts separately.
- Resolve missing imports using the notebook's dependency documentation and a Python-compatible distribution. Check `python -m pip check` after changing the environment. Preserve teaching cells that intentionally demonstrate exceptions, following any explicit request to leave an error uncaught. If the lesson should run through, catch only the specific expected exception and display it.
- Rerun a repaired notebook from the first cell. Review notebook sources and saved outputs separately from generated data and figures. Keep validation logs outside the repository unless the user asks to retain them there.
