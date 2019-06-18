""" sparql.py """

from SPARQLWrapper import (SPARQLWrapper, JSON)

from .data import sparqlendpoints       # local
from .utility import Database, Entry    # local

class SparqlDatabase(Database):
    """ A collection of SPARQL endpoints """
    def __init__(self, entries: set = {}) -> None:
        Database.__init__(self, entries)
        self.setup() # setup is called on initializing class

    def setup(self) -> None:
        """ Populate the database with SPARQL endpoints and their queries """
        for entry in sparqlendpoints:
            keys = entry[2].keys() # entry[2]: {queryname1 : query1, queryname2 : query2, ...}
            queries = {}
            for key in keys:
                query = SparqlQuery(entry[2][key])
                queries.update( {key : query} ) # queries can be found by their name
            point = SparqlEndpoint(entry[1], entry[0], queries) # entry[0]: url, entry[1]: name 
            self.add_entries(set([point]))
                         
class SparqlEndpoint(Entry):
    """ A SPARQL endpoint """
    def __init__(self, name: str, url: str, queries: dict) -> None:
        Entry.__init__(self, name, url)   
        self.queries = queries

    def set_queries(self, queries: dict) -> None:
        self.queries = queries

    def get_queries(self) -> dict:
        return self.queries

    def search(self, searchword: str, queryname: str) -> dict:
        """ Send a queryname-query for searchword to the SPARQL endpoint and returns the results """
        try:
            query = self.queries[queryname]            
        except KeyError:
            return None
        else:
            query.update(searchword)
            sparqlw = SPARQLWrapper(self.url)
            sparqlw.setQuery(query.get())
            sparqlw.setReturnFormat(JSON)
            data = sparqlw.queryAndConvert() # raw JSON not needed, otherwise use: data = sparql.query()
            query.reset()
            return data
            
class SparqlQuery:
    """ A SPARQL query (to be used with a specific endpoint) """
    def __init__(self, query: str) -> None:
        self.query = query
        self.unmodified = query

    def get(self) -> str:
        return self.query

    def update(self, searchword: str) -> None:
        """ Put the searchword into the query """        
        self.query = self.query.replace("!!SEARCHWORD!!", searchword)

    def reset(self) -> None:
        """ Reset to the initial query (w/o searchword) """
        self.query = self.unmodified
