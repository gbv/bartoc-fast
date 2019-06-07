""" A test for sparql.py """

import sys
sys.path.append('//itsc-pg2.storage.p.unibas.ch/ub-home$/hinder0000/Documents/GitHub/bartoc-graphql/app')
import json
import sparql # local
import data   # local

searchwords = ["bike", "fahrrad", "velo", "rennvelo"]
url = "http://vocab.getty.edu/sparql"
name = "Getty Vocabularies"
query = """
        select ?Subject ?Term ?Parents ?Descr ?ScopeNote ?Type (coalesce(?Type1,?Type2) as ?ExtraType) {
        ?Subject luc:term "!!SEARCHWORD!!"; a ?typ.
        ?typ rdfs:subClassOf gvp:Subject; rdfs:label ?Type.
        filter (?typ != gvp:Subject)
        optional {?Subject gvp:placeTypePreferred [gvp:prefLabelGVP [xl:literalForm ?Type1]]}
        optional {?Subject gvp:agentTypePreferred [gvp:prefLabelGVP [xl:literalForm ?Type2]]}
        optional {?Subject gvp:prefLabelGVP [xl:literalForm ?Term]}   
        optional {?Subject gvp:parentStringAbbrev ?Parents}
        optional {?Subject foaf:focus/gvp:biographyPreferred/schema:description ?Descr}
        optional {?Subject skos:scopeNote [dct:language gvp_lang:en; rdf:value ?ScopeNote]}}
        """
queryname = "http://vocab.getty.edu/queries#Full_Text_Search_Query" 

def test_SparqlQuery():
    initial = query
    correct_bike = """
        select ?Subject ?Term ?Parents ?Descr ?ScopeNote ?Type (coalesce(?Type1,?Type2) as ?ExtraType) {
        ?Subject luc:term "bike"; a ?typ.
        ?typ rdfs:subClassOf gvp:Subject; rdfs:label ?Type.
        filter (?typ != gvp:Subject)
        optional {?Subject gvp:placeTypePreferred [gvp:prefLabelGVP [xl:literalForm ?Type1]]}
        optional {?Subject gvp:agentTypePreferred [gvp:prefLabelGVP [xl:literalForm ?Type2]]}
        optional {?Subject gvp:prefLabelGVP [xl:literalForm ?Term]}   
        optional {?Subject gvp:parentStringAbbrev ?Parents}
        optional {?Subject foaf:focus/gvp:biographyPreferred/schema:description ?Descr}
        optional {?Subject skos:scopeNote [dct:language gvp_lang:en; rdf:value ?ScopeNote]}}
        """
    correct_fahrrad = """
        select ?Subject ?Term ?Parents ?Descr ?ScopeNote ?Type (coalesce(?Type1,?Type2) as ?ExtraType) {
        ?Subject luc:term "fahrrad"; a ?typ.
        ?typ rdfs:subClassOf gvp:Subject; rdfs:label ?Type.
        filter (?typ != gvp:Subject)
        optional {?Subject gvp:placeTypePreferred [gvp:prefLabelGVP [xl:literalForm ?Type1]]}
        optional {?Subject gvp:agentTypePreferred [gvp:prefLabelGVP [xl:literalForm ?Type2]]}
        optional {?Subject gvp:prefLabelGVP [xl:literalForm ?Term]}   
        optional {?Subject gvp:parentStringAbbrev ?Parents}
        optional {?Subject foaf:focus/gvp:biographyPreferred/schema:description ?Descr}
        optional {?Subject skos:scopeNote [dct:language gvp_lang:en; rdf:value ?ScopeNote]}}
        """
    testquery = sparql.SparqlQuery(initial)   
    testquery.update("bike")
    assert testquery.get() == correct_bike, "SparqlQuery.update failure"
    testquery.reset()
    assert testquery.get() == initial, "SparqlQuery.reset failure"
    testquery.update("fahrrad")
    assert testquery.get() == correct_fahrrad, "SparqlQuery.update failure"
    testquery.reset()
    assert testquery.get() == initial, "SparqlQuery.reset failure"

def test_SparqlEndpoint():
    testendpoint = sparql.SparqlEndpoint(name, url, {queryname : sparql.SparqlQuery(query)})
    for searchword in searchwords:
        result = testendpoint.search(searchword, queryname)
        with open(f'files/sparql_{searchword}.json', encoding="utf-8") as file:
            correct_result = json.load(file)
            file.close()
            assert str(result) == str(correct_result), "SparqlEndpoint.search failure" # compare str since dict comparison is hard     
           
def test_SparqlDatabase():
    testbase = sparql.SparqlDatabase([])
    urlsprocessed = []
    for endpoint in testbase.get_entries():
        assert type(endpoint) == sparql.SparqlEndpoint, "SparqlDatabase.setup failure: wrong type"
        urlsprocessed.append(endpoint.get_url())
    urlsraw = []
    for entry in data.sparqlendpoints:
        urlsraw.append(entry[0])
    assert set(urlsprocessed) == set(urlsraw), "SparqlDatabase.setup failure: incomplete"

def test_sparql():
    testbase = sparql.SparqlDatabase([])
    for endpoint in testbase.get_entries():
        for querydict in endpoint.get_queries():
            for searchword in searchwords:
                endpoint.search(searchword, [*querydict][0]) # add file checking here
    
test_SparqlQuery()
test_SparqlEndpoint()
test_SparqlDatabase()
test_sparql()

