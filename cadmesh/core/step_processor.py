from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Extend.TopologyUtils import TopologyExplorer, WireExplorer
from OCCUtils.Topology import Topo, dumpTopology
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCC.Core.BRep import BRep_Tool
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Pnt2d
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
from OCC.Core.BRepTools import breptools_UVBounds
from OCC.Core.ShapeFix import ShapeFix_Shape as _ShapeFix_Shape
import os
import igl
from pathlib import Path
import logging
import h5py
from Hda5_Converter import *



from .entity_mapper import EntityMapper
from .geometry_dict_builder import GeometryDictBuilder
from .topology_dict_builder import TopologyDictBuilder
from .statistics_dict_builder import extract_statistical_information
from ..mesh.mesh_builder import MeshBuilder
from ..utils.geometry import load_parts_from_step_file, write_dictionary_to_file
from ..utils.my_logging import setup_logger

class StepProcessor:
    """
    Processor class for step files. Takes as input a step file, an entity_mapper, a topology and geometry dict builder and a mesh processor.
    """
    def __init__(self, step_file, output_dir, log_dir, entity_mapper=EntityMapper, topology_builder=TopologyDictBuilder, geometry_builder=GeometryDictBuilder, mesh_builder=MeshBuilder, stats_builder=None):
        """
        Create the processor, initialize the logger
        """
        self.step_file = step_file
        self.entity_mapper = entity_mapper
        self.topology_builder = topology_builder
        self.geometry_builder = geometry_builder
        self.mesh_builder = mesh_builder
        self.stats_builder = stats_builder
        
        self.data_format = "yaml"
        
        self.extract_geometry = self.geometry_builder != None
        self.extract_meshes = self.mesh_builder != None
        self.extract_stats = self.stats_builder != None
        self.extract_topo = self.topology_builder != None
        
        # Initialize the parts list
        self.parts = []
        
        # Directory for output files
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # Create logdir
        self.log_dir = log_dir #output_dir.stem.replace("results", "log")
        os.makedirs(self.log_dir, exist_ok=True)
        
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        %log_file_name = step_file.stem
        if step_file.stem == 'assembly':
            log_file_name = step_file.parent.name + '_' + step_file.stem
        else:
            log_file_name = step_file.stem
        logger = setup_logger('%s_logger'%step_file.stem, os.path.join(log_dir, '%s.log'%log_file_name), formatter)
        logger.info("Init step processing: %s"%step_file.stem)
        self.logger = logger


    def load_step_file(self):
        self.parts = load_parts_from_step_file(self.step_file, logger=self.logger)

    def process_parts(self, convert=False, fix=False, write_face_obj=True, write_part_obj=True, indices=[], version="2.01"):
        if len(self.parts) == 0:
            self.logger.info("No parts loaded to process.")
            return
        
        # If no indices are given, process all parts
        if len(indices) == 0:
            indices = range(len(self.parts))
            self.logger.info("Processing all %i parts of file."%len(indices))
        
        topo_dicts = []
        geo_dicts = []
        mesh_dicts = []
        stats_dicts = []
        
        # Iterate over all indices
        for index in indices:
            part = self.parts[index]
            
            # Convert complete part to NURBS surfaces
            if convert:
                try:
                    nurbs_converter = BRepBuilderAPI_NurbsConvert(part)
                    nurbs_converter.Perform(part)
                    part = nurbs_converter.Shape()
                except Exception as e:
                    #print("Conversion failed, processing unconverted")
                    #print(e.args.split("\n"))
                    self.logger.error("Nurbs conversion error: %s"%"".join(str(e).split("\n")[:2]))
                    continue
            
            # Fix shape with healing operations
            if fix:
                #print("Fixing shape")
                b = _ShapeFix_Shape(part)
                b.SetPrecision(1e-8)
                #b.SetMaxTolerance(1e-8)
                #b.SetMinTolerance(1e-8)
                b.Perform()
                part = b.Shape()
        
            # Extract information for part
            try:
                topo_dict, geo_dict, meshes, stats_dict = self.__process_part(part)
            except Exception as e:
                print("Error:", str(e))
                self.logger.error("Processing part failed %i"%index)
                self.logger.error(str(e))
                continue
            
            topo_dicts.append(topo_dict)
            geo_dicts.append(geo_dict)
            stats_dicts.append(stats_dict)

            # if write_face_obj:
            #     mesh_path = self.output_dir / f"{self.step_file.stem}_mesh"
            #     #print(str(mesh_path), mesh_path)
            #     os.makedirs(mesh_path, exist_ok=True)
            #     for idx, mesh in enumerate(meshes):
            #         if len(mesh["vertices"]) > 0:
            #             igl.write_triangle_mesh("%s/%03i_%05i_mesh.obj"%(str(mesh_path), index, idx), mesh["vertices"], mesh["faces"])

        parent_folder_name = self.step_file.parent.name
        grandparent_folder_name = self.step_file.parent.parent.name

        new_folder_path = self.output_dir / grandparent_folder_name/parent_folder_name
        new_folder_path.mkdir(parents=True, exist_ok=True)
        hdf5_path = self.output_dir / grandparent_folder_name / parent_folder_name / f"{self.step_file.stem}.hdf5"


        # if self.step_file.stem == 'assembly':
        #     new_file_name = f"{self.step_file.parent.name}_{self.step_file.stem}.hdf5"
        #     hdf5_path = os.path.join(self.output_dir, new_file_name)
        # else:
        #     hdf5_path = self.output_dir / f"{self.step_file.stem}.hdf5"

        # self.logger.info("Writing dictionaries")
        # topo_yaml = self.output_dir / f"{self.step_file.stem}_topo"
        # write_dictionary_to_file(topo_yaml, {"parts": topo_dicts, "version": version}, self.data_format)
        # self.logger.info("Topo dict: Done")
        # geo_yaml = self.output_dir / f"{self.step_file.stem}_geo"
        # write_dictionary_to_file(geo_yaml, {"parts": geo_dicts, "version": version}, self.data_format)
        # self.logger.info("Geo dict: Done")
        # stats_yaml = self.output_dir / f"{self.step_file.stem}_stat"
        # write_dictionary_to_file(stats_yaml, {"parts": stats_dicts, "version": version}, self.data_format)
        # self.logger.info("Stat dict: Done")

        with h5py.File(hdf5_path, "w") as hdf5_file:

            convert_dict_to_hdf5({"parts": topo_dicts, "version": version},
                                 hdf5_file.create_group("topology"))
            convert_dict_to_hdf5({"parts": geo_dicts, "version": version},
                                 hdf5_file.create_group("geometry"))
            convert_stat_to_hdf5({"parts": stats_dicts, "version": version},
                                 hdf5_file.create_group("stat"))

            mesh_group = hdf5_file.create_group('mesh')

            for index, mesh in enumerate(meshes):
                points = mesh["vertices"]
                faces = mesh["faces"]
                mesh_subgroup = mesh_group.create_group(str(index).zfill(3))
                # mesh_subgroup.create_dataset('points', data=points)
                # mesh_subgroup.create_dataset('triangle', data=faces)
                mesh_subgroup.create_dataset('points', data=points, compression="gzip", compression_opts=9)
                mesh_subgroup.create_dataset('triangle', data=faces, compression="gzip", compression_opts=9)
                # group_ids = np.full((faces.shape[0],), -1, dtype=int)
                # mesh_subgroup.create_dataset("group_ids", data=group_ids)



            
    def __process_part(self, part):
        self.logger.info("Entity mapper: Init")
        entity_mapper = self.entity_mapper([part])
        self.logger.info("Entity mapper: Done")

        # Extract topology
        if self.extract_topo:
            self.logger.info("Extract topo: Init")
            topo_dict_builder = self.topology_builder(entity_mapper)
            self.logger.info("Extract topo: Build")
            topo_dict = topo_dict_builder.build_dict_for_parts(part)
            self.logger.info("Extract topo: Done")
        else:
            topo_dict = {}

        # Extract geometry
        if self.extract_geometry:
            self.logger.info("Extract geo: Init")
            geo_dict_builder = self.geometry_builder(entity_mapper)
            self.logger.info("Extract geo: Build")
            geo_dict = geo_dict_builder.build_dict_for_parts(part, self.logger)
            self.logger.info("Extract geo: Done")
        else:
            geo_dict = {}

        # Extract statistics
        if True:#self.extract_stats:
            self.logger.info("Extract stats: Init")
            stats_dict = extract_statistical_information(part, entity_mapper, self.logger)
            self.logger.info("Extract stats: Done")
        else:
            stats_dict = {}

        # Extract meshes
        if self.extract_meshes:
            lenght = 0.1
            if geo_dict and 'bbox' in geo_dict:
                bbox = geo_dict['bbox']
                lenght = max(bbox[3] - bbox[0], bbox[4] - bbox[1], bbox[5] - bbox[2]) * 0.1

            self.logger.info("Extract mesh: Init")
            mesh_builder = self.mesh_builder(entity_mapper, self.logger)
            meshes = mesh_builder.create_surface_meshes(part, lenght)
            self.logger.info("Extract mesh: Done")
        else:
            meshes = []

        return topo_dict, geo_dict, meshes, stats_dict
