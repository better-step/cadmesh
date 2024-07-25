import sys
import glob
import os
import time
import random

# Get the task id, directory, file pattern, and processed files list path as command line arguments
task_id = int(sys.argv[1])
directory = sys.argv[2]
pattern = sys.argv[3]
processed_files_path = sys.argv[4]

# Get all files matching the pattern
all_files = sorted(glob.glob(f"{directory}/{pattern}"))

print(f"Found {len(all_files)} files matching the pattern in the directory.", file=sys.stderr)  # Debug line

# The path of the lock file
lock_file = f"{directory}/lock_file"

while True:
    # Check if the lock file exists
    if not os.path.isfile(lock_file):
        # Create the lock file
        open(lock_file, 'w').close()

        # Read already processed files
        if os.path.isfile(processed_files_path):
            with open(processed_files_path, 'r') as f:
                processed_files = f.read().splitlines()
        else:
            processed_files = []

        print(f"Found {len(processed_files)} already processed files.", file=sys.stderr)  # Debug line

        # Get the list of unassigned files
        unassigned_files = list(set(all_files) - set(processed_files))

        print(f"Found {len(unassigned_files)} unassigned files.", file=sys.stderr)  # Debug line

        # Select 500 or fewer files for this task
        files_to_process = unassigned_files[:500]

        # Update the list of processed files
        processed_files.extend(files_to_process)
        with open(processed_files_path, 'w') as f:
            for item in processed_files:
                f.write("%s\n" % item)

        # Delete the lock file
        os.remove(lock_file)

        # Print the files to standard output, one per line
        for file in files_to_process:
            print(file)

        # Break the loop
        break

    # Sleep for a random amount of time (e.g., between 1 and 10 seconds) before trying again
    time.sleep(random.randint(1, 10))
