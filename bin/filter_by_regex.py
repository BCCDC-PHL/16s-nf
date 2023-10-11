#!/usr/bin/env python3

import argparse
import csv
import json
import re
import sys


def parse_blast_report(blast_report_path):
    header_fieldnames = []
    with open(blast_report_path, 'r') as f:
        header_line = f.readline().strip()
        header_fieldnames = header_line.split(',')

    parsed_blast_report = []
    with open(blast_report_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed_blast_report.append(row)

    return header_fieldnames, parsed_blast_report


def main(args):
    output_fieldnames, blast_report = parse_blast_report(args.input)
    regexes = []
    with open(args.regexes, 'r') as f:
        for line in f:
            regexes.append(re.compile(line.strip()))

    filtered_blast_report = []
    for blast_record in blast_report:
        regex_match = False
        for regex in regexes:
            if regex.search(blast_record['subject_names']):
                regex_match = True                 
        if not regex_match:
            filtered_blast_report.append(blast_record)


    writer = csv.DictWriter(sys.stdout, fieldnames=output_fieldnames, dialect='unix', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for row in filtered_blast_report:
        writer.writerow(row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input')
    parser.add_argument('-r', '--regexes')
    args = parser.parse_args()
    main(args)
