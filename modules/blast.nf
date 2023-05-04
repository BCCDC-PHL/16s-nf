process seq_qc {

    tag { sample_id }

    executor 'local'

    publishDir "${params.outdir}/${sample_id}", mode: 'copy', pattern: "${sample_id}_seq_qc.csv"

    input:
    tuple path(seq)

    output:
    tuple val(sample_id), path("${sample_id}_seq_qc.csv"), emit: seq_qc_csv

    script:
    sample_id = seq.getName().split('\\.')[0]
    """
    seq_qc.py -i ${seq} > ${sample_id}_seq_qc.csv
    """
}

process blastn {
    //errorStrategy 'ignore'
    

    publishDir "${params.outdir}/${sample_id}", mode: 'copy', pattern: "${sample_id}*"

    input:
    tuple path(query), path(db_dir), val(db_name)

    output:
    tuple val(sample_id), path("${sample_id}_blast.csv"), emit: blast_csv, optional:true
    tuple val(sample_id), path("${sample_id}_seq_description"), emit: seq_description, optional:true
    tuple val(sample_id), path("${sample_id}_blast_species_genus_results.csv"), emit: taxon_results, optional:true
    tuple val(sample_id), path("${sample_id}_taxon_results.txt"), emit: raw_taxon_results, optional:true
    
    script:
    sample_id = query.getName().split('\\.')[0]
    """
    export BLASTDB="${db_dir}"

    echo "query_seq_id,subject_accession,subject_strand,query_length,query_start,query_end,subject_length,subject_start,subject_end,alignment_length,percent_identity,percent_coverage,num_mismatch,num_gaps,e_value,bitscore,subject_taxids,subject_names" > ${sample_id}_blast_pre.csv

    blastn \
      -db ${db_name} \
      -num_threads ${task.cpus} \
      -perc_identity ${params.minid} \
      -qcov_hsp_perc ${params.mincov} \
      -query ${query} \
      -outfmt "6 qseqid saccver sstrand qlen qstart qend slen sstart send length pident qcovhsp mismatch gaps evalue bitscore staxids sscinames" \
    | tr \$"\\t" "," >> ${sample_id}_blast_pre.csv

    tail -qn+2 ${sample_id}_blast_pre.csv | cut -d',' -f2 | sort -u > seqids
    blastdbcmd -db ${db_name} -entry_batch seqids | grep '>' > ${sample_id}_seq_description

    if [ "${db_dir}" == "ncbi16s" ] ; then
        parse_genbank.py -i ${sample_id}_blast_pre.csv -g ${params.gbfile} -o ${sample_id}_blast.csv
    else
        cat ${sample_id}_blast_pre.csv > ${sample_id}_blast.csv
    fi

    tail -qn+2 ${sample_id}_blast.csv | cut -d',' -f17 | sort -u > taxids
    taxonkit lineage -r -n  taxids > ${sample_id}_taxon_results.txt

    if [ "${db_dir}" == "2022-11-16_nt" ] || [ "${db_dir}" == "silva" ] || [ "${db_dir}" == "ncbi16s" ] ; then
        bind_taxonkit.py -f ${sample_id}_taxon_results.txt -b ${sample_id}_blast.csv -o ${sample_id}_blast_species_genus_results.csv
    fi

    if [ "${db_dir}" == "RDP" ]; then
        parse_rdp_seq_desc.py -f ${sample_id}_seq_description -b ${sample_id}_blast.csv -o ${sample_id}_blast_species_genus_results.csv
    fi

    if [ "${db_dir}" == "greengenes" ]; then
        parse_gg_seq_desc.py -f ${params.gg_tax} -b ${sample_id}_blast.csv -o ${sample_id}_blast_species_genus_results.csv
    fi

    """
}



process filter_best_bitscore {

    tag { sample_id }

    executor 'local'

    publishDir "${params.outdir}/${sample_id}", mode: 'copy', pattern: "${sample_id}_blast_best_bitscore.csv"

    input:
    tuple val(sample_id), path(full_blast_report)

    output:
    tuple val(sample_id), path("${sample_id}_blast_best_bitscore.csv"), emit: blast_best_bitscore_csv

    script:
    """
    filter_best_bitscore.py -i ${full_blast_report} > ${sample_id}_blast_best_bitscore.csv
    """
}