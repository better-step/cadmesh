# STEP-to-HDF5 Conversion and Point Cloud Sampling (steptohdf5 + ABS-HDF5)

## Introduction

This guide explains how to use **steptohdf5** and **ABS-HDF5** together to convert CAD models from STEP/STP files into HDF5 datasets, and then sample those datasets into point clouds. These two tools are designed to work in tandem:

- **steptohdf5** – a converter that turns CAD solids (from *.step or *.stp* files) into **analysis-ready HDF5** files. Each HDF5 file contains the model’s geometry (B-rep surfaces and curves), topology (faces, edges, etc.), and a high-quality triangular mesh for the surfaces. *Currently, steptohdf5 is not available on PyPI or Conda, so it is run via a Docker container.* (A PyPI/Conda release is planned – until then, use Docker as described below.)

- **ABS-HDF5** – a Python/C++ toolkit (available on PyPI) that **reads the HDF5 files produced by steptohdf5** and generates point cloud samples from the geometry. It provides command-line tools to export point clouds to PLY files or Python pickles, and also a Python API for advanced sampling (including fast Poisson-disk downsampling for blue-noise distributions).

**Workflow Overview:** Using these tools, a typical pipeline is:
1. **Convert** a CAD model from STEP to HDF5 (using steptohdf5).  
2. **Sample** the HDF5 model to a point cloud (using ABS-HDF5).  

This README will cover the installation of both tools, then walk through the conversion and sampling steps with examples (including single-file and batch processing), and provide basic API usage for each. Both projects are open-source under the Better Step initiative – see their GitHub repositories for more details:
- **steptohdf5**: https://github.com/better-step/cadmesh  
- **ABS-HDF5**: https://github.com/better-step/abs  

---

## Installation

### ABS-HDF5 (via pip)

**ABS-HDF5** is distributed on PyPI. Install it into your Python environment (we recommend using a virtual environment):

```bash
pip install abs-hdf5
```

This installs the `abs` Python package along with two CLI tools: `abs-to-ply` and `abs-to-pickle`. No additional system dependencies are required.

> **Tip:** Ensure your `pip` is up-to-date and you’re using Python 3.8 or newer.

---

### Sample HDF5 → Point Cloud using ABS-HDF5

With ABS-HDF5 installed, use the `abs-to-ply` CLI to generate PLY point clouds from HDF5:

```bash
abs-to-ply hdf5/MyModel.hdf5 samples -n 5000 -j 8
```

- `hdf5/MyModel.hdf5`: Input HDF5 file.  
- `samples`: Output folder for PLY files.  
- `-n 5000`: Points per part after Poisson-disk downsampling.  
- `-j 8`: Parallel workers.

**Batch PLY conversion:**

Convert all HDF5 files in `hdf5/`:

```bash
abs-to-ply hdf5/ samples -n 3000 -j 8
```

This creates `samples/MyModel_part001.ply`, etc., for each part of each model.

**abs-to-pickle example:**

```bash
abs-to-pickle hdf5/ pickles -n 5000 -j 4
```

Generates `.pkl` files containing Python dicts:
```python
{
  'file': 'MyModel.h5',
  'part': 1,
  'points': ndarray(N,3),
  'normals': ndarray(N,3)
}
```

---

## API Usage

#### steptohdf5 Python API (cadmesh)

```python
from cadmesh import convert_step
from cadmesh.utils.processing import batch_convert_step_files

# Single conversion
h5 = convert_step('cad_files/Model.step', output_dir='hdf5', log_dir='logs')

# Batch conversion
ok, failed = batch_convert_step_files(
    input_list_path='cad_files/list.txt',
    output_dir='hdf5',
    log_dir='logs',
    n_jobs=4
)
```

#### ABS-HDF5 Python API (abs)

```python
import abs

# Read parts from HDF5
parts = abs.read_parts('hdf5/Model.h5')

# Sample points + normals
def face_normals(part, topo, uv):
    return topo.normal(uv) if topo.is_face() else None

points, normals = abs.sample_parts(parts, num_samples=10000, lambda_func=face_normals)

# Poisson-disk downsample to 1000 points
idx = abs.poisson_disk_downsample(points[0], 1000)
sub_points = points[0][idx]
sub_normals = normals[0][idx]
```

---

## Development & Testing

```bash

# abs-hdf5
git clone https://github.com/better-step/abs.git
cd abs
pip install -e .[dev]
pytest -q
```

---

## Contributing & License

- **steptohdf5** (Python) – GPL-3.0  
- **abs-hdf5** Python bindings – MIT  
- **abs-hdf5** C++ core – MPL-2.0  

Please review the Code of Conduct and open an issue before submitting larger changes.

---
*Happy converting & sampling!*  – The Better Step maintainers
