<!--
README.md for **steptohdf5**
====================================================================
Convert SOLID-CAD (STEP / STP) to a single, self-contained
HDF5 file that stores geometry + topology + ( optional ) surface
meshes – with a one-line CLI **or** a small Python API.
--------------------------------------------------------------------
-->

# steptohdf5

[![PyPI version](https://img.shields.io/pypi/v/steptohdf5)](https://pypi.org/project/steptohdf5/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![CI status](https://github.com/better-step/cadmesh/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/better-step/cadmesh/actions)

> **steptohdf5** turns CAD solids into analysis-ready data sets –
> one HDF5 file per model, including a high-quality surface mesh.
> It is a thin wrapper around [pythonocc-core 7.4.0](https://pypi.org/project/pythonocc-core/), `meshio`, and a few hundred lines of well-tested extraction logic.

---

## ✨ Features

- **Single-file output**: geometry, topology, statistics, meshes in one HDF5 file.
- **Face–triangle mapping**: trace every triangle back to its CAD face.
- **CLI & Python API**: convert from a shell script *or* inside a Jupyter notebook.
- **Batch-ready**: built-in parallel processing via `joblib` and progress bars with `tqdm`.


---

## 🔧 Installation


# 1️⃣  Install Open Cascade bindings (pythonocc-core 7.4.0) from conda-forge
conda install -c conda-forge pythonocc-core=7.4.0 igl

#    note: the conda package already pulls numpy, h5py, etc.

# 2️⃣  Install steptohdf5 and the remaining pure-Python deps via pip
pip install steptohdf5-0.1.0-py3-none-any.whl        # local wheel
#  or, once released:
pip install steptohdf5


Install from PyPI:

```bash
pip install steptohdf5
```

### Runtime dependencies

| Package                 | Note                                                                                     |
|-------------------------|------------------------------------------------------------------------------------------|
| numpy                   | Mathematical utilities                                                                   |
| pythonocc-core==7.4.0   | Open Cascade 7.4 – bundled wheels on Linux/Win/macOS‑x86_64. On Apple Silicon, use conda-forge |
| igl                     | Geometric predicates (PyPI wheel)                                                        |
| h5py                    | HDF5 read/write support                                                                  |
| meshio                  | Mesh import/export                                                                       |
| meshplot                | Optional 3D visualization                                                                 |
| joblib                  | Multiprocessing pool                                                                     |

If the Open Cascade wheel fails on your platform:

```bash
conda install -c conda-forge pythonocc-core=7.4.0
pip install steptohdf5 --no-deps
```

---

## 🚀 Quick start (CLI)

Convert a single STEP file to HDF5:

```bash
steptohdf5 Gear.step -o out -l logs
```

Batch convert multiple models (skip meshes, 8 processes):

```bash
steptohdf5 --list models.txt -o out -l logs -j 8 --no-mesh
```

Process all `.stp` files in a folder tree:

```bash
steptohdf5 --folder ./cad --pattern "*.stp" -o out -l logs -j 4
```

Run `steptohdf5 --help` for the full argument list.

---

## 🐍 Quick start (Python API)

```python
from cadmesh import convert_step   # cadmesh is the internal module name

# Single file → Path('out/Gear.hdf5')
h5 = convert_step(
    "Gear.step",
    output_dir="out",
    log_dir="logs"
)

# Batch conversion --------------------------------------------------
from cadmesh.utils.processing import batch_convert_step_files
ok, failed = batch_convert_step_files(
    input_list_path="models.txt",
    output_dir="out",
    log_dir="logs",
    n_jobs=8
)
print(f"{len(ok)} done, {len(failed)} failed")
```

`cadmesh.core.StepProcessor` exposes raw dictionaries (`geometry_data`, `topology_data`, `stat_data`) for direct access.

---

## 📂 HDF5 layout

```
model.h5
└─ parts/                # Contains all parts; attribute: "version" (string, e.g., "2.0")
   ├─ part_001/          # One group per part
   │  ├─ geometry/       # B-rep entities, surfaces, poles, bounding box
   │  ├─ topology/       # Bodies, faces, edges, orientation flags
   │  └─ mesh/           # Mesh/<face_id>/points + triangles
   ├─ part_002/
   └─ ...
```

Read it with `h5py` or any HDF5 viewer.

---

## 🖥️ Development & tests

```bash
git clone https://github.com/better-step/cadmesh
cd cadmesh
pip install -e .[dev]      # ruff, pytest, coverage, …
pytest -q
```

---

## 🤝 Contributing

Issues and pull requests are welcome! Please open an issue first if you plan a larger change.

---

## 📜 License

GNU General Public License v3.0

© Better Step 2025 – free to use, modify, and share under the same license.

---

## ✏️ Citation

If **steptohdf5** contributes to your academic work, cite it as: [TODO]

> Better Step (2025). steptohdf5 0.1.0 [software]. https://pypi.org/project/steptohdf5

## 📧 Contact
For questions, suggestions, or bug reports, please open an issue on GitHub.
