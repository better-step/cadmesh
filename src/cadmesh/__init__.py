
"""
Tiny public façade for CADMesh-HDF5.

Examples
--------
from cadmesh import convert_step
convert_step("Gear.step", output_dir="out", log_dir="logs")


PosixPath('out/Gear.h5')

"""
from pathlib import Path
from .converters.hdf5_converter import process_step_file_to_hdf5

def convert_step(step_file, *, output_dir=".", log_dir=".", meshes=True):
    """
    Convert a single STEP file to HDF5 and return the Path of the .hdf5 output.
    """
    return process_step_file_to_hdf5(
        Path(step_file),
        output_dir=Path(output_dir),
        log_dir=Path(log_dir)
    )
