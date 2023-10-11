process seq_qc {

    tag { sample_id }

    executor 'local'

    publishDir "${params.outdir}/${sample_id}", mode: 'copy', pattern: "${sample_id}_seq_qc.csv"

    input:
    path(seq)

    output:
    tuple val(sample_id), path("${sample_id}_seq_qc.csv"), emit: seq_qc_csv

    script:
    sample_id = seq.getName().split('\\.')[0]
    """
    seq_qc.py -i ${seq} > ${sample_id}_seq_qc.csv
    """
}

process blastn {
    errorStrategy 'ignore'

    tag { sample_id + ' / ' + db_id }

    publishDir "${params.outdir}/${sample_id}", mode: 'copy', pattern: "${sample_id}_${db_id}*"

    input:
    tuple path(query), val(db_id), val(db_name), path(db_dir)

    output:
    tuple val(sample_id), val(db_id), path("${sample_id}_${db_id}_blast.csv"),       emit: blast_report, optional:true
    tuple val(sample_id), val(db_id), path("${sample_id}_${db_id}_seq_description"), emit: seq_description, optional:true
    tuple val(sample_id), val(db_id), path("${sample_id}_${db_id}_lineage.tsv"),     emit: lineage, optional:true
    
    script:
    sample_id = query.getName().split('\\.')[0]
    """
    export BLASTDB="${db_dir}"

    echo "query_seq_id,subject_accession,subject_strand,query_length,query_start,query_end,subject_length,subject_start,subject_end,alignment_length,percent_identity,percent_coverage,num_mismatch,num_gaps,e_value,bitscore,subject_taxids,subject_names" > ${sample_id}_${db_id}_blast.csv

    blastn \
      -db ${db_name} \
      -num_threads ${task.cpus} \
      -perc_identity ${params.minid} \
      -qcov_hsp_perc ${params.mincov} \
      -query ${query} \
      -outfmt "6 qseqid saccver sstrand qlen qstart qend slen sstart send length pident qcovhsp mismatch gaps evalue bitscore staxids sscinames" \
    | tr \$"\\t" "," >> ${sample_id}_${db_id}_blast.csv

    get_taxids.py --input ${sample_id}_${db_id}_blast.csv > ${sample_id}_${db_id}_taxids.csv
    printf 'query_taxid\\tlineage\\tlineage_taxids\\tquery_taxon_name\\tlineage_ranks\\n' > ${sample_id}_${db_id}_lineages.tsv
    taxonkit lineage -R -n -t ${sample_id}_${db_id}_taxids.csv >> ${sample_id}_${db_id}_lineages.tsv
    mv ${sample_id}_${db_id}_blast.csv ${sample_id}_${db_id}_blast_tmp.csv
    bind_taxonkit.py -f ${sample_id}_${db_id}_lineages.tsv -b ${sample_id}_${db_id}_blast_tmp.csv > ${sample_id}_${db_id}_blast.csv

    if [ "${params.no_db_metadata}" == "false" ]; then
        mv ${sample_id}_${db_id}_blast.csv ${sample_id}_${db_id}_blast_tmp.csv
        add_db_metadata.py -m ${db_dir}/metadata.json -b ${sample_id}_${db_id}_blast_tmp.csv -d ${db_id} > ${sample_id}_${db_id}_blast.csv
    fi
    """
}


process filter_by_regex {

    tag { sample_id + ' / ' + db_id }

    executor 'local'

    publishDir "${params.outdir}/${sample_id}", mode: 'copy', pattern: "${sample_id}_${db_id}_blast_filtered.csv"

    input:
    tuple val(sample_id), val(db_id), path(full_blast_report), path(filter_regexes)

    output:
    tuple val(sample_id), val(db_id), path("${sample_id}_${db_id}_blast_filtered.csv"), emit: blast_filtered

    script:
    """
    filter_by_regex.py -i ${full_blast_report} -r ${filter_regexes} > ${sample_id}_${db_id}_blast_filtered.csv
    """
}


process filter_best_bitscore {

    tag { sample_id + ' / ' + db_id }

    executor 'local'

    publishDir "${params.outdir}/${sample_id}", mode: 'copy', pattern: "${sample_id}_${db_id}_blast_best_bitscore.csv"

    input:
    tuple val(sample_id), val(db_id), path(full_blast_report)

    output:
    tuple val(sample_id), path("${sample_id}_${db_id}_blast_best_bitscore.csv"), emit: blast_best_bitscore_csv

    script:
    """
    filter_best_bitscore.py -i ${full_blast_report} > ${sample_id}_${db_id}_blast_best_bitscore.csv
    """
}
