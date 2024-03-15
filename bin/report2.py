#!/usr/bin/env python3
import os, sys 
import pandas as pd
import argparse
from functools import partial
import re
from custom_html import HEAD, build_dbnote, build_table, build_row, FOOT, PAGEBREAK


EXPR_PRIORITY = re.compile(r'ATCC|LMG|type|NCTC')
row_names = "subject_accession species bitscore percent_coverage percent_identity database_name extra_info".split()
build_row_part = partial(build_row, row_names=row_names)


def parse_db_csv(filepath):
	df = pd.read_csv(filepath, index_col=0)
	return df

def parse_fasta(fasta_path):
	fasta = []
	header = ''
	seq = ''
	with open(fasta_path, 'r') as f:
		for line in f:
			if line.startswith('>'):
				if header != '':
					fasta.append((header, seq))
				header = line.strip().lstrip('>')
				seq = ''
			else:
				seq += line.strip()
		fasta.append((header, seq))
	return fasta

def extract_descriptions(database_df):
	ncbi_path = os.path.join(database_df.loc['ncbi', 'PATH'], database_df.loc['ncbi','DBNAME'])

	headers, _ = zip(*parse_fasta(ncbi_path))

	def clean(string):
		string = string.replace("'",'')
		return string

	headers = [clean(x) for x in headers]

	def extract_info(string):
		string = " ".join(string.split()[3:])

		if "strain" in string:
			string = string.split("strain")[1]
		
		return re.split("(?:16S|,)", string)[0]

	extra_info = [(x.split()[0], extract_info(x)) for x in headers ]

	df = pd.DataFrame(extra_info, columns=['subject_accession', 'extra_info']) 

	df = df.fillna('N/A')
	
	return df


def parse_blast(filepath):
	df = pd.read_csv(filepath)

	#df['database'] = os.path.basename(filepath).split('_')[1]

	df["species"] = df["species"].apply(lambda x: "" if x == "a" else x).astype(str)
	df = df.sort_values(['query_seq_id', 'bitscore'], ascending=[True, False])

	df['percent_identity'] = df['percent_identity'].round(3)
	df['percent_coverage'] = df['percent_coverage'].round(3)


	df = df.drop_duplicates(subset=['query_seq_id', 'subject_accession', 'species', 'genus', 'percent_identity', 'percent_coverage', 'bitscore'])
	df = df[~df['species'].str.contains('uncultured')]

	return df.fillna('N/A')

def main(args):
	blast_table = parse_blast(args.blast)

	outfile = open(args.output, "w")
	outfile.write(HEAD)

	database_df = parse_db_csv(args.db)
	DBNOTE = build_dbnote(database_df)

	extra_info = extract_descriptions(database_df)

	blast_table = blast_table.merge(extra_info, on='subject_accession', how='left')
	

	for name, df in blast_table.groupby('query_seq_id'):
		
		print(name)

		outfile.write(DBNOTE)

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

		outfile.write(PAGEBREAK)

	outfile.write(FOOT)
	outfile.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-b', '--blast', help='A single concatenated BLAST CSV table with hits from multiple samples and multiple database sources.')
	parser.add_argument('-d', '--db', help='Database CSV file containing ID, DBNAME, and PATH columns.')
	parser.add_argument('-o', '--output', help='Output HTML report filename.')
	args = parser.parse_args()
	main(args)
