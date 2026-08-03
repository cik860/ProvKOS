#!/usr/bin/env python3
"""Execute the paper's SPARQL queries (revised versions) against the case data
and compare row counts with the tables reported in the manuscript."""
from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parent.parent

def load(*files):
    g = Graph()
    g.parse(ROOT / "ProvKOS.ttl")
    for f in files:
        g.parse(ROOT / "data" / f)
    return g

PREFIXES = """
PREFIX ProvKOS: <https://w3id.org/def/ProvKOS#>
PREFIX prov:    <http://www.w3.org/ns/prov#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos:    <http://www.w3.org/2004/02/skos/core#>
PREFIX skosxl:  <http://www.w3.org/2008/05/skos-xl#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX owl:     <http://www.w3.org/2002/07/owl#>
PREFIX tgn:     <http://example.org/tgn/>
"""

QUERIES = [
    ("TGN Query 1 (warrants for 'Gulf of America')", "tgn.ttl", 4, """
        SELECT ?warrantLabel ?warrantType WHERE {
            ?label skosxl:literalForm "Gulf of America"@en ;
                   prov:wasGeneratedBy ?activity .
            ?activity ProvKOS:wasWarrantedBy ?concept .
            ?concept ProvKOS:cite ?warrant .
            ?warrant rdfs:label ?warrantLabel ; a ?warrantType .
            FILTER (?warrantType IN
                (ProvKOS:Document, ProvKOS:Literature, skos:ConceptScheme))
        }"""),
    ("TGN Query 2 (concept schemes in record 7021009)", "tgn.ttl", None, """
        SELECT DISTINCT ?schemeLabel WHERE {
            tgn:7021009 ProvKOS:hasLabel ?label .
            ?label prov:wasGeneratedBy ?activity .
            ?activity ProvKOS:wasWarrantedBy ?concept .
            ?concept a skos:Concept ; ProvKOS:cite ?scheme .
            ?scheme a skos:ConceptScheme ; rdfs:label ?schemeLabel .
        } ORDER BY ?schemeLabel"""),
    ("TGN Query 3 (schemes per label, revised)", "tgn.ttl", 3, """
        SELECT DISTINCT ?labelText ?schemeLabel WHERE {
            tgn:7021009 ProvKOS:hasLabel ?label .
            ?label a skosxl:Label ;
                   skosxl:literalForm ?labelText ;
                   prov:wasGeneratedBy ?activity .
            ?activity ProvKOS:wasWarrantedBy ?concept .
            ?concept a skos:Concept ; ProvKOS:cite ?scheme .
            ?scheme a skos:ConceptScheme ; rdfs:label ?schemeLabel .
        } ORDER BY ?labelText ?schemeLabel"""),
    ("STW bridge query (deltas + warrants)", "stw.ttl", 1, """
        SELECT ?deprecatedLabel ?replacedByLabel ?activityType ?warrantDoc ?agent WHERE {
            ?deprecated owl:deprecated true ;
                skos:prefLabel ?deprecatedLabel ;
                dcterms:isReplacedBy ?replacement .
            ?replacement skos:prefLabel ?replacedByLabel .
            FILTER (lang(?deprecatedLabel) = "en")
            FILTER (lang(?replacedByLabel) = "en")
            ?deprecated prov:wasInvalidatedBy ?activity .
            ?activity a ?activityType ;
                ProvKOS:wasWarrantedBy ?warrant ;
                prov:wasAssociatedWith ?agentNode .
            ?warrant rdfs:label ?warrantDoc .
            ?agentNode rdfs:label ?agent .
            FILTER (?activityType = ProvKOS:Truncation)
        }"""),
    ("DDC cross-activity query (shared warrant)", "ddc.ttl", None, """
        SELECT ?activity ?activityType ?deprecatedEntity ?influencedEntity WHERE {
            ?activity ProvKOS:wasWarrantedBy
                <http://example.org/dewey/warrant_epc_143_s30_1> ;
                a ?activityType .
            FILTER (?activityType IN (ProvKOS:Replacement,
                ProvKOS:Truncation, ProvKOS:Expansion, ProvKOS:Relocation))
            OPTIONAL { ?deprecatedEntity ProvKOS:wasDeprecatedBy ?activity . }
            OPTIONAL { ?influencedEntity prov:wasInfluencedBy ?activity . }
        }"""),
]

for name, datafile, expected, query in QUERIES:
    g = load(datafile)
    rows = list(g.query(PREFIXES + query))
    status = ""
    if expected is not None:
        status = "OK" if len(rows) == expected else f"MISMATCH (paper says {expected})"
    print(f"\n=== {name}: {len(rows)} rows {status}")
    for r in rows:
        print("   ", " | ".join(str(v) for v in r))
