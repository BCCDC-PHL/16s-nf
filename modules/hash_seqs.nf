process hash_seqs {

    tag { sample_id  }

    input:
    val(seq)

    output:
    tuple  val(sample_id), path("${sample_id}_sha256.csv"), emit: csv
    tuple  val(sample_id), path("${sample_id}_provenance.yml"), emit: provenance

    script:
    sample_id = seq.id
    """
    echo ">${sample_id}" > ${sample_id}.fa
    echo "${seq.seqString}" >> ${sample_id}.fa

    shasum -a 256  ${sample_id}.fa | tr -s ' ' ',' > ${sample_id}_sha256.csv

    while IFS=',' read -r hash filename; do
      printf -- "- input_filename: \$filename\\n  input_path: \$(realpath \$filename)\\n  sha256: \$hash\\n" >> ${sample_id}_provenance.yml
    done < ${sample_id}_sha256.csv
    """
}
