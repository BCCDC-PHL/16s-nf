#!/usr/bin/env python3
import os, sys 
import pandas as pd
import argparse
from functools import partial
from custom_html import HEAD, DBNOTE, build_table, build_row, FOOT

row_names = "subject_accession species genus query_length alignment_length num_mismatch bitscore percent_coverage percent_identity database_name database_version database_date".split()
build_row_part = partial(build_row, row_names=row_names)

def parse_blast(filepath):
	df = pd.read_csv(filepath)

	#df['database'] = os.path.basename(filepath).split('_')[1]
	df["species"] = df["species"].apply(lambda x: "" if x == "a" else x)
	df = df.sort_values(['query_seq_id', 'bitscore'], ascending=[True, False])

	df['percent_identity'] = df['percent_identity'].round(3)
	df['percent_coverage'] = df['percent_coverage'].round(3)


	df = df.drop_duplicates(subset=['query_seq_id', 'subject_accession', 'species', 'genus', 'percent_identity', 'percent_coverage', 'bitscore'])
	df = df[~df['species'].str.contains('uncultured')]


	return df.fillna('')

def main(args):
	blast_table = parse_blast(args.blast)

	outfile = open(args.output, "w")
	outfile.write(HEAD)
	#outfile.write(DBNOTE)

	for name, df in blast_table.groupby('query_seq_id'):
		
		print(name)
		
		if df.shape[0] < 20:
			str_rows = df.apply(build_row_part, axis=1)
			str_rows = '\n'.join(str_rows)
			str_table = build_table(name, row_names, str_rows)
			outfile.write(str_table)
		else:
			N = df.shape[0]
			str_rows = df.iloc[0:20].apply(build_row_part, axis=1)
			str_rows = '\n'.join(str_rows)
			
			hidden_str_rows = df.iloc[21:min(N, 300)].apply(build_row_part, axis=1)
			hidden_str_rows = '\n'.join(hidden_str_rows)

			str_table = build_table(name, row_names, str_rows, hidden_str_rows)
			outfile.write(str_table)

	outfile.write(FOOT)
	outfile.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-b', '--blast')
	parser.add_argument('-o', '--output')
	args = parser.parse_args()
	main(args)
