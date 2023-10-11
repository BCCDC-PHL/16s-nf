#!/usr/bin/env python3


import argparse
import csv
import json
import sys


def parse_blast_report(blast_report_path):
    """
    """
    parsed_blast_report = []
    with open(blast_report_path, 'r') as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            parsed_blast_report.append(row)

    return parsed_blast_report


def main(args):
    blast_report = parse_blast_report(args.input)
    for blast_record in blast_report:
        print(blast_record['subject_taxids'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input')
    args = parser.parse_args()
    main(args)
