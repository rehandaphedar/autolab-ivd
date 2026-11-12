# Introduction
A containerized, reactive Nextflow DSL2 pipeline designed for clinical laboratories. It automates pre-analytical interference audits (Serum Indices), autoverifies high-throughput clinical chemistry panels, isolates non-compliant analytical runs, and fits calibrated diagnostic risk models across validated patient cohorts.


# Clinical Rationale & Problem

- In hospital laboratory diagnostics, up to **70% of analytical errors occur during the pre-analytical phase**.
- In-vitro hemolysis (erythrocyte rupture from mechanical trauma or pneumatic tube transport) is the primary cause. Free hemoglobin interferes optically and chemically with clinical chemistry assays (e.g., falsely elevating potassium, AST, and lactate dehydrogenase while invalidating glucose readings).
- ISO 15189 demands strict traceability, pre-analytical sample evaluation, and deterministic result verification.
- `autolab-ivd` implements an automated gatekeeping architecture that screens optical Serum Indices, imputes physiologically bound missing values, branches compromised runs away from diagnostic inference, and outputs an audit-compliant clinical summary report.


# Features

- **Metadata-Aware Streaming:** Every channel carries an immutable `[ meta, file ]` tuple map preserving analyzer ID, batch ID, and operator ID throughout the DAG.
- **Asynchronous Execution & Dynamic Branching:** Rejection criteria are dynamically parsed using Groovy's `JsonSlurper` to route data streams reactively via `.branch`.
- **Fault-Tolerant Fan-In Aggregation:** Uses Nextflow's `.collect()` to aggregate `N` independent, asynchronous process outputs into a single consolidated audit document.
- **Reproducible Containerization:** Analytical steps execute inside a minimal, version-pinned Debian-slim environment tracked via sourcehut CI and pushed to DockerHub.
- **Idempotency & Resumability:** Full cryptographic task-caching support (`-resume`). Unchanged tasks hit cache in < 1 second.

# Dependencies
- Linux or macOS
- Nextflow >= 23.04
- Docker

# Usage

Clone the repository and run the end-to-end pipeline with a single command:

```bash
nextflow run main.nf -profile docker
```

To run with full execution benchmarking and DAG visualization:

```
nextflow run main.nf -profile docker -resume \
    -with-report results/execution_report.html \
    -with-timeline results/timeline.html \
    -with-dag results/dag.png
```

## Output Artifacts

All final deliverables are written to `results/`:

1. `clinical_summary_report.pdf`: The validated quality audit report ready for laboratory medical sign-off.
2. `execution_report.html`: Hardware performance metrics (CPU%, memory peak, process runtime).
3. `timeline.html`: Interactive execution timeline demonstrating asynchronous process scheduling.
