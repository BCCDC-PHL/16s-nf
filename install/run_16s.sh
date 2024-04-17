#!/bin/bash
set -e

if [ $# -ne 1 ]; then
    echo "USAGE: bash run_16s.sh [RUN_NAME]"
    exit 0 
fi

INPUT="/mnt/bam/Sanger_Sequencing/16S/2024/inputs/${1}"
OUTPUT="/mnt/bam/Sanger_Sequencing/16S/2024/results/${1}"

mkdir -p ~/work/16s/nf_work/

if [ ! -d $INPUT ]; then 
    echo "ERROR: The input directory you specified does not exist. Double check that the folder exists and that the typed name matches precisely."
    echo $INPUT
    exit 1
elif [ ! -d `dirname $OUTPUT` ]; then 
    echo "ERROR: The output directory does not exist on the netdrive. Please contact a member of the bioinformatics team."
    echo `dirname $OUTPUT`
    exit 1
elif [ -d $OUTPUT ]; then 
    echo "ERROR: A pipeline run with the same name already exists in the outputs. Please change your input folder name and try again."
    echo "$OUTPUT"
    exit 1
elif [ -z "$PIPELINE_VERSION_16S" ]; then 
    echo "ERROR: The pipeline version is not accessible. Something went wrong with the installation. Please contact a member of the bioinformatics team."
    echo "16S Pipeline Version Variable: $PIPELINE_VERSION_16S"
    exit 1
elif [ ! -f ~/work/16s/db/databases.csv ]; then 
    echo "ERROR: The databases.csv is not available. Something went wrong with the installation. Please contact a member of the bioinformatics team."
    exit 1
else
    echo "DETECTED VALID INPUT FOLDER: ${INPUT}" &&
    echo "Starting pipeline run..."
fi

nextflow run BCCDC-PHL/16s-nf \
-r $PIPELINE_VERSION_16S \
-profile conda \
--fasta_input $INPUT \
--outdir $OUTPUT \
--databases ~/work/16s/db/databases.csv \
--taxonkit_db /data/ref_databases/taxonkit/latest \
--cache /scratch/conda_envs/16s/ \
-work-dir ~/work/16s/nf_work/
