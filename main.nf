#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

include { seq_qc }               from './modules/blast.nf'
include { blastn }               from './modules/blast.nf'
include { filter_best_bitscore } from './modules/blast.nf'

workflow {

  if (params.samplesheet_input != 'NO_FILE') {
    ch_fasta = Channel.fromPath(params.samplesheet_input).splitCsv(header: true).map{ it -> [it['ID'], it['FILE']] }
  } else {
    ch_fasta = Channel.fromPath(params.fasta_search_path)
  }

  if (params.databases != 'NO_FILE') {
    ch_db = Channel.fromPath(params.databases).splitCsv(header: true).map{ it -> [it['ID'], it['DBNAME'], it['PATH']] }
  } else {
    ch_db = Channel.of()
  }

  ch_seqs = ch_fasta.splitFasta(file: true)

  main:
    seq_qc(ch_seqs)
    ch_blast = blastn(ch_seqs.combine(ch_db))
    ch_best_blast = filter_best_bitscore(ch_blast.taxon_results)

    ch_blast.taxon_results
        .collectFile(it -> it[1], name: "combined_blast_species_genus_results.csv", storeDir: params.outdir,keepHeader: true, skip: 1)
  
    ch_best_blast.blast_best_bitscore_csv
        .collectFile(it -> it[1], name: "combined_top1_results.csv", storeDir: params.outdir,keepHeader: true, skip: 1)
}
