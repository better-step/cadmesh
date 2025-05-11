# src/cadmesh/core/step_processor.py
"""
StepProcessor
=============

A thin orchestration layer that:

1.  *loads* a STEP (ISO-10303) file with Open Cascade,
2.  optionally heals / converts the geometry,
3.  delegates to helper builders to extract
    • topology   • geometry   • statistics   • surface meshes,
4.  stores those results in public attributes so that callers
   (CLI / batch / notebook) can do whatever they like with them
   – for instance, write them to HDF5 via
   :pyfunc:`cadmesh.converters.hdf5_converter.process_step_file_to_hdf5`.

Nothing in here touches HDF5, YAML, or the filesystem except
temporary OBJ meshes when a *MeshBuilder* is used.

Public attributes *after* :py:meth:`process_parts` runs
-------------------------------------------------------

``self.geometry_data``   nested ``dict`` built by *GeometryDictBuilder*  
``self.topology_data``   nested ``dict`` built by *TopologyDictBuilder*  
``self.stat_data``       nested ``dict`` from *extract_statistical_information*  
``self.mesh_data``       list of *MeshBuilder* meshes (if used)
``self.parts``           list of *STEPControl_Reader* parts (raw OCC objects)

"""

from __future__ import annotations

# --- stdlib ----------------------------------------------------------------
import logging
import os
from pathlib import Path
from typing import Sequence

# --- third-party -----------------------------------------------------------
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.ShapeFix import ShapeFix_Shape
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
import igl  # used by MeshBuilder

# --- package ----------------------------------------------------------------
from src.cadmesh.core.entity_mapper import EntityMapper
from src.cadmesh.core.geometry_dict_builder import GeometryDictBuilder
from src.cadmesh.core.topology_dict_builder import TopologyDictBuilder
from src.cadmesh.core.statistics_dict_builder import extract_statistical_information
from src.cadmesh.mesh.mesh_builder import MeshBuilder
from src.cadmesh.utils.geometry import load_parts_from_step_file
from src.cadmesh.utils.logging import setup_logger


