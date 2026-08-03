#!/usr/bin/env python3
"""ProvKOS SHACL validation runner.

Generates a violation corpus by mutating the positive case data, then runs
pySHACL (RDFS inference over the ProvKOS ontology) on every dataset.
Positive datasets are expected to conform; each violation dataset is expected
to fail with its designated constraint message.

Usage:  python scripts/run_validation.py
Output: reports/<name>.txt (full validation reports), summary to stdout,
        reports/summary_table.tex (LaTeX table for the paper).
"""
import sys
from pathlib import Path
from rdflib import Graph
from pyshacl import validate

ROOT = Path(__file__).resolve().parent.parent
DATA, SHACL, REPORTS = ROOT / "data", ROOT / "shacl", ROOT / "reports"
VIOL = DATA / "violations"
ONT, SHAPES = ROOT / "ProvKOS.ttl", SHACL / "provkos-shapes.ttl"

# ---------------------------------------------------------------
# 1. Violation corpus: (name, source, triples-to-remove, expected message key)
#    Each mutation deletes exact Turtle lines from a positive dataset.
# ---------------------------------------------------------------
MUTATIONS = [
    ("stw_missing_deprecated_flag", "stw.ttl",
     ["    owl:deprecated true ;"],
     "owl:deprecated"),
    ("ddc_truncation_no_invalidated", "ddc.ttl",
     ["    ProvKOS:wasDeprecatedBy ddc:activity_349268 .",
      "    ProvKOS:wasDeprecatedBy ddc:activity_349268 ."],
     "must invalidate at least one entity"),
    ("ddc_replacement_no_generated", "ddc.ttl",
     ["    prov:wasGeneratedBy ddc:activity_349269 ."],
     "must generate the replacing label"),
    ("ddc_activity_no_warrant", "ddc.ttl",
     ["    ProvKOS:wasWarrantedBy ddc:warrant_epc_143_s30_1 ."],
     "must be justified by at least one Warrant"),
    ("syn_relocation_no_authorized", "synthetic.ttl",
     ["    ProvKOS:wasAuthorizedBy ex:activity_relocation_349210 ."],
     "must authorize the target class number"),
    ("syn_expansion_no_generated", "synthetic.ttl",
     ["    ProvKOS:wasAuthorizedBy ex:activity_expansion_refugees .",
      "    prov:wasGeneratedBy ex:activity_expansion_refugees ."],
     "must generate or authorize at least one entity"),
]


def make_violations():
    VIOL.mkdir(parents=True, exist_ok=True)
    for name, source, removals, _ in MUTATIONS:
        text = (DATA / source).read_text()
        for line in removals:
            if line + "\n" not in text:
                sys.exit(f"[violation-gen] line not found in {source}: {line!r}")
            # remove first occurrence; terminate the preceding statement cleanly
            idx = text.index(line + "\n")
            before = text[:idx]
            after = text[idx + len(line) + 1:]
            # if removed line ended the statement (". "), fix dangling ";"
            if line.rstrip().endswith(".") and before.rstrip().endswith(";"):
                before = before.rstrip()[:-1] + ".\n"
            text = before + after
        (VIOL / f"{name}.ttl").write_text(text)
        Graph().parse(VIOL / f"{name}.ttl")  # must stay parseable
    print(f"[violation-gen] {len(MUTATIONS)} violation datasets written to {VIOL}")


# ---------------------------------------------------------------
# 2. Validation
# ---------------------------------------------------------------
def run_one(data_path: Path):
    data = Graph().parse(data_path)
    conforms, _, report_text = validate(
        data_graph=data,
        shacl_graph=str(SHAPES),
        ont_graph=str(ONT),
        inference="rdfs",
        advanced=True,
    )
    return conforms, report_text


def main():
    make_violations()
    REPORTS.mkdir(exist_ok=True)
    rows, failures = [], 0

    positives = sorted(p for p in DATA.glob("*.ttl"))
    for p in positives:
        conforms, report = run_one(p)
        (REPORTS / f"{p.stem}.txt").write_text(report)
        ok = conforms is True
        rows.append((p.stem, "positive", "conforms", "conforms" if conforms else "VIOLATION", ok))
        failures += (not ok)

    for name, _, _, expected_msg in MUTATIONS:
        p = VIOL / f"{name}.ttl"
        conforms, report = run_one(p)
        (REPORTS / f"{name}.txt").write_text(report)
        ok = (conforms is False) and (expected_msg in report)
        rows.append((name, "violation", f"fails: “{expected_msg}”",
                     "as expected" if ok else ("conforms (!)" if conforms else "wrong message"), ok))
        failures += (not ok)

    w = max(len(r[0]) for r in rows) + 2
    print(f"\n{'dataset'.ljust(w)}{'kind'.ljust(11)}{'result'}")
    for name, kind, _, result, ok in rows:
        print(f"{name.ljust(w)}{kind.ljust(11)}{'PASS' if ok else 'FAIL'} ({result})")
    print(f"\n{len(rows)} checks, {len(rows)-failures} passed, {failures} failed.")

    # LaTeX summary for the paper
    tex = ["\\begin{tabular}{llll}", "\\toprule",
           "Dataset & Kind & Expected & Observed \\\\", "\\midrule"]
    for name, kind, expected, result, ok in rows:
        nm = name.replace("_", "\\_")
        exp = "conforms" if kind == "positive" else "targeted violation"
        obs = result.replace("“", "").replace("”", "")
        tex.append(f"{nm} & {kind} & {exp} & {obs} \\\\")
    tex += ["\\bottomrule", "\\end{tabular}"]
    (REPORTS / "summary_table.tex").write_text("\n".join(tex))
    print(f"LaTeX summary written to {REPORTS/'summary_table.tex'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
