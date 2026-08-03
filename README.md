# ProvKOS — Development Repository

**An Application Profile for Documenting Provenance in Knowledge Organization Systems**

ProvKOS extends the W3C [SKOS](https://www.w3.org/TR/skos-reference/) and [PROV-O](https://www.w3.org/TR/prov-o/) standards to represent the provenance of *editorial activities* in Knowledge Organization Systems (KOS): not only what changed between versions, but why a change was made, who authorized it, and what evidence warranted it.

This is the **development repository**: ontology sources, case-study data, SHACL shapes, and validation tooling.
The **published documentation** is served from the persistent namespace URI **https://w3id.org/def/ProvKOS** (repository: [provkos/Ontology](https://github.com/provkos/Ontology)).

## The profile at a glance

- **Typed editorial activities** — `Relocation`, `Expansion`, `Truncation`, `Replacement` — for classification-specific composite operations that existing ontologies cannot express. Operations already expressible with PROV-O core properties (additions via `prov:wasGeneratedBy`, retirements via `prov:wasInvalidatedBy`, scope changes via `prov:wasInfluencedBy`) deliberately reuse PROV-O directly (*reuse before mint*).
- **A structured Warrant hierarchy** — `ProvKOS:Document` and `ProvKOS:Literature`, together with `skos:Concept` and `skos:ConceptScheme` declared as warrant types — for the heterogeneous sources that justify editorial decisions.
- **Warrant chains** via `ProvKOS:cite`, linking layered evidence.
- **PROV-O sub-property alignments** (`wasDeprecatedBy` ⊑ `prov:wasInvalidatedBy`, `wasAuthorizedBy` ⊑ `prov:wasGeneratedBy`, `wasWarrantedBy` ⊑ `prov:wasInfluencedBy`), which are load-bearing during validation: constraints written once at the PROV-O level apply to classification systems and thesauri alike.

## Namespace

```
@prefix ProvKOS: <https://w3id.org/def/ProvKOS#> .
```

## Repository contents

| Path | Description |
|---|---|
| `ProvKOS.ttl` | Ontology source (TBox), Turtle. Canonical development version. |
| `data/` | Case-study datasets (TGN, STW, DDC) and a supplementary dataset exercising Relocation and Expansion; `data/violations/` holds the auto-generated violation corpus. |
| `shacl/provkos-shapes.ttl` | SHACL shapes for all four typed activities plus the shared warrant constraint. |
| `scripts/run_validation.py` | Regenerates the violation corpus and runs pySHACL over all datasets. |
| `scripts/run_queries.py` | Executes the paper's SPARQL queries against the case data and checks the results. |
| `reports/` | Validation reports and a LaTeX summary table. |
| `VALIDATION.md` | Validation protocol, environment, and results. |

## Validation

```bash
pip install -r requirements.txt   # rdflib 7.6.0, pySHACL 0.40.1
python scripts/run_validation.py  # exit code 0 iff all checks pass
python scripts/run_queries.py
```

Validation runs with RDFS inference over the ontology so that the profile's sub-property and subclass alignments take effect. See `VALIDATION.md` for details and current results.

## Releasing

Ontology (TBox) changes are published by regenerating the WIDOCO documentation and committing it, together with the RDF/XML serialization, to [provkos/Ontology](https://github.com/provkos/Ontology), which serves https://w3id.org/def/ProvKOS. Changes limited to SHACL shapes, data, or scripts stay in this repository.

## Citation

If you use ProvKOS, please cite:

> Choi, I., & Cheng, Y.-Y. ProvKOS: An Application Profile for Documenting Provenance in Knowledge Organization Systems. *(under review)*

## Authors

- Inkyung Choi — Sungkyunkwan University ([ORCID 0000-0001-5048-8516](https://orcid.org/0000-0001-5048-8516))
- Yi-Yun Cheng — Rutgers University ([ORCID 0000-0001-6123-7595](https://orcid.org/0000-0001-6123-7595))
