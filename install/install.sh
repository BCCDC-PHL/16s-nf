#!/bin/bash

if [ $# -ne 1 ]; then 
	echo "USAGE: bash install.sh [PIPELINE_VERSION]"
	exit 0
fi

PIPELINE_VERSION=$1
DB_NCBI_VERSION="2024-01-16_1.0_16s-ncbi"
DB_ITG_VERSION="2023-12-05_1.0_16s-itgdb"
DB_EZBIO_VERSION="2023-12-12_1.0_16s-ezbio"

cd ~/

# set up necessary nextflow / conda directories 
mkdir -p ~/.nextflow/ 
mkdir -p ~/.conda/envs/
mkdir -p ~/work/16s/results/
mkdir -p ~/work/16s/nf_work/
mkdir -p ~/work/16s/db/ 

# make nextflow config file to link nextflow to Slurm executor
if [ ! -f ~/.nextflow/config ] ; then 
	echo " ------ Setting up Nextflow config... ------ " && 
	echo -e "process {\n executor = 'slurm' \n}" > ~/.nextflow/config 
else
	echo " ------ Nextflow config already set up. Skipping step... ------ "
fi	

# add nextflow to PATH in ~/.bashrc
if [[ ! `grep "/opt/shared/nextflow/bin" ~/.bashrc` ]]; then 
	echo " ------ Adding Nextflow to PATH in bashrc... ------ " && 
	echo -e "export PATH=/opt/shared/nextflow/bin:\$PATH" >> ~/.bashrc
else
	echo " ------ Nextflow already added to .bashrc. Skipping step... ------ "
fi	

# add nextflow / conda executables to path 
if [[ ! `grep "/opt/shared/mambaforge/condabin/" ~/.bashrc` ]]; then 
	echo " ------ Adding mamba to PATH in .bashrc... ------ " && 
	echo -e "export PATH=/opt/shared/mambaforge/condabin/:\$PATH" >> ~/.bashrc &&
	mamba init 
else
	echo " ------ Mamba already added to .bashrc. Skipping step... ------ "
fi	

echo " ------ Setting pipeline version variable ------ " 
if [[ `grep "export PIPELINE_VERSION_16S" ~/.bashrc` ]]; then 
	sed -i '/export PIPELINE_VERSION_16S/d' ~/.bashrc 
fi 
echo -e "export PIPELINE_VERSION_16S=\"${PIPELINE_VERSION}\"" >> ~/.bashrc

source ~/.bashrc


# pull the nextflow pipeline 
echo " ------ Downloading 16S pipeline... ------ " && 
nextflow pull -r ${PIPELINE_VERSION} BCCDC-PHL/16s-nf

# double check that the run_16s.sh script is available
if [ ! -f ~/.nextflow/assets/BCCDC-PHL/16s-nf/install/run_16s.sh ]; then
	echo "ERROR: Could not find the routine analysis script (run_16s.sh) in the 16S pipeline repo. Please contact the bioinformatics team"
	exit 1
fi

# copy run scripts to the user's home directory 
echo " ------ Copying run scripts to home directory ------ " &&
cp ~/.nextflow/assets/BCCDC-PHL/16s-nf/install/run_16s.sh ~/ &&
cp ~/.nextflow/assets/BCCDC-PHL/16s-nf/install/run_16s_flex.sh ~/ &&


echo " ------ Successfully copied pipeline run script to ~/run_16s.sh ------ "

# write the 16s databases.csv file needed for the pipeline
if [ ! -f ~/work/16s/db/databases.csv ]; then 
	echo " ------ Creating databases.csv file ... ------ " &&
	cat <<-EOL > ~/work/16s/db/databases.csv
	ID,DBNAME,DBVERSION,PATH
	ncbi,16s-ncbi,1.0,/data/ref_databases/blast/16S/ncbi/${DB_NCBI_VERSION}/
	itgdb,16s-itgdb,1.0,/data/ref_databases/blast/16S/itgdb/${DB_ITG_VERSION}/
	ezbio,16s-ezbio,1.0,/data/ref_databases/blast/16S/ezbio/${DB_EZBIO_VERSION}/
	EOL
else
	echo " ------ Databases file already exists. Skipping step... ------ "
fi
