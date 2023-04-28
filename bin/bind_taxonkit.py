#!/usr/bin/env python3

import argparse
import pandas as pd 
import numpy as np

def main(args):
    cols = 'subject_taxids,lineage,name,rank'.split(',')
    #taxon_results = pd.read_csv('F1910235_taxon_results.txt',sep = '\t', names=cols)
    taxon_results = pd.read_csv(args.taxonresult,sep = '\t', names=cols)

    blast_results = pd.read_csv(args.blastresult,sep = ',')
    taxon_results = taxon_results.dropna()



    conditions = [
        (taxon_results['rank'] == "genus"),
        (taxon_results['rank'] == "species"),
        (taxon_results['rank'] == "strain")

    ]

    choices_species = [None, taxon_results['lineage'].apply(lambda x: x.split(';')[-1]), taxon_results['lineage'].apply(lambda x: x.split(';')[-2])]
    choices_genus = [taxon_results['lineage'].apply(lambda x: x.split(';')[-1]), taxon_results['lineage'].apply(lambda x: x.split(';')[-2]),taxon_results['lineage'].apply(lambda x: x.split(';')[-3])]

    taxon_results['species'] = np.select(conditions,choices_species, default = taxon_results['lineage'].apply(lambda x: x.split(';')[-1]))
    taxon_results['genus'] = np.select(conditions,choices_genus, default = taxon_results['lineage'].apply(lambda x: x.split(';')[-2]))
    

    merged = pd.merge(blast_results,taxon_results[['subject_taxids','species','genus']],on='subject_taxids', how='left')

    merged.to_csv(args.outfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-f','--taxonresult')
    parser.add_argument('-b','--blastresult')
    parser.add_argument('-o','--outfile')
    args = parser.parse_args()
    main(args)