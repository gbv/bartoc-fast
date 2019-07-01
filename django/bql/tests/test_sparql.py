""" A test for sparql.py """

from django.test import SimpleTestCase

import json
from SPARQLWrapper import (SPARQLWrapper, JSON)

from ..sparql import SparqlDatabase, SparqlEndpoint, SparqlQuery # local

SEARCHWORDS_a = ["bike", "fahrrad", "velo", "rennvelo"]
SEARCHWORDS_b = ["oil", "fire", "language"]
QUERYSTRING_0 = """
        select ?Subject ?Term ?Parents ?Descr ?ScopeNote ?Type (coalesce(?Type1,?Type2) as ?ExtraType) {
        ?Subject luc:term "!!!SEARCHWORD!!!"; a ?typ.
        ?typ rdfs:subClassOf gvp:Subject; rdfs:label ?Type.
        filter (?typ != gvp:Subject)
        optional {?Subject gvp:placeTypePreferred [gvp:prefLabelGVP [xl:literalForm ?Type1]]}
        optional {?Subject gvp:agentTypePreferred [gvp:prefLabelGVP [xl:literalForm ?Type2]]}
        optional {?Subject gvp:prefLabelGVP [xl:literalForm ?Term]}   
        optional {?Subject gvp:parentStringAbbrev ?Parents}
        optional {?Subject foaf:focus/gvp:biographyPreferred/schema:description ?Descr}
        optional {?Subject skos:scopeNote [dct:language gvp_lang:en; rdf:value ?ScopeNote]}}
        """
QUERYSTRING_1 = """
        select ?x ?label {
        ?x luc:term "!!!SEARCHWORD!!!";
        gvp:prefLabelGVP/xl:literalForm ?label.
        filter exists {
        ?x (xl:prefLabel|xl:altLabel)/gvp:term ?term.
        filter (lcase(str(?term))="!!!SEARCHWORD!!!" && langMatches(lang(?term),"en"))}}
        """
     
class TestSparqlQuery_a(SimpleTestCase):
    
    def setUp(self) -> None:
        self.sparqlquery = SparqlQuery(QUERYSTRING_0, "Description: bla", 0)

    def test_update(self) -> None:
        """ Ensure that update and reset work """
        
        initial = self.sparqlquery.querystring
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
        self.sparqlquery.update("bike")
        self.assertEqual(self.sparqlquery.querystring, correct_bike, "ERROR: SparqlQuery.update")
        self.sparqlquery.reset()
        self.sparqlquery.update("fahrrad")
        self.assertEqual(self.sparqlquery.querystring, correct_fahrrad, "ERROR: SparqlQuery.update")
        self.sparqlquery.reset()
        self.assertEqual(self.sparqlquery.querystring, initial, "ERROR: SparqlQuery.update")

class TestSparqlQuery_b(SimpleTestCase):
    
    def setUp(self) -> None:
        self.sparqlquery = SparqlQuery(QUERYSTRING_1, "Description: 1", 1)

    def test_update(self) -> None:
        """ Ensure that update and reset work """
        
        initial = self.sparqlquery.querystring
        correct_oil = """
        select ?x ?label {
        ?x luc:term "oil";
        gvp:prefLabelGVP/xl:literalForm ?label.
        filter exists {
        ?x (xl:prefLabel|xl:altLabel)/gvp:term ?term.
        filter (lcase(str(?term))="oil" && langMatches(lang(?term),"en"))}}
        """
        correct_fire = """
        select ?x ?label {
        ?x luc:term "fire";
        gvp:prefLabelGVP/xl:literalForm ?label.
        filter exists {
        ?x (xl:prefLabel|xl:altLabel)/gvp:term ?term.
        filter (lcase(str(?term))="fire" && langMatches(lang(?term),"en"))}}
        """
        self.sparqlquery.update("oil")
        self.assertEqual(self.sparqlquery.querystring, correct_oil, "ERROR: SparqlQuery.update")
        self.sparqlquery.reset()
        self.sparqlquery.update("fire")
        self.assertEqual(self.sparqlquery.querystring, correct_fire, "ERROR: SparqlQuery.update")
        self.sparqlquery.reset()
        self.assertEqual(self.sparqlquery.querystring, initial, "ERROR: SparqlQuery.update")

class TestSparqlEndpoint(SimpleTestCase):
    
    def setUp(self) -> None:
        self.sparqlendpoint = SparqlEndpoint("Test Getty endpoint",
                                             "http://vocab.getty.edu/sparql",
                                             [SparqlQuery(QUERYSTRING_0, "Description: 0", 0),
                                              SparqlQuery(QUERYSTRING_1, "Description: 1", 1)
                                              ])

    def test_search_a(self) -> None:
        """ Ensure validity of search results """
        
        for searchword in SEARCHWORDS_a:
            result_default = self.sparqlendpoint.search(searchword)
            result_0 = self.sparqlendpoint.search(searchword, 0)
                                             
            with open(f'//itsc-pg2.storage.p.unibas.ch/ub-home$/hinder0000/Documents/GitHub/bartoc-graphql/django/bql/tests/files/sparql_0_{searchword}.json', encoding="utf-8") as file: 
                correct_result = json.load(file)
                file.close()
                self.assertEqual(result_default.data, correct_result, "ERROR: SparqlEndpoint.search, default")
                self.assertEqual(result_0.data, correct_result, "ERROR: SparqlEndpoint.search, 0")

    def test_search_b(self) -> None:
        """ Ensure validity of search results """
                
        for searchword in SEARCHWORDS_b:
            result_1 = self.sparqlendpoint.search(searchword, 1)

            with open(f'//itsc-pg2.storage.p.unibas.ch/ub-home$/hinder0000/Documents/GitHub/bartoc-graphql/django/bql/tests/files/sparql_1_{searchword}.json', encoding="utf-8") as file:
                correct_result = json.load(file)
                file.close()
                self.assertEqual(result_1.data, correct_result, "ERROR: SparqlEndpoint.search, 1")

class TestSparqlDatabase(SimpleTestCase):

    def setUp(self) -> None:
        self.sparqldatabase = SparqlDatabase() 
        
    def test_setup(self) -> None:
        """ Ensure that all languages have been added from fixtures """
        
        self.assertEqual(len(self.sparqldatabase.entries), 2, "ERROR: SparqlDatabase.setup") # check fixtures/sparqlendpoints.xlsx to see how many endpoints there should be

        for endpoint in self.sparqldatabase.entries:
            print(endpoint.name)
            for query in endpoint.queries:
                print(query.querystring)
                print(query.description)

    def test_xlsx(self):
        """ Ensure that data from excel is parsed correctly """

        endpoint = self.sparqldatabase.select("Getty")

        for searchword in SEARCHWORDS_a:
            result_default = endpoint.search(searchword)
            result_0 = endpoint.search(searchword, 0)

            with open(f'//itsc-pg2.storage.p.unibas.ch/ub-home$/hinder0000/Documents/GitHub/bartoc-graphql/django/bql/tests/files/sparql_0_{searchword}.json', encoding="utf-8") as file: 
                correct_result = json.load(file)
                file.close()
                self.assertEqual(result_default.data, correct_result, "ERROR: SparqlEndpoint.search, default")
                self.assertEqual(result_0.data, correct_result, "ERROR: SparqlEndpoint.search, 0")
        
    def test_search(self) -> None:       
        pass


    



