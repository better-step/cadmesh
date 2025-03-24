
module load python/3.10
cd /home/nafiseh/scratch
source pyoccenv/bin/activate

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/nafiseh/scratch/occt-install/occt781/lib/



cd /home/nafiseh/scratch/CAD/cadmesh
python /home/nafiseh/scratch/CAD/cadmesh/test.py

python home/nafiseh/scratch/CAD/cadmesh/cloud_conversion.py --input "$BATCH_PATH" --output "$OUTPUT_PATH" --log "$LOG_PATH" --batchId "$BATCH_ID" --jobId "$JOB_ID" --hdf5_file "$HDF5_PATH"
