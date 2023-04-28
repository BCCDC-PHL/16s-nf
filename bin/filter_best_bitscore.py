#!/usr/bin/env python3

import argparse
import csv
import json
import sys


def parse_blast_report(blast_report_path):
    with open(blast_report_path, 'r') as f:
        header_line = f.readline().strip()
        header_fieldnames = header_line.split(',')

    int_fields = [
        'bitscore',
    ]
    parsed_blast_report = []
    with open(blast_report_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in int_fields:
                row[field] = int(row[field])
            parsed_blast_report.append(row)

    return header_fieldnames, parsed_blast_report


def determine_best_bitscore(parsed_blast_report):
    best_bitscore = 0
    for blast_record in parsed_blast_report:
        if blast_record['bitscore'] > best_bitscore:
            best_bitscore = blast_record['bitscore']

    return best_bitscore
        

def main(args):
    output_fieldnames, blast_report = parse_blast_report(args.input)
    best_bitscore = determine_best_bitscore(blast_report)

    filtered_blast_report = list(filter(lambda x: x['bitscore'] == best_bitscore, blast_report))

    writer = csv.DictWriter(sys.stdout, fieldnames=output_fieldnames, dialect='unix', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for row in filtered_blast_report:
        writer.writerow(row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input')
    args = parser.parse_args()
    main(args)
