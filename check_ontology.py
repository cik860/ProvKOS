"""Validate the revised ProvKOS ontology: parse, structural checks, inference tests."""
from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef
import owlrl

PROVKOS = Namespace("https://w3id.org/def/ProvKOS#")
PROV = Namespace("http://www.w3.org/ns/prov#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SKOSXL = Namespace("http://www.w3.org/2008/05/skos-xl#")

# 1. Parse
g = Graph()
g.parse("ProvKOS-FINAL-revised.ttl", format="turtle")
print(f"[1] Parse OK — {len(g)} triples")

# 2. No references to old names / internal hosts
bad = []
for s, p, o in g:
    for term in (s, p, o):
        t = str(term)
        if "Class_number" in t:
            bad.append(("old class name", t))
        if "oclc.org" in t or "dewey.org" in t:
            bad.append(("internal host", t))
raw = open("ProvKOS-FINAL-revised.ttl").read()
for token in ("Class_number", "oclc.org", "dewey.org", "Acitivty"):
    if token in raw:
        bad.append(("in raw text", token))
print(f"[2] Legacy-name / internal-host check: {'CLEAN' if not bad else bad}")

# 3. Key axioms present
checks = {
    "hasLabel domain = prov:Entity": (PROVKOS.hasLabel, RDFS.domain, PROV.Entity),
    "wasAuthorizedBy subPropertyOf prov:wasGeneratedBy": (PROVKOS.wasAuthorizedBy, RDFS.subPropertyOf, PROV.wasGeneratedBy),
    "wasDeprecatedBy subPropertyOf prov:wasInvalidatedBy": (PROVKOS.wasDeprecatedBy, RDFS.subPropertyOf, PROV.wasInvalidatedBy),
    "wasWarrantedBy subPropertyOf prov:wasInfluencedBy": (PROVKOS.wasWarrantedBy, RDFS.subPropertyOf, PROV.wasInfluencedBy),
    "skos:Concept subClassOf Warrant": (SKOS.Concept, RDFS.subClassOf, PROVKOS.Warrant),
    "skos:ConceptScheme subClassOf Warrant": (SKOS.ConceptScheme, RDFS.subClassOf, PROVKOS.Warrant),
    "skos:Concept declared owl:Class": (SKOS.Concept, RDF.type, OWL.Class),
    "ClassNumber subClassOf prov:Entity": (PROVKOS.ClassNumber, RDFS.subClassOf, PROV.Entity),
}
for name, triple in checks.items():
    print(f"[3] {name}: {'OK' if triple in g else 'MISSING!'}")

# 4. Axioms that must be ABSENT
absent = {
    "Entity disjointWith Warrant removed": (PROV.Entity, OWL.disjointWith, PROVKOS.Warrant),
    "skos:notation domain removed": (SKOS.notation, RDFS.domain, None),
}
for name, (s, p, o) in absent.items():
    hits = list(g.triples((s, p, o)))
    print(f"[4] {name}: {'OK (absent)' if not hits else 'STILL PRESENT: ' + str(hits)}")

# 5. Inference test with mini ABox
test = """
@prefix : <https://w3id.org/def/ProvKOS#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix skosxl: <http://www.w3.org/2008/05/skos-xl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex: <http://example.org/> .

# TGN-style: authority record typed only as prov:Entity, with a label
ex:tgn7021009 a prov:Entity ; :hasLabel ex:gulfLabel .
ex:gulfLabel a skosxl:Label ; skosxl:literalForm "Gulf of America"@en ;
    prov:wasGeneratedBy ex:act1 .
ex:act1 a prov:Activity ; :wasWarrantedBy ex:conceptAmerica .
ex:conceptAmerica a skos:Concept ; :cite ex:nytArticle .
ex:nytArticle a :Literature .

# A Document warrant that is ALSO a prov:Entity (previously clashed with disjointness)
ex:epcDoc a :Document , prov:Entity .

# DDC-style truncation
ex:cn30482 a :ClassNumber ; :wasDeprecatedBy ex:act2 .
ex:act2 a :Truncation .
"""
data = Graph()
data.parse("ProvKOS-FINAL-revised.ttl", format="turtle")
data.parse(data=test, format="turtle")
owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(data)

ex = Namespace("http://example.org/")
tgn_is_cn = (ex.tgn7021009, RDF.type, PROVKOS.ClassNumber) in data
print(f"[5] TGN record NOT inferred as ClassNumber: {'OK' if not tgn_is_cn else 'FAIL — still inferred as ClassNumber'}")

# subproperty inference: wasDeprecatedBy -> prov:wasInvalidatedBy
dep_inf = (ex.cn30482, PROV.wasInvalidatedBy, ex.act2) in data
print(f"[5] wasDeprecatedBy entails prov:wasInvalidatedBy: {'OK' if dep_inf else 'FAIL'}")

# wasWarrantedBy -> prov:wasInfluencedBy
war_inf = (ex.act1, PROV.wasInfluencedBy, ex.conceptAmerica) in data
print(f"[5] wasWarrantedBy entails prov:wasInfluencedBy: {'OK' if war_inf else 'FAIL'}")

# consistency: OWL-RL flags inconsistency by adding owl:Nothing memberships / error triples
nothing_members = list(data.subjects(RDF.type, OWL.Nothing))
print(f"[5] Consistency (no owl:Nothing members): {'OK' if not nothing_members else 'INCONSISTENT: ' + str(nothing_members)}")

# skos:Concept warrant inference: conceptAmerica should be a Warrant
w_inf = (ex.conceptAmerica, RDF.type, PROVKOS.Warrant) in data
print(f"[5] skos:Concept instance inferred as Warrant: {'OK' if w_inf else 'FAIL'}")
