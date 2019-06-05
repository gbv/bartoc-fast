##DEPENDENDIES:
import graphene
import time
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
#local:
import skosmos
import sparql

##SCHEMA:

class SparqlResult(graphene.ObjectType):
    subject = graphene.String(description='Subject')
    term = graphene.String(description='Term')
    parents = graphene.String(description='Parents')
    descr = graphene.String(description='Descr')
    scopenote = graphene.String(description='ScopeNote')
    kind = graphene.String(description='Type')
    extrakind = graphene.String(description='ExtraType')

class SkosmosResult(graphene.ObjectType):
    uri = graphene.String(description='URI')
    kind = graphene.List(graphene.String, description='type')
    preflabel = graphene.String(description='http://www.w3.org/2004/02/skos/core#prefLabel')
    altlabel = graphene.String(description='http://www.w3.org/2004/02/skos/core#altLabel')
    hiddenlabel = graphene.String(description='http://www.w3.org/2004/02/skos/core#hiddenLabel')
    lang = graphene.String(description='language')
    notation = graphene.String(description='http://www.w3.org/2004/02/skos/core#notation')
    vocab = graphene.String(description='vocabulary')
    exvocab = graphene.String(description='???')


##RESOLVER:

class Query(graphene.ObjectType):

#SPARQL:

    results_sparql = graphene.List(SparqlResult,
                                   searchword=graphene.String(required=True),
                                   queryname=graphene.String(required=True))
    def resolve_results_sparql(self, info, searchword, queryname):
        start = time.time() #timer
        base = sparql.SparqlDatabase([])
        endpoints = base.get_entries() #set of SparqlEndpoints
        data = []
        for endpoint in endpoints:#aggregate data before or after normalizing??
            jsondata = endpoint.search(searchword, queryname)
            normalized = normalize_sparql(jsondata)
            data = data + normalized
        end = time.time() #timer
        print(end - start)#timer
        return data 

#SKOSMOS:

    results_standard = graphene.List(SkosmosResult,
                                     searchword=graphene.String(required=True))
    def resolve_results_standard(self, info, searchword):
        start = time.time() #timer
        base = skosmos.SkosmosDatabase([])
        entries = base.get_entries()
        data = []
        for entry in entries:
            jsondata = entry.search(searchword)
            results = jsondata[u'results']
            data = data + results
        outwithyou = rest_resolver({u'results':data}) #timer, otherwise return rest_resolver({u'results':data})
        end = time.time() #timer
        print(end - start)#timer
        return outwithyou

    results_parallel = graphene.List(SkosmosResult,
                                     searchword=graphene.String(required=True))
    def resolve_results_parallel(self, info, searchword):
        start = time.time() #timer
        pool = ThreadPool()
        base = skosmos.SkosmosDatabase([])
        entries = base.get_entries()
        parallel = Helper(searchword)
        test = pool.map(parallel.search, entries)
        pool.close()
        pool.join()
        outwithyou = rest_resolver({u'results':parallel.get_store()}) #timer, otherwise return rest_resolver({u'results':helper.get_store()})
        end = time.time() #timer
        print(end - start)#timer
        return outwithyou

    #multi argument resover allowing for complex queries which are constructed by concatenating arguments according to
    #http://api.finto.fi/doc/#!/Global_methods/get_search
    results_multi = graphene.List(SkosmosResult,
                                  searchword=graphene.String(required=True),
                                  language=graphene.String(required=True))
    def resolve_results_multi(self, info, searchword, language):
        start = time.time() #timer

        #query for searchword in language is constructed via concatenation; can be extended for vocab etc.
        language = '&lang=' + language 
        searchword = searchword + language 

        pool = ThreadPool()
        base = skosmos.SkosmosDatabase([])
        entries = base.get_entries()
        parallel = Helper(searchword)
        test = pool.map(parallel.search, entries)
        pool.close()
        pool.join()
        outwithyou = rest_resolver({u'results':parallel.get_store()}) #timer, otherwise return rest_resolver({u'results':helper.get_store()})
        end = time.time() #timer
        print(end - start)#timer
        return outwithyou

##EXRESOLVER:

#given pool.map(function, iterable), enables function to pass searchword variable to iterable;
#stores resulting data as list
class Helper:
    def __init__(self, searchword = str, store = []):
        self.searchword = searchword
        self.store = store #stores the result of self.search as list

    def search(self, entry): #entry is a SkosmosInstance()
        jsondata = entry.search(self.searchword)
        results = jsondata[u'results']
        data = self.store
        self.store = data + results

    def get_store(self):
        return self.store    

#takes result of SPARQL query and, for each binding, sets missing keys to None;
#returns list of bindings mapped to SparqlResult()s
def normalize_sparql(data):
    normalized = []
    variables = data[u'head'][u'vars']
    bindings = data[u'results'][u'bindings']
    for entry in bindings:
        for variable in variables:
            try:
                entry[variable]
            except KeyError:
                entry[variable] = None
        normalized.append(SparqlResult(subject=entry[u'Subject'], #should be dynamically mapped to variables set...
                                       term=entry[u'Term'],
                                       parents=entry[u'Parents'],
                                       descr=entry[u'Descr'],
                                       scopenote=entry[u'ScopeNote'],
                                       kind=entry[u'Type'],
                                       extrakind=entry[u'ExtraType']))
    return normalized    

#returns list of SkosmosResult-objects based on data;
#missing labels are added and set to None
def rest_resolver(data): 
    resolved = []
    skos = get_skos()
    for entry in data[u'results']:
        dummy = entry
        for label in skos:
            if label in dummy:
                pass
            else:
                dummy[label] = None        
        resolved.append(SkosmosResult(uri=dummy[u'uri'],
                                kind=dummy[u'type'],
                                preflabel=dummy[u'prefLabel'],
                                altlabel=dummy[u'altLabel'],
                                hiddenlabel=dummy[u'hiddenLabel'],
                                lang=dummy[u'lang'],
                                notation=dummy[u'notation'],
                                vocab=dummy[u'vocab'],
                                exvocab=dummy[u'exvocab']))
        dummy.clear()
    return resolved 

##MIX AND MATCH:

#returns implemented SKOS labels
def get_skos():
    return [u'uri',u'type' u'prefLabel', u'altLabel', u'hiddenLabel', u'lang', u'notation', u'vocab', u'exvocab']

##MAIN:

schema = graphene.Schema(query=Query)


