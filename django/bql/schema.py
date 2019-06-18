""" schema.py """

import time
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from typing import List, Set, Dict, Tuple, Optional

import graphene

from .skosmos import SkosmosInstance, SkosmosDatabase   # local
from .sparql import SparqlEndpoint, SparqlDatabase      # local
     
class SparqlResult(graphene.ObjectType):
    """ Result of a SPARQL query """
    subject = graphene.String(description='Subject')
    term = graphene.String(description='Term')
    parents = graphene.String(description='Parents')
    descr = graphene.String(description='Descr')
    scopenote = graphene.String(description='ScopeNote')
    type_ = graphene.String(description='Type')
    extrakind = graphene.String(description='ExtraType')

class SkosmosResult(graphene.ObjectType):
    """ Result of a Skosmos query """
    uri = graphene.String(description='URI')
    type_ = graphene.List(graphene.String, description='type')
    preflabel = graphene.String(description='http://www.w3.org/2004/02/skos/core#prefLabel')
    altlabel = graphene.String(description='http://www.w3.org/2004/02/skos/core#altLabel')
    hiddenlabel = graphene.String(description='http://www.w3.org/2004/02/skos/core#hiddenLabel')
    lang = graphene.String(description='language')
    notation = graphene.String(description='http://www.w3.org/2004/02/skos/core#notation')
    vocab = graphene.String(description='vocabulary')
    exvocab = graphene.String(description='???')

class Helper:
    """ Helps to call pool.map(function, iterable) by enabling function to pass variable(s) to iterable"""

    def __init__(self, searchword: str = None, queryname: str = None, store: list = []) -> None:
        self.searchword = searchword
        self.queryname = queryname
        self.store = store # cumulative over all searched entries

    def skosmos(self, entry: SkosmosInstance) -> None:
        """ Seach entry for searchword and store 'results' """
        data = entry.search(self.searchword)
        try:
            results = data['results']
        except KeyError:
            print (f"KeyError: schema.Helper.skosmos: {entry.name} data for {self.searchword} has no 'results'")
        self.store = self.store + results
 
    def sparql(self, entry: SparqlEndpoint) -> None:
        """ Call queryname for searchword and store 'bindings' """
        data = entry.search(self.searchword, self.queryname)
        try:
            bindings = data['results']['bindings'] # development: perhaps vars should also be stored, data['head']['vars']
        except KeyError:
            print (f"KeyError: schema.Helper.sparql: {entry.name} data for {self.searchword} has no 'results'")
        self.store = self.store + bindings

    def get_store(self):
        return self.store    

class Query(graphene.ObjectType):
    """ Schema """    

    results_skosmos = graphene.List(SkosmosResult,
                                    searchword=graphene.String(required=True))
    """ Skosmos query type """
    def resolve_results_skosmos(self, info, searchword):
        """ Resolve Skosmos query type """
        pool = ThreadPool()
        base = SkosmosDatabase()
        entries = base.get_entries()
        helper = Helper(searchword) 
        pool.map(helper.skosmos, entries)
        pool.close()
        pool.join()
        return Normalize.skosmos(({'results':helper.get_store()}))

    results_sparql = graphene.List(SparqlResult,
                                   searchword=graphene.String(required=True),
                                   queryname=graphene.String(required=True))

    """ SPARQL query type """
    def resolve_results_sparql(self, info, searchword, queryname):
        """ Resolve SPARQL query type """
        pool = ThreadPool()
        base = SparqlDatabase()
        endpoints = base.get_entries()
        helper = Helper(searchword, queryname) 
        pool.map(helper.sparql, endpoints)
        pool.close()
        pool.join()
        return Normalize.sparql(({'results' : {'bindings':helper.store}}))

    results_skosmos_timed = graphene.List(SkosmosResult,
                                    searchword=graphene.String(required=True))  

    # development
    """ Skosmos timed query type """
    def resolve_results_skosmos_timed(self, info, searchword):                  
        """ Resolve Skosmos timed query type """
        start = time.time() # timer
        pool = ThreadPool()
        base = SkosmosDatabase()
        entries = base.get_entries()        
        helper = Helper(searchword) 
        pool.map(helper.skosmos, entries)
        pool.close()
        pool.join()
        result = Normalize.skosmos(({'results':helper.get_store()}))
        end = time.time()   # timer
        print(end - start)  # timer
        return result

    results_sparql_timed = graphene.List(SparqlResult,
                                   searchword=graphene.String(required=True),
                                   queryname=graphene.String(required=True))

    """ SPARQL timed query type """
    def resolve_results_sparql_timed(self, info, searchword, queryname):
        """ Resolve SPARQL timed query type """
        start = time.time() # timer
        pool = ThreadPool()
        base = SparqlDatabase()
        endpoints = base.get_entries()
        helper = Helper(searchword, queryname) 
        pool.map(helper.sparql, endpoints)
        pool.close()
        pool.join()
        result = Normalize.sparql(({'results' : {'bindings':helper.store}}))
        end = time.time()   # timer
        print(end - start)  # timer
        return result
    #/developtment

class Normalize():
    """ Collection of normalizing methods """
    
    @classmethod
    def skosmos(self, data: dict) -> List[SkosmosResult]:
        """ Prepare data for Skosmos resolver """
        normalized = []
        labels = ['uri', 'type', 'prefLabel', 'altLabel', 'hiddenLabel', 'lang', 'notation', 'vocab', 'exvocab']
        try:
            data['results']
        except KeyError:
            print (f"KeyError: schema.Normalize.skosmos: Data without 'results'")
        else:
            for entry in data['results']:
                for label in labels:
                    try:
                        entry[label]
                    except KeyError:
                        entry[label] = None # missing labels are added and set to None
                normalized.append(SkosmosResult(uri=entry['uri'],
                                type_=entry['type'],
                                preflabel=entry['prefLabel'],
                                altlabel=entry['altLabel'],
                                hiddenlabel=entry['hiddenLabel'],
                                lang=entry['lang'],
                                notation=entry['notation'],
                                vocab=entry['vocab'],
                                exvocab=entry['exvocab']))
            return normalized

    @classmethod
    def sparql(self, data: dict) -> List[SparqlResult]:
        """ Prepare data for Sparql resolver """
        normalized = []
        variables = ['Subject', 'Term', 'Parents', 'Descr', 'ScopeNote', 'Type', 'ExtraType']
        try:
            data['results']
        except KeyError:
            print (f"KeyError: schema.Normalize.sparql: Data without 'results'")
        else:
            for entry in data['results']['bindings']:
                for variable in variables:
                    try:
                        entry[variable]
                    except KeyError:
                        entry[variable] = None
                normalized.append(SparqlResult(subject=entry['Subject'],
                                               term=entry['Term'],
                                               parents=entry['Parents'],
                                               descr=entry['Descr'],
                                               scopenote=entry['ScopeNote'],
                                               type_=entry['Type'],
                                               extrakind=entry['ExtraType']))
            return normalized       


