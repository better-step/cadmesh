from core.step_processor import StepProcessor
from pathlib import Path


sf ="/Users/nafiseh/Documents/GitHub/cadmesh/data/cad/00000048_efe12a13ac2e4ea7880a66d1_step_000.step"
output_dir = "/Users/nafiseh/Documents/GitHub/cadmesh/data/cad"
log_dir = "/Users/nafiseh/Documents/GitHub/cadmesh/data/cad/logs"

sp = StepProcessor(sf, Path(output_dir), Path(log_dir))