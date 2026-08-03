# ProvKOS SHACL Validation Package

This directory contains the executable validation suite for the ProvKOS
Application Profile, supporting Section 4 of the paper.

## Contents

- `ProvKOS.ttl` — the ontology (v1.1, TBox), including the PROV-O sub-property
  alignments that validation relies on.
- `shacl/provkos-shapes.ttl` — SHACL node shapes for all four typed activities
  (Truncation, Replacement, Relocation, Expansion) plus a shared
  warrant-cardinality constraint.
- `data/tgn.ttl`, `data/stw.ttl`, `data/ddc.ttl` — the three case-study
  datasets from the paper (revised listings).
- `data/synthetic.ttl` — synthetic data exercising Relocation and Expansion,
  which the case studies do not cover.
- `data/violations/` — six violation datasets, generated automatically by
  mutating the positive data (one targeted constraint violation each).
- `scripts/run_validation.py` — regenerates the violation corpus and runs
  pySHACL over all ten datasets.
- `scripts/run_queries.py` — executes the paper's SPARQL queries against the
  case data and compares row counts with the reported tables.
- `reports/` — validation reports per dataset and a LaTeX summary table.

## Reproduction

```bash
pip install -r requirements.txt   # rdflib 7.6.0, pySHACL 0.40.1
python scripts/run_validation.py  # exit code 0 iff all 10 checks pass
python scripts/run_queries.py
```

Validation runs with RDFS inference over the ontology
(`pyshacl ... inference='rdfs'`). Inference makes the profile's sub-property
alignments effective: constraints are written once against the PROV-O
super-properties (`prov:wasInvalidatedBy`, `prov:wasGeneratedBy`) and apply
both to classification systems using the ProvKOS sub-properties
(`wasDeprecatedBy`, `wasAuthorizedBy`) and to thesauri using PROV-O directly.

## Results (2026-08-03)

All 10 checks pass: the 4 positive datasets conform, and each of the 6
violation datasets fails with its targeted constraint message
(see `reports/summary_table.tex`).

| Dataset | Kind | Result |
|---|---|---|
| tgn / stw / ddc / synthetic | positive | conforms |
| stw_missing_deprecated_flag | violation | fails: owl:deprecated integrity |
| ddc_truncation_no_invalidated | violation | fails: Truncation cardinality |
| ddc_replacement_no_generated | violation | fails: Replacement pairing |
| ddc_activity_no_warrant | violation | fails: warrant cardinality |
| syn_relocation_no_authorized | violation | fails: Relocation pairing |
| syn_expansion_no_generated | violation | fails: Expansion cardinality |
