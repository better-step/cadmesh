# STEP-to-HDF5

Converts STEP/STP CAD files into analysis-ready HDF5 files compatible with [ABS-HDF5](https://github.com/better-step/abs). Each output file contains the model's B-Rep geometry (surfaces and curves), topology (faces, edges, loops, half-edges), and a triangular mesh per face.

## Installation

### Option A: Docker

```bash
docker pull itsmechandu/steptohdf5:latest
```

### Option B: Install from source

```bash
git clone https://github.com/better-step/cadmesh.git
cd cadmesh
pip install -e .
```
## Usage

### Option A: Docker

You need to first create a text file listing your STEP files:

```bash
cd /path/to/your/folder
ls *.step > input.txt
```
Then run the conversion script:`

```bash
docker run --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  itsmechandu/steptohdf5:latest \
  steptohdf5 --list input.txt -o hdf5 -l logs -j 4
```

The `-v` flag mounts your local folder into the container. Output files will appear in `/path/to/your/folder/hdf5/`. The `-j` flag controls the number of parallel workers.

### Option B: From source

You need to first create a text file listing your STEP files:

```bash
ls *.step > input.txt
```

Then run the conversion script:

```bash
python src/steptohdf5/cloud_conversion.py \
  --input /path/to/input.txt \
  --output /path/to/output \
  --log /path/to/logs
```

## Converting data to Version 3.0

Our latest dataset version is version 3.0, but we continue to support version 2.0 files as well. Both versions expose the exact same half-edge structure and object-oriented Python interface, reading, traversing, and processing works identically regardless of which version you have.

The two versions differ only in their internal HDF5 layout:

- **Version 2.0**: the legacy output of steptohdf5. Structured hierarchically, making it easier to inspect manually with an HDF5 viewer.
- **Version 3.0**: a flattened layout that reduces memory usage and speeds up loading. Less human-readable in the raw file, but identical to version 2.0 through the library.

To upgrade a version 2.0 file to version 3.0, run the `convert_new_format.py` script in the [`scripts/`](scripts/) folder:

```bash
python scripts/convert_new_format.py --input path/to/model.hdf5
```

This will produce a new file at `path/to/model_new.hdf5`.

