# src/cadmesh/cli.py
from __future__ import annotations
import argparse
from pathlib import Path
from cadmesh import convert_step
from cadmesh.utils.processing import batch_convert_step_files


def build_parser():
    p = argparse.ArgumentParser(
        prog="cadmesh-hdf5",
        description="Convert STEP → HDF5 (single file or batch list)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "step_file",
        nargs="?",
        help="A single *.step / *.stp file to convert "
             "(omit when using --list).",
    )
    p.add_argument(
        "--list", "-i",
        metavar="LIST.TXT",
        help="Text file with many STEP paths (one per line).",
    )
    p.add_argument(
        "-o", "--output", required=True, metavar="DIR",
        help="Directory for HDF5 output.",
    )
    p.add_argument(
        "-l", "--log", required=True, metavar="DIR",
        help="Directory for log files.",
    )
    p.add_argument(
        "-j", "--jobs", type=int, default=1, metavar="N",
        help="Parallel workers when using --list.",
    )
    p.add_argument(
        "--no-mesh", action="store_true",
        help="Skip surface-mesh extraction (faster/smaller).",
    )
    return p


def main():
    args = build_parser().parse_args()

    out_dir = Path(args.output).expanduser().absolute()
    log_dir = Path(args.log).expanduser().absolute()
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    #  SINGLE-FILE MODE
    # ------------------------------------------------------------------ #
    if args.step_file and not args.list:
        h5 = convert_step(
            args.step_file,
            output_dir=out_dir,
            log_dir=log_dir,
            meshes=not args.no_mesh,
        )
        print(f"✓  {h5}")
        return

    # ------------------------------------------------------------------ #
    #  BATCH MODE  (--list ...)
    # ------------------------------------------------------------------ #
    if not args.list:
        raise SystemExit("Error: supply either a STEP file or --list")

    ok, failed = batch_convert_step_files(
        input_list_path=Path(args.list),
        output_dir=out_dir,
        log_dir=log_dir,
        n_jobs=args.jobs,
        produce_meshes=not args.no_mesh,
    )

    print(f"\nDone  ✓{len(ok)}  ✗{len(failed)}")
    if failed:
        print("Failures:")
        for fp, err in failed:
            print(f"  {fp}  –  {err}")
