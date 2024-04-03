#!/bin/bash
set -e

PIPELINE_RELEASE="v1.0.2"

cd ~/

# set up necessary nextflow / conda directories 
mkdir -p ~/.nextflow/ 
mkdir -p ~/.conda/envs/
mkdir -p ~/work/16s/results/
mkdir -p ~/work/16s/db/ 

# make nextflow config file to link nextflow to Slurm executor
if [ ! -f ~/.nextflow/config ] ; then 
	echo " ------ Setting up Nextflow config... ------ " && 
	echo -e "process {\n executor = 'slurm' \n}" > ~/.nextflow/config 
else
	echo " ------ Nextflow config already set up. Skipping step... ------ "
fi	

if [[ ! `grep "/opt/shared/nextflow/bin" ~/.bashrc` ]]; then 
	echo " ------ Adding Nextflow to PATH in bashrc... ------ " && 
	echo -e "export PATH=/opt/shared/nextflow/bin:\$PATH" >> ~/.bashrc
else
	echo " ------ Nextflow already added to .bashrc. Skipping step... ------ "
fi	
# add nextflow / conda executables to path 
if [[ ! `grep "/opt/shared/mambaforge/condabin/" ~/.bashrc` ]]; then 
	echo " ------ Adding mamba to PATH in bashrc.. ------ ." && 
	echo -e "export PATH=/opt/shared/mambaforge/condabin/:\$PATH" >> .bashrc &&
	mamba init 
else
	echo " ------ Mamba already added to .bashrc. Skipping step... ------ "
fi	

source ~/.bashrc


# pull the nextflow pipeline 
if [ ! -d ~/.nextflow/assets/BCCDC-PHL/16s-nf ]; then
	echo " ------ Downloading 16S pipeline... ------ " && 
	nextflow pull -r ${PIPELINE_RELEASE} BCCDC-PHL/16s-nf
else
	echo " ------ 16S pipeline already downloaded. Skipping step... ------ "
fi	

if [ ! -f ~/.nextflow/assets/BCCDC-PHL/16s-nf/install/run_16s.sh ]; then
	echo "ERROR: Could not find the routine analysis script (run_16s.sh) in the 16S pipeline repo."
	exit 1
fi

echo " ------ Copying run scripts to home directory ------ " &&
cp ~/.nextflow/assets/BCCDC-PHL/16s-nf/install/run_16s.sh ~/ &&
cp ~/.nextflow/assets/BCCDC-PHL/16s-nf/install/run_16s_flex.sh ~/ &&


echo " ------ Successfully copied pipeline run script to ~/run_16s.sh ------ "

if [ ! -f ~/work/16s/db/databases.csv ]; then 
	echo " ------ Creating databases.csv file ... ------ " &&
	cat <<-EOL > ~/work/16s/db/databases.csv
	ID,DBNAME,DBVERSION,PATH
	ncbi,16s-ncbi,1.0,/data/ref_databases/blast/16S/ncbi/2024-01-16_1.0_16s-ncbi/
	itgdb,16s-itgdb,1.0,/data/ref_databases/blast/16S/itgdb/2023-12-05_1.0_16s-itgdb/
	ezbio,16s-ezbio,1.0,/data/ref_databases/blast/16S/ezbio/2023-12-12_1.0_16s-ezbio/
	EOL
else
	echo " ------ Databases file already exists. Skipping step... ------ "
fi
