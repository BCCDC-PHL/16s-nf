#!/usr/bin/env python3

import argparse
import pandas as pd 

def main(args):
    blast_results = pd.read_csv(args.blastresult,sep = ',')
    #blast_results = pd.read_csv('F1910235_blast.csv',sep = ',')
    blast_results['subject_accession'] = blast_results['subject_accession'].astype(str)
    dict = {}
    with open(args.decriptionfile) as f:
        for line in f:
            key = line.split('\t')[0]
            species = line.split(';')[0][-1].replace('s__','')
            #species = ' '.join(species).replace('Lineage=Root','').replace('(T)','').strip()
            genus = line.split(';')[-2].replace('g__','')
            dict[key] = [species, genus]



    df = pd.DataFrame([{"subject_accession": key, "species": species, "genus": genus} for key, (species,genus) in dict.items()])

    merged = pd.merge(blast_results,df,on='subject_accession', how='left')

    merged.to_csv(args.outfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-f','--decriptionfile')
    parser.add_argument('-b','--blastresult')
    parser.add_argument('-o','--outfile')
    args = parser.parse_args()
    main(args)