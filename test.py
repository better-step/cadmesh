from cadmesh.core.step_processor import StepProcessor
from Hda5_Converter import *
from pathlib import Path

# for the offset
sf ="/media/nafiseh/5f43a9e1-ea28-46ea-ab14-42040d28983d/data/abc_check/retrieve (2)/00043667/00043667_331051c2d5f94876bc6e56b8_step_000.step"
# sf = '/media/nafiseh/my passport/a1.0.0_00/22461_0ba0e480.setp'

output_dir = "/home/nafiseh/Desktop/output/"
log_dir = "/home/nafiseh/Desktop/log/"

sp = StepProcessor(Path(sf), Path(output_dir), Path(log_dir))
sp.load_step_file()
sp.process_parts()
