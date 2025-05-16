import os
from utils.processing import process_step_files
import argparse



def main():
        parser = argparse.ArgumentParser(description="Process STEP files in a directory.")
        parser.add_argument("--input", help="Path to the text file with the list of STEP files.")
        parser.add_argument("--output", help="Path to the directory where results will be saved.")
        parser.add_argument("--log", help="Path to the directory where logs will be saved.")
        parser.add_argument("--hdf5_file", help="Path to the HDF5 file where results will be saved.")
        args = parser.parse_args()

        success, failed = process_step_files(args.input, args.output, args.log)
        print(f"Successful conversions: {success}")
        print(f"Failed conversions: {failed}")

        with open(args.input + 'success.txt', 'w') as f:
            for item in success:
                f.write(str(item) + "\n")

        with open(args.input + 'failed.txt', 'w') as f:
            for item in failed:
                f.write(str(item) + "\n")

if __name__ == "__main__":
    main()

