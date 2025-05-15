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

    h5_path = out_dir / f"{step_path.stem}.hdf5"
    convert_data_to_hdf5(
        geometry_data=geometry_data,
        topology_data=topology_data,
        stat_data=statistics_data,
        mesh_data=mesh_data,
        output_file=str(h5_path),
        version=sp.version,
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


def convert_data_to_hdf5(geometry_data, topology_data, stat_data, mesh_data, output_file, version: str = "2.0"):
    # if not os.path.isdir(meshPath):
    #     print(f"The provided path '{meshPath}' is not a directory.")
    #     return

    try:
        with h5py.File(output_file, 'w') as hdf:

            parts_group = hdf.create_group("parts")
            parts_group.attrs["version"] = version

            n_parts = len(topology_data.get("parts", []))

            for i in range(n_parts):
                topo = topology_data["parts"][i]
                geo = geometry_data["parts"][i]
                stat = stat_data["parts"][i]
                meshes = mesh_data[i]

                part_grp = parts_group.create_group(f"part_{i + 1:03d}")

                # topology
                topo_grp = part_grp.create_group("topology")
                convert_dict_to_hdf5(topo, topo_grp)

                # geometry
                geo_grp = part_grp.create_group("geometry")
                convert_dict_to_hdf5(geo, geo_grp)

                # statistics
                #stat_grp = part_grp.create_group("stat")
                #convert_stat_to_hdf5(stat, stat_grp)

                # meshes
                mesh_grp = part_grp.create_group("mesh")
                for j, mesh_obj in enumerate(meshes):
                    msub = mesh_grp.create_group(f"{j:03d}")
                    msub.create_dataset(
                        "points",
                        data=mesh_obj["vertices"],
                        compression="gzip",
                        compression_opts=9,
                    )
                    msub.create_dataset(
                        "triangle",
                        data=mesh_obj["faces"],
                        compression="gzip",
                        compression_opts=9,
                    )
    except OSError as e:
        print(f"Error accessing or writing to HDF5 file: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")


