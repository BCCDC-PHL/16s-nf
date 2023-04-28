#!/usr/bin/env python3

import argparse
import json

def parse_fasta(fasta_path):
    fasta = {}
    seq_id = ''
    seq = []
    with open(fasta_path, 'r') as f:
        for line in f:
            if line.startswith('>'):
                seq_id = line.strip().lstrip('>').split()[0]
            else:
                seq.append(line.strip())

    fasta['id'] = seq_id
    fasta['seq'] = ''.join(seq)

    return fasta

def main(args):
    iupac_ambiguous_bases = set([
        'M', 'R', 'W', 'S', 'Y', 'K',
        'V', 'H', 'D', 'B',
    ])
    fasta = parse_fasta(args.input)
    seq_length = len(fasta['seq'])
    num_ambiguous_bases = 0
    num_n_bases = 0

    for base in fasta['seq']:
        if base.upper() in iupac_ambiguous_bases:
            num_ambiguous_bases += 1

    for base in fasta['seq']:
        if base.upper() == 'N':
            num_n_bases += 1

    print('seq_length,num_ambiguous_bases,num_n_bases')
    print(','.join(map(str, [seq_length, num_ambiguous_bases, num_n_bases])))
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input')
    args = parser.parse_args()
    main(args)
