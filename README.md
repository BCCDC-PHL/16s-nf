# 16s-nf

Prepare a report for taxonomic assignment based on [16S rRNA](https://en.wikipedia.org/wiki/16S_ribosomal_RNA) sequences, using [BLAST](https://blast.ncbi.nlm.nih.gov/Blast.cgi).

## Usage

The pipeline requires a list of BLAST databases to run against. It should follow the following format:

```csv
ID,DBNAME,PATH
ncbi,16S_ribosomal_RNA,/path/to/ncbi/2023-09-19_1.1_16S_ribosomal_RNA
silva,SSURef_NR99_tax_silva_trunc,/path/to/silva/2020-08-24_138.1_SSURef_NR99_tax_silva_trunc
```

...where we expect to find the actual database files at:

```
/path/to/ncbi/2023-09-19_1.1_16S_ribosomal_RNA/16S_ribosomal_RNA.ndb
/path/to/ncbi/2023-09-19_1.1_16S_ribosomal_RNA/16S_ribosomal_RNA.nhr
/path/to/ncbi/2023-09-19_1.1_16S_ribosomal_RNA/16S_ribosomal_RNA.nin
...etc
/path/to/silva/2020-08-24_138.1_SSURef_NR99_tax_silva_trunc/SSURef_NR99_tax_silva_trunc.ndb
/path/to/silva/2020-08-24_138.1_SSURef_NR99_tax_silva_trunc/SSURef_NR99_tax_silva_trunc.nhr
/path/to/silva/2020-08-24_138.1_SSURef_NR99_tax_silva_trunc/SSURef_NR99_tax_silva_trunc.nin
...etc
```

The pipeline also assumes that there is a `metadata.json` file alongside the database files

```
/path/to/ncbi/2023-09-19_1.1_16S_ribosomal_RNA/metadata.json
/path/to/silva/2020-08-24_138.1_SSURef_NR99_tax_silva_trunc/metadata.json
```

The contents of the metadata file may vary by database, but we assume that:

- The file contains a single top-level object (not an array or atomic value).
- The top-level object includes these fields:

```
version
date
```

The values associated with those fields will be incorporated into the blast results. All other fields in
the `metadata.json` file are ignored.

```
nextflow run BCCDC-PHL/16s-nf \
  --databases </path/to/blast/databases.csv> \
  --fasta_input </path/to/fasta_dir> \
  --outdir </path/to/output_dir>
```

By default, minimum identity and coverage thresholds of 95% will be applied to the blast results.
Alternate thresholds can be applied using the `--minid` and `--mincov` flags.

```
nextflow run BCCDC-PHL/16s-nf \
  --databases </path/to/blast/databases.csv> \
  --fasta_input </path/to/fasta_dir> \
  --minid 99.0 \
  --mincov 97.5 \
  --outdir </path/to/output_dir>
```

Collecting database metadata from the `metadata.json` file can be skipped using the `--no_db_metadata` flag.

```
nextflow run BCCDC-PHL/16s-nf \
  --databases </path/to/blast/databases.csv> \
  --no_db_metadata \
  --fasta_input </path/to/fasta_dir> \
  --outdir </path/to/output_dir>
```


## Outputs

Each sequence will have a separate output directory, named using the seq ID parsed from
the fasta header. That directory will contain:

```
<seq_id>_<db_id>_blast.csv
<seq_id>_<db_id>_blast_best_bitscore.csv
<seq_id>_<db_id>_blast_filtered.csv
<seq_id>_<db_id>_seq_qc.csv
```

The `_blast.csv`, `_blast_filtered.csv` and `blast_best_bitscore.csv` files have the following headers:

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
species
genus
database_name
database_version
database_date
```

...though if the `--no_db_metadata` flag is used when running the pipeline, the last three fields will be omitted.

The `seq_qc.csv` file has the following headers:

```
seq_length
num_ambiguous_bases
num_n_bases
```

There will also be collected ouputs in the top-level of the `--outdir` directory, named:

```
collected_blast.csv
collected_blast_best_bitscore.csv
```

...which will include results from all sequences.
