#!/usr/bin/env python3

import argparse
import csv
import json
import sys


def parse_taxonkit_lineage(taxonkit_path):
    """
    Parse taxonkit lineage outputs

    :param taxonkit_path: path to taxonkit lineage output
    :type taxonkit_path: str
    :return: taxonkit lineages, by taxid. dict of dicts. keys of inner dicts: ['taxid', 'lineage', 'name', 'rank']
    :rtype: dict[str, dict[str, str]]
    """
    taxonkit_lineage_by_taxid = {}
    with open(taxonkit_path, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            taxonkit_lineage_record = {}
            query_taxid = row['query_taxid']
            lineage = row['lineage']
            lineage_split = lineage.split(';')
            taxids = row['lineage_taxids']
            taxids_split = taxids.split(';')
            name = row['query_taxon_name']
            ranks = row['lineage_ranks']
            ranks_split = ranks.split(';')

            taxonkit_lineage_record['query_taxid'] = query_taxid
            for idx, rank in enumerate(ranks_split):
                if rank == 'species':
                    taxonkit_lineage_record['species_taxid'] = taxids_split[idx]
                    taxonkit_lineage_record['species_name'] = lineage_split[idx]
                elif rank == 'genus':
                    taxonkit_lineage_record['genus_taxid'] = taxids_split[idx]
                    taxonkit_lineage_record['genus_name'] = lineage_split[idx]

            taxonkit_lineage_by_taxid[query_taxid] = taxonkit_lineage_record
            
    return taxonkit_lineage_by_taxid


def parse_blast_results(blast_results_path):
    """
    Parse blast results

    :param blast_results_path: path to blast results
    :type blast_results_path: str
    
    """
    header_fieldnames = []
    blast_results = []
    with open(blast_results_path, 'r') as f:
        header_line = f.readline().strip()
        header_fieldnames = header_line.split(',')

    with open(blast_results_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            blast_results.append(row)

    return header_fieldnames, blast_results


def main(args):
    
    taxonkit_lineage_by_taxid = parse_taxonkit_lineage(args.taxonresult)

    output_fieldnames, blast_results = parse_blast_results(args.blastresult)

    for blast_result in blast_results:
        subject_taxid = blast_result['subject_taxids']
        if subject_taxid in taxonkit_lineage_by_taxid:
            blast_result['species'] = taxonkit_lineage_by_taxid[subject_taxid].get('species_name', None)
            blast_result['genus'] = taxonkit_lineage_by_taxid[subject_taxid].get('genus_name', None)
        else:
            blast_result['species'] = None
            blast_result['genus'] = None
    
    output_fieldnames += [
        'genus',
        'species',
    ]
    writer = csv.DictWriter(sys.stdout, fieldnames=output_fieldnames, delimiter=',', lineterminator='\n', quoting=csv.QUOTE_MINIMAL, extrasaction='ignore')
    writer.writeheader()
    for blast_result in blast_results:
        writer.writerow(blast_result)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-f','--taxonresult')
    parser.add_argument('-b','--blastresult')
    args = parser.parse_args()
    main(args)
