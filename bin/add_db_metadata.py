#!/usr/bin/env python3

import argparse
import csv
import json
import sys

def parse_metadata(metadata_path):
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    return metadata

def parse_blast_results(blast_results_path):
    blast_results = []
    with open(blast_results_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            blast_results.append(row)

    return blast_results


def main(args):
    metadata = parse_metadata(args.metadata)
    blast_results = parse_blast_results(args.blastresult)
    for record in blast_results:
        record['database_name'] = args.database_name
        record['database_version_string'] = metadata.get('version', None)
        record['database_version_date'] = metadata.get('date', None)


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
        'database_name',
        'database_version_string',
        'database_version_date',
    ]

    writer = csv.DictWriter(sys.stdout, fieldnames=output_fieldnames, delimiter=',', lineterminator='\n', quoting=csv.QUOTE_MINIMAL, extrasaction='ignore')

    writer.writeheader()
    for record in blast_results:
        writer.writerow(record)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m','--metadata')
    parser.add_argument('-d','--database_name')
    parser.add_argument('-b','--blastresult')
    args = parser.parse_args()
    main(args)
