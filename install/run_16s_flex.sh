#!/bin/bash
set -e

if [ $# -ne 3 ]; then
    echo "USAGE: bash run_16s_flex.sh [RELEASE] [INPUT_PATH] [OUTPUT_PATH]"
    exit 0 
fi

RELEASE=$1
INPUT=$2
OUTPUT=$3

if [ ! -d "$INPUT" ]; then 
    echo "ERROR: The input directory you specified does not exist. Check your path carefully."
    exit 1
elif [ -d "$OUTPUT" ]; then 
    echo "ERROR: This output directory already exists. Please choose a different output path"
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