# --------------------------------------------------------------------------- #
class StepProcessor:
    """
    A *single* STEP file processor.

    Parameters
    ----------
    step_file
        Path to ``*.step`` / ``*.stp`` file.
    output_dir
        Where temporary surface meshes (OBJ) will be written
        **if** ``mesh_builder`` is not ``None``.
    log_dir
        Per-file log output.
    mesh_builder
        ``None``  ⇒ *no* surface meshes are created.
        *class*   ⇒ an instance is constructed and used.
    """

    # ------------------------------------------------------------------ #
    def __init__(
            self,
            step_file: str | Path,
            output_dir: str | Path,
            log_dir: str | Path,
            *,
            entity_mapper=EntityMapper,
            topology_builder=TopologyDictBuilder,
            geometry_builder=GeometryDictBuilder,
            mesh_builder=MeshBuilder,
            stats_builder=extract_statistical_information,
    ):
        self.step_file = Path(step_file).expanduser().absolute()
        self.output_dir = Path(output_dir).expanduser().absolute()
        self.log_dir = Path(log_dir).expanduser().absolute()

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # log file named after model
        log_path = self.log_dir / f"{self.step_file.stem}.log"
        self.logger = setup_logger(self.step_file.stem, log_path)

        # builder classes
        self.entity_mapper_cls = entity_mapper
        self.topology_builder_cls = topology_builder
        self.geometry_builder_cls = geometry_builder
        self.mesh_builder_cls = mesh_builder
        self.stats_builder_fn = stats_builder

        # placeholders for results
        self.parts: Sequence = []
        self.geometry_data: dict | None = None
        self.topology_data: dict | None = None
        self.stat_data: dict | None = None
        self.mesh_data: list | None = None

    #  self.mesh_dir: Path | None       = None

    # ------------------------------------------------------------------ #
    #  STEP I/O
    # ------------------------------------------------------------------ #
    def load_step_file(self) -> None:
        """Read the STEP file and populate :pyattr:`parts` with solids."""
        self.logger.info("Reading STEP file %s", self.step_file.name)
        self.parts = load_parts_from_step_file(self.step_file, logger=self.logger)
        self.logger.info("Found %d part(s)", len(self.parts))

    # ------------------------------------------------------------------ #
    #  Top-level public workflow
    # ------------------------------------------------------------------ #
    def process_parts(
            self,
            *,
            convert_to_nurbs: bool = False,
            heal_shape: bool = False,
            mesh_deflection_rel: float = 1e-3,
            indices: Sequence[int] | None = None,
    ):
        """
        Extract topology/geometry/stats/(optional)meshes for all or a slice of parts.

        Parameters
        ----------
        convert_to_nurbs
            If ``True`` every shape is run through
            :class:`OCC.Core.BRepBuilderAPI.BRepBuilderAPI_NurbsConvert`.
        heal_shape
            If ``True`` run OCC *ShapeFix_Shape* healing before extraction.
        mesh_deflection_rel
            Relative deflection used by *MeshBuilder* (ignored if meshes disabled).
        indices
            Optional list/tuple of *part indices* to process (default = all).
        """

        if not self.parts:
            raise RuntimeError("Call load_step_file() first")

        to_process = range(len(self.parts)) if indices is None else indices

        topo, geo, stats, mesh_objs = [], [], [], []

        # --- iterate parts -------------------------------------------------- #
        for idx in to_process:
            part = self.parts[idx]
            self.logger.info("Processing part %d/%d", idx + 1, len(self.parts))

            # optional NURBS conversion
            if convert_to_nurbs:
                try:
                    part = BRepBuilderAPI_NurbsConvert(part).Shape()
                except Exception as exc:
                    self.logger.warning("NURBS conversion failed: %s", exc)

            # optional healing
            if heal_shape:
                shfix = ShapeFix_Shape(part)
                shfix.Perform()
                part = shfix.Shape()

            # run extraction pipeline for *one* part
            t, g, s, m = self._process_part(part, mesh_deflection_rel)
            topo.append(t)
            geo.append(g)
            stats.append(s)
            mesh_objs.extend(m)

        # ------------------------------------------------------------------ #
        #  store results in public attrs
        # ------------------------------------------------------------------ #
        self.topology_data = {"parts": topo, "version": "2.0"}
        self.geometry_data = {"parts": geo, "version": "2.0"}
        self.stat_data = {"parts": stats, "version": "2.0"}
        self.mesh_data = mesh_objs

        self.logger.info("Extraction complete")

    # ------------------------------------------------------------------ #
    #  Internal helper – one part
    # ------------------------------------------------------------------ #
    def _process_part(self, part, mesh_deflection_rel: float):
        """
        Return topology_dict, geometry_dict, stats_dict, [mesh_paths]
        """
        # Entity map
        entity_mapper = self.entity_mapper_cls([part])

        # Topology
        topo_builder = self.topology_builder_cls(entity_mapper)
        topo_dict = topo_builder.build_dict_for_parts(part)

        # Geometry
        geo_builder = self.geometry_builder_cls(entity_mapper)
        geo_dict = geo_builder.build_dict_for_parts(part, self.logger)

        # Stats
        stats_dict = self.stats_builder_fn(part, entity_mapper, self.logger)

        # Meshes
        if self.mesh_builder_cls is not None:
            bbox = geo_dict.get("bbox", None)
            if bbox:
                length = max(bbox[3] - bbox[0],
                             bbox[4] - bbox[1],
                             bbox[5] - bbox[2]) * mesh_deflection_rel
            else:
                length = mesh_deflection_rel

            m_builder = self.mesh_builder_cls(entity_mapper, self.logger)
            # returns list of {vertices, faces}
            meshes = m_builder.create_surface_meshes(part, length)

        return topo_dict, geo_dict, stats_dict, meshes
