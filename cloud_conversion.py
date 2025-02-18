import os
import cadmesh
import OCCUtils
import argparse
from Hda5_Converter import *
from pathlib import Path
import os
import glob
import shutil
import tempfile
import multiprocessing
import subprocess
from tqdm import tqdm
from memory_profiler import profile

def process_files(success_files, models_folder, output_folder, batch_id, job_id):
    successful_conversions = []
    failed_conversions = []
    input_folder = Path(models_folder)
    output_folder_path = Path(output_folder)

    for item in tqdm(success_files):
        try:
            output_folder_path.mkdir(parents=True, exist_ok=True)
            model_name = item.stem

            meshPath = input_folder / f"{model_name}_mesh"
            geometry_yaml_file_path = input_folder / f"{model_name}_geo.yaml"
            topology_yaml_file_path = input_folder / f"{model_name}_topo.yaml"
            stat_yaml_file_path = input_folder / f"{model_name}_stat.yaml"
            output_file = output_folder_path / f'{model_name}.sample_hdf5'

            assert meshPath.exists()
            assert geometry_yaml_file_path.exists()
            assert topology_yaml_file_path.exists()
            assert stat_yaml_file_path.exists()

            geometry_data = load_dict_from_yaml(geometry_yaml_file_path)
            topology_data = load_dict_from_yaml(topology_yaml_file_path)
            stat_data = load_dict_from_yaml(stat_yaml_file_path)

            convert_data_to_hdf5(geometry_data, topology_data, stat_data, meshPath, output_file)

            successful_conversions.append(model_name)

            # delete files on success
            for file in [item, meshPath, geometry_yaml_file_path, topology_yaml_file_path, stat_yaml_file_path]:
                try:
                    if file.exists():
                        if file.is_dir():
                            shutil.rmtree(str(file))  # for directories
                        else:
                            os.remove(str(file))  # for files
                except OSError as e:
                    print(f"Error: {file} : {e.strerror}")

        except Exception as e:
            print(f"Conversion failed for model {model_name}. Error: {e}")
            failed_conversions.append(model_name)

    with open(f'successful_conversions_{job_id}_{batch_id}.txt', 'w') as f:
        for item in successful_conversions:
            f.write("%s\n" % item)

    with open(f'failed_conversions_{job_id}_{batch_id}.txt', 'w') as f:
        for item in failed_conversions:
            f.write("%s\n" % item)

    if len(failed_conversions) > 0:
        print(f"Some files failed conversion. Check 'failed_conversions_{job_id}_{batch_id}.txt' for details.")
        exit(1)
    else:
        print(f"All files successfully converted. Check 'successful_conversions_{job_id}_{batch_id}.txt' for details.")
        try:
            if input_folder.exists():
                shutil.rmtree(str(input_folder))  # Delete the models folder
        except OSError as e:
            print(f"Error: {input_folder} : {e.strerror}")
        exit(0)



def main():
        parser = argparse.ArgumentParser(description="Process STEP files in a directory.")
        parser.add_argument("--input", help="Path to the text file with the list of STEP files.")
        parser.add_argument("--output", help="Path to the directory where results will be saved.")
        parser.add_argument("--log", help="Path to the directory where logs will be saved.")
        parser.add_argument("--hdf5_file", help="Path to the HDF5 file where results will be saved.")
        # parser.add_argument("--jobId", help="Job ID for this execution")
        # parser.add_argument("--batchId", help="Batch ID for this execution")
        args = parser.parse_args()

        success, failed = cadmesh.utils.processing.process_step_files(args.input, args.output, args.log)
        print(f"Successful conversions: {success}")
        print(f"Failed conversions: {failed}")

        with open(args.output + 'success.txt', 'w') as f:
            for item in success:
                f.write(str(item) + "\n")

        with open(args.output + 'failed.txt', 'w') as f:
            for item in failed:
                f.write(str(item) + "\n")
        # process_files(success, args.output, args.hdf5_file, args.batchId, args.jobId)

if __name__ == "__main__":
    main()


# find $(pwd) -type f -name "*.step" >> ~/cadmesh/files.txt
#  python cloud_conversion.py --input files.txt --output /media/nafiseh/5f43a9e1-ea28-46ea-ab14-42040d28983d/data/steps/output/ --log /media/nafiseh/5f43a9e1-ea28-46ea-ab14-42040d28983d/data/steps/log/ --hdf5_file /media/nafiseh/5f43a9e1-ea28-46ea-ab14-42040d28983d/data/steps/hdf5/