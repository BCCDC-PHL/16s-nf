#!/usr/bin/env python3

import argparse
import csv
import json


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
        lineage_list = []
        taxon_names = row['taxon_names']
        taxids = row['taxids']
        taxon_ranks = row['taxon_ranks']

        for idx in range(len(taxon_names)):
            lineage_list.append({
                'taxon_name': taxon_names[idx],
                'taxid': taxids[idx],
                'rank': taxon_ranks[idx],
            })

        root = {}
        for lineage_item in reversed(lineage_list):
            if 'child' in root:
                child_tmp = root['child']
                lineage_item['child'] = child_tmp
            root['child'] = lineage_item

        root['input_taxid'] = row['input_taxid']
        root['lineage'] = root['child']
        root.pop('child')

        output_lineages.append(root)

    return output_lineages

            
def main(args):
    lineage = parse_lineage(args.input)
    print(json.dumps(lineage, indent=2))
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input')
    args = parser.parse_args()
    main(args)
