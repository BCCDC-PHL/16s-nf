#!/bin/bash
set -e

if [ $# -ne 1 ]; then 
	echo "USAGE: bash install.sh [PIPELINE_VERSION]"
fi

PIPELINE_VERSION=$1

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
	ncbi,16s-ncbi,1.0,/data/ref_databases/blast/16S/ncbi/latest/
	itgdb,16s-itgdb,1.0,/data/ref_databases/blast/16S/itgdb/latest/
	ezbio,16s-ezbio,1.0,/data/ref_databases/blast/16S/ezbio/latest/
	EOL
else
	echo " ------ Databases file already exists. Skipping step... ------ "
fi
