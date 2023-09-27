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
        taxonkit_lineage_record = {}
        for line in f:
            line_split = line.strip().split('\t')
            taxid = line_split[0]
            lineage = line_split[1]
            lineage_split = lineage.split(';')
            name = line_split[2]
            rank = line_split[3]
            taxonkit_lineage_record['taxid'] = taxid
            taxonkit_lineage_record['lineage_str'] = lineage
            taxonkit_lineage_record['lineage'] = lineage_split
            taxonkit_lineage_record['name'] = name
            taxonkit_lineage_record['rank'] = rank
            taxonkit_lineage_by_taxid[taxid] = taxonkit_lineage_record
            taxonkit_lineage_record = {}
            if len(lineage) >= 8:
                taxonkit_lineage_by_taxid[taxid]['species'] = lineage_split[7]
            else:
                taxonkit_lineage_by_taxid[taxid]['species'] = None
            if len(lineage) >= 7:
                taxonkit_lineage_by_taxid[taxid]['genus'] = lineage_split[6]
            else:
                taxonkit_lineage_by_taxid[taxid]['genus'] = None
            
    return taxonkit_lineage_by_taxid


def parse_blast_results(blast_results_path):
    """
    Parse blast results

    :param blast_results_path: path to blast results
    :type blast_results_path: str
    
    """
    blast_results = []
    with open(blast_results_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            blast_results.append(row)

    return blast_results


def main(args):
    
    taxonkit_lineage_by_taxid = parse_taxonkit_lineage(args.taxonresult)

    blast_results = parse_blast_results(args.blastresult)

    for blast_result in blast_results:
        taxid = blast_result['subject_taxids']
        if taxid in taxonkit_lineage_by_taxid:
            blast_result['species'] = taxonkit_lineage_by_taxid[blast_result['subject_taxids']]['species']
            blast_result['genus'] = taxonkit_lineage_by_taxid[blast_result['subject_taxids']]['genus']
        else:
            blast_result['species'] = None
            blast_result['genus'] = None

    output_fieldnames = [
        'query_seq_id',
        'subject_accession',
        'subject_strand',
        'query_length',
        'query_start',
        'query_end',
        'subject_length',
        'subject_start',
        'subject_end',
        'alignment_length',
        'percent_identity',
        'percent_coverage',
        'num_mismatch',
        'num_gaps',
        'e_value',
        'bitscore',
        'subject_taxids',
        'subject_names',
        'species',
        'genus',
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
