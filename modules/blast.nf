process seq_qc {

    tag { sample_id }

    executor 'local'

    publishDir "${params.outdir}/${sample_id}", mode: 'copy', pattern: "${sample_id}_seq_qc.csv"

    input:
    val(seq)

    output:
    tuple val(sample_id), path("${sample_id}_seq_qc.csv"), emit: seq_qc_csv
    tuple val(sample_id), path("${sample_id}_qc_provenance.yml"),                emit: provenance

    script:
    sample_id = seq.id
    """
    echo ">${sample_id}" > ${sample_id}.fa
    echo "${seq.seqString}" >> ${sample_id}.fa

    seq_qc.py -i ${sample_id}.fa > ${sample_id}_seq_qc.csv

    cat <<-EOL_VERSIONS > ${sample_id}_qc_provenance.yml
    - process_name: "${task.process}"
      tools:
      - tool_name: python
        tool_version: \$(python3 --version | cut -d' ' -f2)
    EOL_VERSIONS
    """
}

process blastn {

    tag { sample_id + ' / ' + db_id }

    publishDir "${params.outdir}/${sample_id}", mode: 'copy', pattern: "${sample_id}_${db_id}*"

    input:
    tuple val(seq), val(db_id), val(db_name), val(db_version), path(db_dir)

    output:
    tuple val(sample_id), val(db_id), path("${sample_id}_${db_id}_blast.csv"),       emit: blast_report, optional:true
    tuple val(sample_id), val(db_id), path("${sample_id}_${db_id}_seq_description"), emit: seq_description, optional:true
    tuple val(sample_id), val(db_id), path("${sample_id}_${db_id}_lineages.tsv"),    emit: lineage, optional:true
    tuple val(sample_id), path("${sample_id}_${db_id}_blastn_provenance.yml"),                emit: provenance
    
    script:
    sample_id = seq.id
    """
    echo ">${sample_id}" > ${sample_id}.fa
    echo "${seq.seqString}" >> ${sample_id}.fa

    export BLASTDB="${db_dir}"
    export TAXONKIT_DB="${params.taxonkit_db}"

    echo "query_seq_id,subject_accession,subject_strand,query_length,query_start,query_end,subject_length,subject_start,subject_end,alignment_length,percent_identity,percent_coverage,num_mismatch,num_gaps,e_value,bitscore,subject_taxids,subject_names" > ${sample_id}_${db_id}_blast.csv

    blastn \
      -db ${db_name} \
      -num_threads ${task.cpus} \
      -perc_identity ${params.minid} \
      -qcov_hsp_perc ${params.mincov} \
      -query ${sample_id}.fa \
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

    cat <<-EOL_VERSIONS > ${sample_id}_${db_id}_blastn_provenance.yml
    - process_name: "${task.process}"
      tools:
      - tool_name: blastn
        tool_version: \$(blastn -version | head -n1 | sed 's/blastn: //g')
        parameters:
        - parameter: "perc_identity"
          value: ${params.minid}
        - parameter: "qcov_hsp_perc"
          value: ${params.mincov}
      - tool_name: taxonkit
        tool_version: \$(taxonkit version | cut -d' ' -f2)
      - tool_name: python
        tool_version: \$(python3 --version | cut -d' ' -f2)
      databases:
      - database_name: ${db_name}
        database_version: ${db_version}
        files: 
    \$(sha256sum \$(readlink -f ${db_dir})/${db_name}* | awk '{ printf("    - filename: \\"%s\\"\\n      sha256: \\"%s\\"\\n", \$2, \$1) }')
    EOL_VERSIONS

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
    tuple val(sample_id), path("${sample_id}_${db_id}_filter_regex_provenance.yml") ,   emit: provenance, optional: true

    script:
    """
    filter_by_regex.py -i ${full_blast_report} -r ${filter_regexes} > ${sample_id}_${db_id}_blast_filtered.csv

    # cat <<-EOL_VERSIONS > ${sample_id}_${db_id}_filter_regex_provenance.yml
    # - process_name: "${task.process}"
    #   tools:
    #   - tool_name: python
    #     tool_version: \$(python3 --version | cut -d' ' -f2)
    #     parameters:
    #     - parameter: filter_regexes
    #       value: ${filter_regexes}
    # EOL_VERSIONS
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
    tuple val(sample_id), path("${sample_id}_${db_id}_filter_bitscore_provenance.yml"),    emit: provenance, optional: true

    script:
    """
    filter_best_bitscore.py -i ${full_blast_report} > ${sample_id}_${db_id}_blast_best_bitscore.csv

    # cat <<-EOL_VERSIONS > ${sample_id}_${db_id}_filter_bitscore_provenance.yml
    # - process_name: "${task.process}"
    #   tools:
    #   - tool_name: python
    #     tool_version: \$(python3 --version | cut -d' ' -f2)
    # EOL_VERSIONS
    """
}

process build_report {

    executor 'local'

    publishDir "${params.outdir}/", mode: 'copy', pattern: "*report.html"

    input:
    path(collected_blast)
    path(database_csv)

    output:
    path("*_report.html"),        emit: report
    path("report_provenance.yml"),      emit: provenance

    script:
    """
    report2.py --blast ${collected_blast} --db ${database_csv} --output ${params.run_name}_report.html

    cat <<-EOL_VERSIONS > report_provenance.yml
    - process_name: "${task.process}"
      tools:
      - tool_name: python
        tool_version: \$(python3 --version | cut -d' ' -f2)
    EOL_VERSIONS
    """
}
