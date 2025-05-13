"""
Batch helpers used by the CLI or importable by end-users.
This module contains functions to convert multiple STEP files in parallel.
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import List, Tuple
import contextlib
import joblib
from joblib import Parallel, delayed
from tqdm.auto import tqdm

from ..converters.hdf5_converter import process_step_file_to_hdf5


# ────────────────────────────────────────────────────────────────────── #
@contextlib.contextmanager
def _tqdm_joblib(bar: "tqdm"):
    class _Callback(joblib.parallel.BatchCompletionCallBack):
        def __call__(self, *args, **kwargs):
            bar.update(self.batch_size)
            return super().__call__(*args, **kwargs)
    old = joblib.parallel.BatchCompletionCallBack
    joblib.parallel.BatchCompletionCallBack = _Callback
    try:
        yield bar
    finally:
        joblib.parallel.BatchCompletionCallBack = old
        bar.close()


# ────────────────────────────────────────────────────────────────────── #
def _worker(sf: Path, out: Path, log: Path):
    try:
        process_step_file_to_hdf5(sf, output_dir=out, log_dir=log)
        return sf, None
    except Exception as exc:           # noqa: BLE001
        return sf, str(exc)


# ───────────────────── public helpers ──────────────────────────────── #
def batch_convert_step_files(
    *,
    input_list_path: Path,
    output_dir: Path,
    log_dir: Path,
    n_jobs: int = 1
) -> Tuple[List[Path], List[Tuple[Path, str]]]:
    """Convert STEP files listed in a text file."""
    files = [Path(line.strip()) for line in input_list_path.read_text().splitlines() if line.strip()]
    return _run_pool(files, output_dir, log_dir, n_jobs)


def folder_convert_step_files(
    *,
    folder: Path,
    pattern: str,
    output_dir: Path,
    log_dir: Path,
    n_jobs: int = 1,
    recursive: bool = True,
) -> Tuple[List[Path], List[Tuple[Path, str]]]:
    """Convert every STEP file inside *folder* matching *pattern*."""
    files = sorted(folder.rglob(pattern) if recursive else folder.glob(pattern))
    return _run_pool(files, output_dir, log_dir, n_jobs)



process_step_files = batch_convert_step_files


# ────────────────────── shared implementation ─────────────────────── #
def _run_pool(files, out_dir, log_dir, n_jobs):
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    ok, fail = [], []
    with _tqdm_joblib(tqdm(total=len(files), desc="Converting", unit="file")):
        results = Parallel(n_jobs=n_jobs, backend="loky")(
            delayed(_worker)(fp, out_dir, log_dir) for fp in files
        )

    for fp, err in results:
        (ok if err is None else fail).append((fp if err is None else (fp, err)))

    # split tuples per contract
    if fail:
        ok_only = [fp for fp in ok]            # ok already plain Paths
        fail_tuples = fail                    # list[(Path, str)]
    else:
        ok_only, fail_tuples = ok, []
    return ok_only, fail_tuples
