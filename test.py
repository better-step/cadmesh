from src.cadmesh.core.step_processor import StepProcessor
from src.hdf5_converter import *
from pathlib import Path

# for the offset
sf ="/Users/chandu/Workspace/GM/better_step/cadmesh/data/test/BevelGear.stp"
# sf = '/media/nafiseh/my passport/a1.0.0_00/22461_0ba0e480.setp'

output_dir = "/Users/chandu/Workspace/GM/better_step/cadmesh/data/output_dir"
log_dir = "/Users/chandu/Workspace/GM/better_step/cadmesh/data/output_dir"

sp = StepProcessor(Path(sf), Path(output_dir), Path(log_dir))
sp.load_step_file()
sp.process_parts()
