# steptohdf5

Convert STEP (`.step`/`.stp`) CAD files to HDF5 (`.hdf5`) using Docker.

---

## Prerequisites

- **Docker** installed and running:
  - **Linux**: Install Docker Engine via your package manager (e.g. `apt`, `dnf`, `pacman`).
  - **Windows**: Install Docker Desktop (requires Windows 10/11 Pro or Home with WSL2).

- Your CAD models in `.step` or `.stp` format.

---

## 1. Pull the Docker Image

```bash
docker pull itsmechandu/steptohdf5:latest
```

---

## 2. Prepare Your Workspace

Create a host‑side directory named `cad_jobs` with three subfolders:

```
cad_jobs/
├── input_files/    ← place your .step/.stp files here
├── output/         ← will receive the converted .hdf5 files
└── logs/           ← will receive conversion log files
```

### Linux (bash)

```bash
mkdir -p ~/cad_jobs/{input_files,output,logs}
mv /path/to/your/*.step ~/cad_jobs/input_files/
```

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Path $HOME\cad_jobs\input_files,$HOME\cad_jobs\output,$HOME\cad_jobs\logs
Move-Item C:\path\to\your\*.step $HOME\cad_jobs\input_files\
```

### Windows CMD

```cmd
mkdir %USERPROFILE%\cad_jobs\input_files %USERPROFILE%\cad_jobs\output %USERPROFILE%\cad_jobs\logs
move C:\path\to\your\*.step %USERPROFILE%\cad_jobs\input_files\
```

---

## 3. Converting a Single File

Run a one‑off Docker container:

### Linux & WSL (bash)

```bash
docker run --rm \
  -v ~/cad_jobs:/workspace \
  -w /workspace \
  itsmechandu/steptohdf5:latest \
  input_files/MyModel.step \
  -o output \
  -l logs
```

### Windows PowerShell

```powershell
docker run --rm \`
  -v ${HOME}/cad_jobs:/workspace \`
  -w /workspace \`
  itsmechandu/steptohdf5:latest \`
  input_files\MyModel.step \`
  -o output \`
  -l logs
```

### Windows CMD

```cmd
docker run --rm ^
  -v %USERPROFILE%\cad_jobs:/workspace ^
  -w /workspace ^
  itsmechandu/steptohdf5:latest ^
  input_files\MyModel.step ^
  -o output ^
  -l logs
```

- `-v …:/workspace` mounts your host folder into the container.  
- `-w /workspace` sets the working directory.  
- `input_files/MyModel.step` is your input file.  
- `-o output` writes `MyModel.hdf5` into `cad_jobs/output`.  
- `-l logs` writes `MyModel.log` into `cad_jobs/logs`.  

**Result**:

```
~/cad_jobs/output/MyModel.hdf5
~/cad_jobs/logs/MyModel.log
```
(Windows paths under `%USERPROFILE%\cad_jobs\…`)

---

## 4. Converting Multiple Files (Batch Mode)

### 4.1 Generate a List of Files

#### Linux & WSL

```bash
cd ~/cad_jobs
ls input_files/*.step > input_files/list.txt
```

#### Windows PowerShell

```powershell
Set-Location $HOME\cad_jobs
Get-ChildItem input_files\*.step | ForEach-Object { $_.Name } > input_files\list.txt
```

#### Windows CMD

```cmd
cd %USERPROFILE%\cad_jobs
dir /b input_files\*.step > input_files\list.txt
```

The file `input_files/list.txt` should look like:

```
input_files/Box.step
input_files/Cone.step
input_files/Cylinder.step
…
```

### 4.2 Run Batch Conversion

Adjust `-j` for the number of parallel jobs (e.g. CPU cores).

#### Linux & WSL (bash)

```bash
docker run --rm \
  -v ~/cad_jobs:/workspace \
  -w /workspace \
  itsmechandu/steptohdf5:latest \
  --list input_files/list.txt \
  -o output \
  -l logs \
  -j 4
```

#### Windows PowerShell

```powershell
docker run --rm \`
  -v ${HOME}/cad_jobs:/workspace \`
  -w /workspace \`
  itsmechandu/steptohdf5:latest \`
  --list input_files\list.txt \`
  -o output \`
  -l logs \`
  -j 4
```

#### Windows CMD

```cmd
docker run --rm ^
  -v %USERPROFILE%\cad_jobs:/workspace ^
  -w /workspace ^
  itsmechandu/steptohdf5:latest ^
  --list input_files\list.txt ^
  -o output ^
  -l logs ^
  -j 4
```

- `--list input_files/list.txt` points to your list of files.  
- `-j 4` processes up to 4 conversions in parallel.  

**Sample output**:

```
✓  input_files/Box.step    → output/Box.hdf5
✓  input_files/Cone.step   → output/Cone.hdf5
…
Done  ✓10  ✗0
```

All resulting `.hdf5` files appear in `cad_jobs/output/` and logs in `cad_jobs/logs/`.

---

_You’re all set! Enjoy seamless STEP → HDF5 conversions across Linux & Windows._
