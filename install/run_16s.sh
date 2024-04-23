#!/bin/bash

if [ $# -ne 1 ]; then
    echo "USAGE: bash run_16s.sh [RUN_NAME]"
    exit 0 
fi

INPUT="/mnt/bam/Sanger_Sequencing/16S/2024/inputs/${1}"
OUTPUT="/mnt/bam/Sanger_Sequencing/16S/2024/results/${1}"
TAXONKIT_DB="/data/ref_databases/taxonkit/latest"
CONDA_CACHE="/scratch/conda_envs/16s/"
DATABASES_CSV=~/work/16s/db/databases.csv
RUN_NAME="$1"

mkdir -p ~/work/16s/nf_work/

# check for missing input directory
if [ ! -d $INPUT ]; then 
    echo "ERROR: The input directory you specified does not exist. Double check that the folder exists and that the typed name matches precisely."
    echo $INPUT
    exit 1
# check for missing output directory
elif [ ! -d `dirname $OUTPUT` ]; then 
    echo "ERROR: The output directory does not exist on the netdrive. Please contact a member of the bioinformatics team."
    echo `dirname $OUTPUT`
    exit 1
# check for existing run folder with identical name (prevents overwrite)
elif [ -d $OUTPUT ]; then 
    echo "ERROR: A pipeline run with the same name already exists in the outputs. Please change your input folder name and try again."
    echo "$OUTPUT"
    exit 1
# checks for missing PIPELINE_VERSION_16S variable
elif [ -z "$PIPELINE_VERSION_16S" ]; then 
    echo "ERROR: The pipeline version is not accessible. Something went wrong with the installation. Please contact a member of the bioinformatics team."
    echo "16S Pipeline Version Variable: $PIPELINE_VERSION_16S"
    exit 1
# checks for missing databases.csv file needed for pipeline 
elif [ ! -f ${DATABASES_CSV} ]; then 
    echo "ERROR: The databases.csv is not available. Something went wrong with the installation. Please contact a member of the bioinformatics team."
    exit 1
else
    echo "DETECTED VALID INPUT FOLDER: ${INPUT}" &&
    echo "Starting 16S Pipeline Version ${PIPELINE_VERSION_16S}..."
fi

nextflow run BCCDC-PHL/16s-nf \
-r $PIPELINE_VERSION_16S \
-profile conda \
--fasta_input $INPUT \
--outdir $OUTPUT \
--run_name $RUN_NAME \
--databases ${DATABASES_CSV} \
--taxonkit_db $TAXONKIT_DB \
--cache $CONDA_CACHE \
-work-dir ~/work/16s/nf_work/
