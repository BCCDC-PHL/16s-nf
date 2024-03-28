#!/bin/bash
set -e

if [ $# -ne 1 ]; then
    echo "USAGE: bash run_16s.sh [RUN_NAME]"
    exit 0 
fi

RELEASE="v1.0.2"
INPUT="/mnt/genomics/16s/2024/inputs/${1}"
OUTPUT="/mnt/genomics/16s/2024/results/${1}"

if [ ! -d "$INPUT" ]; then 
    echo "ERROR: The input directory you specified does not exist. Check your path carefully."
    exit 1
elif [ ! -d "/mnt/genomics/16s/2024/results/" ]; then 
    echo "ERROR: The synchronization point on the netdrive does not exist. Please contact a member of the bioinformatics team."
    exit 1
elif [ -d "$OUTPUT" ]; then 
    echo "ERROR: A pipeline run with the same name already exists in the outputs. Please change your input folder name and try again. "
    exit 1
else
    echo "DETECTED VALID INPUT FOLDER: ${INPUT}" &&
    echo "Starting pipeline run..."
fi

nextflow run BCCDC-PHL/16s-nf -r $RELEASE -profile conda \
--fasta_input $INPUT \
--outdir $OUTPUT \
--databases ~/work/16s/db/databases.csv \
--taxonkit_db /data/ref_databases/taxonkit/latest \
--cache /scratch/conda_envs/16s/
