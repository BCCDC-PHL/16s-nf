# fasta-blasta

A simple pipeline for running [BLAST](https://blast.ncbi.nlm.nih.gov/Blast.cgi) on [fasta](https://en.wikipedia.org/wiki/FASTA_format) files.

If multi-fasta file(s) are supplied, each sequence will be processed independently.

## Usage

```
nextflow run dfornika/fasta-blasta \
  --db_dir </path/to/blast/database_dir> \
  --db_name <blast_db_name> \
  --fasta_input </path/to/fasta_dir> \
  --outdir </path/to/output_dir>
```

By default, minimum identity and coverage thresholds of 95% will be applied to the blast results.
Alternate thresholds can be applied using the `--minid` and `--mincov` flags.

```
nextflow run dfornika/fasta-blasta \
  --db_dir </path/to/blast/database_dir> \
  --db_name <blast_db_name> \
  --fasta_input </path/to/fasta_dir> \
  --minid 99.0 \
  --mincov 97.5 \
  --outdir </path/to/output_dir>
```

## Outputs

Each sequence will have a separate output directory, named using the seq ID parsed from
the fasta header. That directory will contain:

```
<seq_id>_blast.csv
<seq_id>_blast_best_bitscore.csv
<seq_id>_seq_qc.csv
```

The `blast.csv` and `blast_best_bitscore.csv` files have the following headers:

```
query_seq_id
subject_accession
subject_strand
query_length
query_start
query_end
subject_length
subject_start
subject_end
alignment_length
percent_identity
percent_coverage
num_mismatch
num_gaps
e_value
bitscore
subject_taxids
subject_names
```

The `seq_qc.csv` file has the following headers:

```
seq_length
num_ambiguous_bases
num_n_bases
```
