##############################################################################
# ---------- Stage 0: build the Conda environment ---------------------------
FROM condaforge/mambaforge:23.11.0-0 AS builder

# Create the env in /opt/conda/envs/steptohdf5
WORKDIR /opt/conda
COPY environment.yml .
RUN mamba env create -f environment.yml

# Activate the env and install your package with pip
ENV PATH=/opt/conda/envs/steptohdf5/bin:$PATH \
    CONDA_DEFAULT_ENV=steptohdf5
WORKDIR /workspace

# Copy project source *after* the env so code changes trigger only small rebuilds
COPY pyproject.toml .
COPY src ./src
RUN pip install --no-cache-dir .

# ensure Python sees it
ENV PYTHONPATH=/app/src

# run as module
ENTRYPOINT ["python", "-m", "steptohdf5.cloud_conversion"]

##############################################################################
# ---------- Stage 1: slim runtime ------------------------------------------
FROM condaforge/mambaforge:23.11.0-0 AS runtime

# Copy only the ready-made env – nothing else
COPY --from=builder /opt/conda/envs/steptohdf5 /opt/conda/envs/steptohdf5
ENV PATH=/opt/conda/envs/steptohdf5/bin:$PATH \
    CONDA_DEFAULT_ENV=steptohdf5

# Optional: add a non-root user (safer on shared hosts)
RUN useradd -m worker
USER worker

# A neutral workspace users will bind-mount
VOLUME ["/workspace"]
WORKDIR /workspace

# steptohdf5 is already on PATH via the entry-point declared in pyproject.toml
ENTRYPOINT ["steptohdf5"]