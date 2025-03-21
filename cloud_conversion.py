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

if __name__ == "__main__":
    main()

