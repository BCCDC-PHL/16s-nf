#!/bin/bash
set -e

if [ $# -ne 2 ]; then
    echo "USAGE: bash run_16s.sh [INPUT_PATH] [OUTPUT_PATH]"
    exit 0 
fi

INPUT=$1
OUTPUT=$2
RELEASE="v1.0.2"

if [ ! -d "$INPUT" ]; then 
    echo "ERROR: The input directory you specified does not exist. Check your path carefully."
    exit 1
fi 

nextflow run BCCDC-PHL/16s-nf -r $RELEASE -profile conda \
--fasta_input $INPUT \
--outdir $OUTPUT \
--databases ~/work/16s/db/databases.csv \
--taxonkit_db /data/ref_databases/taxonkit/latest \
--cache /scratch/conda_envs/16s/
