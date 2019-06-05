##DEPENDENCIES:
from SPARQLWrapper import SPARQLWrapper, JSON
#local:
import data
import utility

##CLASSES:
#a collection of SparqlEndpoints
class SparqlDatabase(utility.Database):
    def __init__(self, entries=set):
        utility.Database.__init__(self, entries)
        self.setup() #setup is called on initializing class

    def setup(self):
        for entry in data.sparqlendpoints:
            #entry[2] is {queryname1 : query1, queryname2 : query2, ...}
            keys = entry[2].keys()
            queries = {}
            for key in keys:
                query = SparqlQuery(key, entry[2][key])
                queries.update( {key : query} ) #queries can be found by their name; but then name attribute for SparqlQuery not really needed
            point = SparqlEndpoint(entry[1], entry[0], queries) #entry[1] is name, entry[0] is url
            self.add_entries(set([point]))
                         
#an endpoint with a name, url, and query methods
class SparqlEndpoint:
    def __init__(self, name=str, url=str, queries=dict):
        self.name = name
        self.url = url        
        self.queries = queries

    def set_url(self, url):
        self.url = url
    def get_url(self):
        return self.url

    def set_name(self, name):
        self.name = name
    def get_name(self):
        return self.name

    def set_queries(self, queries):
        self.queries = queries
    def get_queries(self):
        return self.queries

    #returns JSON of query named queryname for searchword
    def search(self, searchword, queryname):
        try:
            query = self.queries[queryname]            
        except KeyError:
            return None
        else:
            query.update(searchword)
            sparql = SPARQLWrapper(self.url)
            sparql.setQuery(query.get())
            sparql.setReturnFormat(JSON)
            data = sparql.query().convert()
            query.reset()
            return data
            
#a specific query with a name to be used with a specific endpoint
class SparqlQuery:
    def __init__(self, name=str, query=str):
        self.name = name #no methods needed
        self.query = query
        self.unmodified = query

    def get(self):
        return self.query

    def update(self, searchword):
            self.query = self.query.replace("!!SEARCHWORD!!", searchword)

    def reset(self):
        self.query = self.unmodified
