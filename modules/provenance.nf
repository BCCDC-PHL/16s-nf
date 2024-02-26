process collect_provenance {

  tag { sample_id }

  executor 'local'

  publishDir "${params.outdir}/provenance_files", pattern: "${sample_id}_*_provenance.yml", mode: 'copy'

  input:
  tuple val(sample_id), path(provenance_files)

  output:
  tuple val(sample_id), path("${sample_id}_*_provenance.yml")

  script:
  """
  cat ${provenance_files} > ${sample_id}_\$(date +%Y%m%d%H%M%S)_provenance.yml
  """
}

process pipeline_provenance {

  tag { pipeline_name + " / " + pipeline_version }

  executor 'local'

  input:
  tuple val(pipeline_name), val(pipeline_version), val(analysis_start)
  path(other_files)

  output:
  path("pipeline_provenance.yml")

  script:
  """
  cat ${other_files} > pipeline_provenance.yml
  printf -- "- pipeline_name: ${pipeline_name}\\n  pipeline_version: ${pipeline_version}\\n- timestamp_analysis_start: ${analysis_start}\\n" >> pipeline_provenance.yml

  """
}
process global_provenance {

  tag { pipeline_name + " / " + pipeline_version }

  executor 'local'

  input:
  path(pipline_provenance)
  path(other_files)

  output:
  path("pipeline_provenance.yml")

  script:
  """
  cat ${pipline_provenance} ${other_files} >> pipeline_provenance.yml
  """
}