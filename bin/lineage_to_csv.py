#!/usr/bin/env python3

import argparse
import csv
import json
import sys


def parse_lineage(lineage_path):
    input_fieldnames = [
        'input_taxid',
        'taxon_names',
        'taxids',
        'taxon_ranks',
    ]
    semicolon_delimited_fields = [
        'taxon_names',
        'taxids',
        'taxon_ranks',
    ]

    parsed_lineages = []
    output_lineages = []
    with open(lineage_path, 'r') as f:
        reader = csv.DictReader(f, fieldnames=input_fieldnames, delimiter='\t')
        for row in reader:
            for field in semicolon_delimited_fields:
                row[field] = row[field].split(';')
            parsed_lineages.append(row)

    for row in parsed_lineages:
        taxon_names = row['taxon_names']
        taxids = row['taxids']
        taxon_ranks = row['taxon_ranks']

        for idx in range(len(taxon_names)):
            lineage_record = {
                'name': taxon_names[idx],
                'taxid': taxids[idx],
                'rank': taxon_ranks[idx],
            }
            output_lineages.append(lineage_record)


    return output_lineages

            
def main(args):
    lineage = parse_lineage(args.input)
    output_fieldnames = [
        'taxid',
        'rank',
        'name',
    ]
    writer = csv.DictWriter(sys.stdout, fieldnames=output_fieldnames, dialect='unix', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for row in lineage:
        writer.writerow(row)

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input')
    args = parser.parse_args()
    main(args)
