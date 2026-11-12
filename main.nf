params.samplesheet = "${launchDir}/samplesheet.csv"
params.results_dir = "${launchDir}/results"

workflow {
	samples_ch = channel.fromPath(params.samplesheet, checkIfExists: true)
		.splitCsv(header: true)
		.map { row ->
			[[batch_id: row.batch_id, instrument_id: row.instrument_id, operator: row.operator], file(row.csv_path)]
		}

	CLEAN_AND_QC(samples_ch)

	qc_processed_ch = CLEAN_AND_QC.out.map { meta, clean_csv, qc_json ->
		def parsed = new groovy.json.JsonSlurper().parseText(qc_json.text)
		def new_meta = meta + [qc_status: parsed.status]
		[new_meta, clean_csv, qc_json]
	}

	qc_processed_ch
		.branch { new_meta, _clean_csv, _qc_json ->
			passed: new_meta.qc_status == 'PASSED'
			rejected: new_meta.qc_status == 'REJECTED_HEMOLYSIS'
		}
		.set { qc_routed }


	TRAIN_MODEL(qc_routed.passed)


	passed_metrics_ch = TRAIN_MODEL.out.model_results
		.map { _meta, _model, metrics -> metrics }
		.collect()

	rejected_qc_ch = qc_routed.rejected
		.map { _meta, _clean_csv, qc_json -> qc_json }
		.collect()

	COMPILE_REPORT(passed_metrics_ch, rejected_qc_ch)
}

process CLEAN_AND_QC {
	input:
	tuple val(metadata), path(raw_csv)

	output:
	tuple val(metadata), path("${metadata.instrument_id}_cleaned.csv"), path("${metadata.instrument_id}_qc.json"), emit: qc_results

	script:
	"""
	clean_qc.py ${raw_csv} ${metadata.instrument_id}_cleaned.csv ${metadata.instrument_id}_qc.json
	"""
}

process TRAIN_MODEL {
	input:
	tuple val(meta), path(clean_csv), path(qc_json)

	output:
	tuple val(meta), path("${meta.instrument_id}_model.pkl"), path("${meta.instrument_id}_metrics.json"), emit: model_results

	script:
	"""
	train_model.py ${clean_csv} ${meta.instrument_id} ${meta.instrument_id}_model.pkl ${meta.instrument_id}_metrics.json
	"""
}

process COMPILE_REPORT {
	publishDir "${params.results_dir}", mode: 'copy'

	input:
	path "metrics_dir/*"
	path "rejected_dir/*"

	output:
	path "clinical_summary_report.pdf"

	script:
	"""
    compile_report.py metrics_dir rejected_dir clinical_summary_report.pdf
    """
}
