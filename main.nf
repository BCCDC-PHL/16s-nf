#!/usr/bin/env nextflow

import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

// Define a formatter
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")

// Get the current date and time
LocalDateTime now = LocalDateTime.now()

// Format the current date and time
String formattedDateTime = now.format(formatter)

// Print the formatted date and time
println "Current date and time: $formattedDateTime"

nextflow.enable.dsl = 2

include { hash_seqs }               from './modules/hash_seqs.nf'
include { seq_qc }               from './modules/blast.nf'
include { blastn }               from './modules/blast.nf'
include { filter_by_regex }      from './modules/blast.nf'
include { filter_best_bitscore } from './modules/blast.nf'
include { build_report }         from './modules/blast.nf'
include { collect_provenance }         from './modules/provenance.nf'
include { pipeline_provenance }         from './modules/provenance.nf'
include { global_provenance }         from './modules/provenance.nf'


workflow {

  ch_start_time = Channel.of(now)
  ch_pipeline_name = Channel.of(workflow.manifest.name)
  ch_pipeline_version = Channel.of(workflow.manifest.version)

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

  ch_seqs = ch_fasta.splitFasta(record: [id: true, seqString: true])

  main:

    hash_seqs(ch_seqs)


    seq_qc(ch_seqs)
    ch_blast = blastn(ch_seqs.combine(ch_db)).blast_report
    ch_blast_prov = blastn.out.provenance.map{}

    if (params.filter_regexes != 'NO_FILE') {
      ch_regexes = Channel.fromPath(params.filter_regexes)
      ch_blast = filter_by_regex(ch_blast.combine(ch_regexes)).blast_filtered
    }

    ch_blast_collect = ch_blast.collectFile(it -> it[2], name: "${params.outdir}/collected_blast.csv", keepHeader: true, skip: 1)

    filter_best_bitscore(ch_blast)

    build_report(ch_blast_collect, Channel.fromPath(params.databases))

    filter_best_bitscore.out.blast_best_bitscore_csv.collectFile(it -> it[1], name: "collected_blast_best_bitscore.csv", storeDir: params.outdir, keepHeader: true, skip: 1)

    // Build pipeline provenance 
    ch_pipeline_provenance = pipeline_provenance(ch_pipeline_name.combine(ch_pipeline_version).combine(ch_start_time), build_report.out.provenance)
    
    //Pool Provenance data
    ch_provenance = hash_seqs.out.provenance
    ch_provenance = ch_provenance.join(seq_qc.out.provenance).map{ it -> [it[0], [it[1]] << it[2]] }
    ch_provenance = ch_provenance.join(blastn.out.provenance.groupTuple()).map{ it -> [it[0], (it[1] + it[2]).flatten() ] } 
    ch_provenance = ch_provenance.join(filter_best_bitscore.out.provenance).map{ it -> [it[0], it[1] << it[2]] }
    ch_provenance = ch_provenance.join(seq_qc.out.provenance.map{it -> it[0]}.combine(ch_pipeline_provenance)).map{ it -> [it[0], it[1] << it[2]] }
    collect_provenance(ch_provenance)
}
