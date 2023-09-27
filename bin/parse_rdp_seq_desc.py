#!/usr/bin/env python3

import argparse
import pandas as pd 

def main(args):
    blast_results = pd.read_csv(args.blastresult,sep = ',')
    #blast_results = pd.read_csv('F1910235_blast.csv',sep = ',')
    #print(blast_results)
    dict = {}
    with open(args.decriptionfile) as f:
        for line in f:
            key = line.split(';')[0].split(' ')[0].replace('>','')
            species = line.split(';')[0].split(' ')[1:3]
            species = ' '.join(species).replace('Lineage=Root','').replace('(T)','').strip()
            genus = line.split(';')[-2]
            dict[key] = [species, genus]



    df = pd.DataFrame([{"subject_accession": key, "species": species, "genus": genus} for key, (species,genus) in dict.items()])
    
    fil = df['species'].str.contains('uncultured')
    filtered_df = df[~fil]

    
    merged = pd.merge(blast_results,filtered_df,on='subject_accession', how='left')

    

    
    merged = merged.dropna(subset=['species','genus'])
    print(merged)
    #filtered_merged = filtered_merged[~(filtered_merged['species'] == '')]
    

    merged.to_csv(args.outfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-f','--decriptionfile')
    parser.add_argument('-b','--blastresult')
    parser.add_argument('-o','--outfile')
    args = parser.parse_args()
    main(args)