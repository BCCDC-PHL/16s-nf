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
    metadata = parse_metadata(args.metadata)
    output_fieldnames, blast_results = parse_blast_results(args.blastresult)
    for record in blast_results:
        record['database_name'] = args.database_name
        record['database_version'] = metadata.get('version', None)
        record['database_date'] = metadata.get('date', None)


    output_fieldnames += [
        'database_name',
        'database_version',
        'database_date',
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
