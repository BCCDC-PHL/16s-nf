#!/usr/bin/env python3

import argparse
import pandas as pd


dict = {}

#with open('/home/sherrie.wang/analysis/16s/databases/ncbi16s/sequence.gb', 'r') as f:
def main(args):
    with open(args.gbfile, 'r') as f:
        taxon = None
        locus = None
        for line in f:
            if line.startswith('VERSION'):
                locus = line.split()[1]
            elif line.strip().startswith('/db_xref="taxon:'):
                taxon = line.split('=')[1].strip().strip('"').split(':')[1]
            if locus and taxon:
                dict[locus] = taxon


    blast_result = pd.read_csv(args.input)
    blast_result['subject_taxids'] = blast_result['subject_accession'].apply(lambda x: dict[x] if x in dict.keys() else None)

    blast_result.to_csv(args.output, index = False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-i','--input')
    parser.add_argument('-g','--gbfile')
    parser.add_argument('-o','--output')
    args = parser.parse_args()
    main(args)