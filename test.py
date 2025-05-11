from src.cadmesh import convert_step
from pathlib import Path

# for the offset
sf ="/Users/chandu/Workspace/GM/better_step/cadmesh/data/test/BevelGear.stp"

output_dir = "/Users/chandu/Workspace/GM/better_step/cadmesh/data/output_dir"
log_dir = "/Users/chandu/Workspace/GM/better_step/cadmesh/data/output_dir"

convert_step(Path(sf), output_dir=Path(output_dir), log_dir=Path(log_dir))



# from src.cadmesh.utils.processing import batch_convert_step_files
# from pathlib import Path
#
# sf ="/Users/chandu/Workspace/GM/better_step/cadmesh/models.txt"
# output_dir = "/Users/chandu/Workspace/GM/better_step/cadmesh/data/output_dir"
# log_dir = "/Users/chandu/Workspace/GM/better_step/cadmesh/data/output_dir"
#
#
# ok, failed = batch_convert_step_files(
#     input_list_path=Path(sf),
#     output_dir=Path(output_dir),
#     log_dir=Path(log_dir),
#     n_jobs=8,
#     produce_meshes=False,     # skip meshes
# )
# print(f"{len(ok)} ok, {len(failed)} failed")