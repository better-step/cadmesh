from __future__ import annotations

# ── stdlib ──────────────────────────────────────────────────────────────────
import os
import sys
import tempfile
from pathlib import Path

# ── third-party ────────────────────────────────────────────────────────────
import numpy as np
import h5py
import meshio

# ── steptohdf5 ─────────────────────────────────────────────────────────────────
from ..core.step_processor import StepProcessor



def process_step_file_to_hdf5(
    step_file: str | Path,
    *,
    output_dir: str | Path = ".",
    log_dir: str | Path = "."
) -> Path:
    """
    High-level helper used by the CLI & batch code.
    This function converts a single STEP file to an HDF5 file.

    Parameters
    ----------
    step_file
        Path to a single ``*.step`` / ``*.stp`` file.
    output_dir
        Directory where the final ``<model>.hdf5`` is written.
    log_dir
        Directory where :class:`steptohdf5.core.StepProcessor` will store logs.

    Returns
    -------
    Path
        Full path of the written HDF5 file.
    """
    step_path = Path(step_file).expanduser().resolve()
    out_dir   = Path(output_dir).expanduser().resolve()
    log_dir   = Path(log_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    # ── run extractor ────────────────────────────────────────────────────
    sp = StepProcessor(
        step_file=step_path,
        output_dir=out_dir,
        log_dir=log_dir
    )
    sp.load_step_file()
    sp.process_parts()

    geometry_data  = sp.geometry_data or {}
    topology_data  = sp.topology_data or {}
    statistics_data = sp.stat_data    or {}
    mesh_data = sp.mesh_data or []

    # ── create mesh directory ───────────────────────────────────────────
    # mesh_dir: Path
    # if produce_meshes and sp.mesh_dir and sp.mesh_dir.is_dir():
    #     mesh_dir = sp.mesh_dir
    # else:
    #     # create a *temporary* dir with one minimal OBJ
    #     mesh_dir = out_dir / f"__dummy_mesh__{step_path.stem}"
    #     mesh_dir.mkdir(exist_ok=True)
    #     if not produce_meshes:
    #         _create_minimal_obj(mesh_dir / "dummy.obj")


    h5_path = out_dir / f"{step_path.stem}.hdf5"
    convert_data_to_hdf5(
        geometry_data=geometry_data,
        topology_data=topology_data,
        stat_data=statistics_data,
        mesh_data=mesh_data,
        output_file=str(h5_path),
    )

    return h5_path


def convert_dict_to_hdf5(data, group):
    for key, value in data.items():
        if isinstance(value, dict):
            subgroup = group.create_group(key)
            convert_dict_to_hdf5(value, subgroup)
        elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
            if key == "faces" and all(
                    isinstance(item, dict) and "face_index" in item and "face_orientation_wrt_shell" in item for item in
                    value):
                array_data = np.array([(item['face_index'], item['face_orientation_wrt_shell']) for item in value],
                                      dtype=[('face_index', int), ('face_orientation_wrt_shell', bool)])
                group.create_dataset(key, data=array_data)
            else:
                subgroup = group.create_group(key)
                for i, item in enumerate(value):
                    if key == 'parts':
                        convert_dict_to_hdf5(item, subgroup.create_group('part_' + str(i + 1).zfill(3)))
                    else:
                        convert_dict_to_hdf5(item, subgroup.create_group(str(i).zfill(3)))
        elif isinstance(value, list) and all(isinstance(item, (int, float)) for item in value):
            if key == "bbox" and len(value) == 6:
                array_data = np.array(value).reshape((2, 3))
                group.create_dataset(key, data=array_data)
            elif key == "trim_domain" and len(value) == 4:
                array_data = np.array(value).reshape((2, 2))
                group.create_dataset(key, data=array_data)
            else:
                array_data = np.array(value)
                group.create_dataset(key, data=array_data)
        elif isinstance(value, list):
            if key == "poles" or key == "vertices":
                array_data = np.array(value)
                group.create_dataset(key, data=array_data)
            else:
                subgroup = group.create_group(key)
                for i, item in enumerate(value):
                    subgroup.create_dataset(str(i), data=np.array(item))
        elif isinstance(value, np.ndarray) and value.shape == (3,4):
            array_data = value.astype(np.float64)
            group.create_dataset(key, data=array_data)
        else:
            group.create_dataset(key, data=value)


def convert_stat_to_hdf5(data, group):
    for key, value in data.items():
        if isinstance(value, dict):
            subgroup = group.create_group(key)
            convert_stat_to_hdf5(value, subgroup)
        elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
            subgroup = group.create_group(key)
            for i, item in enumerate(value):
                convert_stat_to_hdf5(item, subgroup.create_group(str(i).zfill(3)))
        elif isinstance(value, list) and all(isinstance(item, (int, float)) for item in value):
            array_data = np.array(value)
            group.create_dataset(key, data=array_data)
        elif isinstance(value, list):
            if key == "parts" and isinstance(value[0], list) and group.name == "/stat":
                subgroup = group.create_group(key)
                for i, inner_list in enumerate(value):
                    subgroup_1 = subgroup.create_group('part_' + str(i + 1).zfill(3))
                    for j, item in enumerate(inner_list):
                        if not item is None:
                            convert_stat_to_hdf5(item, subgroup_1.create_group(str(j).zfill(3)))
            else:
                subgroup = group.create_group(key)
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        convert_stat_to_hdf5(item, subgroup.create_group(str(i).zfill(3)))
                    else:
                        subgroup.create_dataset(str(i), data=np.array(item))
        else:
            group.create_dataset(key, data=value)


def convert_data_to_hdf5(geometry_data, topology_data, stat_data, mesh_data, output_file):
    # if not os.path.isdir(meshPath):
    #     print(f"The provided path '{meshPath}' is not a directory.")
    #     return

    try:
        with h5py.File(output_file, 'w') as hdf:
            geometry_group = hdf.create_group('geometry')
            convert_dict_to_hdf5(geometry_data, geometry_group)

            topology_group = hdf.create_group('topology')
            convert_dict_to_hdf5(topology_data, topology_group)

            stat_group = hdf.create_group('stat')
            convert_stat_to_hdf5(stat_data, stat_group)

            mesh_group = hdf.create_group('mesh')

            for index, mesh_obj in enumerate(mesh_data):
                try:
                    mesh = meshio.Mesh(points=mesh_obj['vertices'], cells=[("triangle", mesh_obj['faces'])])
                    points = mesh.points
                    cells = mesh.cells
                    cell_data = mesh.cell_data
                    mesh_subgroup = mesh_group.create_group(str(index).zfill(3))
                    mesh_subgroup.create_dataset('points', data=points)
                    for cell in cells:
                        cell_type = cell.type
                        cell_indices = cell.data
                        mesh_subgroup.create_dataset(cell_type, data=cell_indices)

                    for data_key, data_value in cell_data.items():
                        if data_key == "obj:group_ids":
                            data_key = "group_ids"
                        if isinstance(data_value, list):
                            mesh_subgroup.create_dataset(data_key, data=data_value)
                        else:
                            subgroup = mesh_subgroup.create_group(data_key)
                            for field_key, field_value in data_value.items():
                                subgroup.create_dataset(field_key, data=field_value)
                except Exception as e:
                         print(f"Error reading mesh object '{mesh_obj}': {e}")

            if mesh_group.keys() == 0:
                print(f"No mesh data found in the object '{mesh_data}'.")
                raise ValueError(f"No mesh data found in the object '{mesh_data}'.")

            # for index, mesh_file in enumerate(
            #         sorted(f for f in os.listdir(meshPath) if os.path.isfile(os.path.join(meshPath, f)))):
            #     if mesh_file.endswith(".obj"):
            #         try:
            #             mesh = meshio.read(os.path.join(meshPath, mesh_file))
            #             points = mesh.points
            #             cells = mesh.cells
            #             cell_data = mesh.cell_data
            #
            #             mesh_subgroup = mesh_group.create_group(str(index).zfill(3))
            #             mesh_subgroup.create_dataset('points', data=points)
            #             for cell in cells:
            #                 cell_type = cell.type
            #                 cell_indices = cell.data
            #                 mesh_subgroup.create_dataset(cell_type, data=cell_indices)
            #
            #             for data_key, data_value in cell_data.items():
            #                 if data_key == "obj:group_ids":
            #                     data_key = "group_ids"
            #                 if isinstance(data_value, list):
            #                     mesh_subgroup.create_dataset(data_key, data=data_value)
            #                 else:
            #                     subgroup = mesh_subgroup.create_group(data_key)
            #                     for field_key, field_value in data_value.items():
            #                         subgroup.create_dataset(field_key, data=field_value)
            #         except Exception as e:
            #             print(f"Error reading mesh file '{mesh_file}': {e}")
            #
            # if mesh_group.keys() == 0:
            #     print(f"No mesh files found in the directory '{meshPath}'.")
            #     raise ValueError(f"No mesh files found in the directory '{meshPath}'.")
    except OSError as e:
        print(f"Error accessing or writing to HDF5 file: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")


