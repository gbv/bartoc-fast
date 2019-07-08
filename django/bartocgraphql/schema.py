""" schema.py """

import time # for dev
import asyncio 
from typing import List, Set, Dict, Tuple, Optional, Union

import graphene
from aiohttp import ClientSession

from .models import SkosmosInstance, SparqlEndpoint

from .utility import Result, MappingDatabase            # local

class GlobalResult(graphene.ObjectType):
    """ Result of a Global (with capital G) query """
    
    uri = graphene.String(description='URI')
    prefLabel = graphene.String(description='http://www.w3.org/2004/02/skos/core#prefLabel')
    altLabel = graphene.String(description='http://www.w3.org/2004/02/skos/core#altLabel')
    hiddenLabel = graphene.String(description='http://www.w3.org/2004/02/skos/core#hiddenLabel')
    # broader
    # narrower
    # related
    # broadMatch
    # closeMatch
    # narrowMatch
    # relatedMatch
    # exactMatch
    # note
    definition = graphene.String(description='http://www.w3.org/2004/02/skos/core#definition')
    # inScheme
    # topConceptOf

    def __eq__(self, other):
        """ Identity condition """ # https://stackoverflow.com/questions/4169252/remove-duplicates-in-list-of-object-with-python

        return self.uri == other.uri

    def __hash__(self):
        """ Hash function """
        
        return hash(('uri', self.uri))

    @classmethod
    def fields(self) -> Set[str]:
        """ Return all fields """
        
        A = set(dir(graphene.ObjectType))
        B = set(dir(GlobalResult))
        C = B.difference(A)
        C.remove('_meta')
        return C

    @classmethod
    def flat(self, field: str) -> str:
        """ Return flat field (if any) """
        
        try:
            assert(field in self.fields())
        except AssertionError:
            return None
        else:
            mappings = MappingDatabase() # replace with model
            mapping = mappings.select_by_field(field)
            return mapping.uri

    @classmethod
    def select(self, uri: str) -> str:
        """ Select (the name of a) field by uri """

        mappings = MappingDatabase()
        mapping = mappings.select_by_uri(uri)
        return mapping.field

class Query(graphene.ObjectType):
    """ Query """

    results_global = graphene.List(GlobalResult,
                                   searchword=graphene.String(required=True),
                                   category=graphene.Int(required=True)) # check this line

    def resolve_results_global(self, info, searchword, category):
        """ Resolve Global query type """

        start = time.time()                                 # dev
        print(f'ASYNC **START')                             # dev

        # initialize:
        # should already be done... if not, update federation manually

        # access resources in federation:
        resources = list(SparqlEndpoint.objects.all()) + list(SkosmosInstance.objects.all())
        
        end_init = time.time()                              # dev
        print(f'ASYNC *INITIALIZE took {end_init - start}') # dev

        # fetch data from resources as results:
        results = asyncio.run(fetch(resources, searchword, category))
        end_fetch = time.time()                             # dev
        print(f'ASYNC *FETCH took {end_fetch - end_init}')  # dev

        # normalize results:
        globalresults = Normalize.normalize(results)
        end = time.time()                                   # dev
        print(f'ASYNC *NORMALIZE took {end - end_fetch}')   # dev
        print(f'ASYNC **TOTAL took {end - start}')          # dev
        return globalresults

async def fetch(resources: List[Union[SkosmosInstance, SparqlEndpoint]], searchword: str, category: int = 0) -> List[Result]:
    """ Coroutine: fetch data from resources as results """

    async with ClientSession() as session:

        # start = time.time()                         # dev

        results = await asyncio.gather(*[resource.search(session, searchword, category) for resource in resources])
        await session.close()
        
        # end = time.time()                           # dev
        # print(f'ASYNC FETCH took {end - start}')    # dev

        return results    

class Normalize:
    """ Normalize results """

    @classmethod
    def normalize(self, results: List[Result]) -> List[GlobalResult]: 
        """ Normalize results """

        globalresults = []
        for result in results:
            globalresult = self.select(result)
            globalresults.extend(globalresult)
            
        return self.purge(globalresults)

    @classmethod
    def select(self, result: Result) -> List[GlobalResult]: # not very nice yet
        """ Select and execute method for result """

        skosmosnames = ["AgroVoc", "Bartoc", "data.ub.uio.no", "Finto", "Legilux", "MIMO", "UNESCO", "OZCAR-Theia", "Loterre"]

        if result.data == None:
            return []
        elif result.name in skosmosnames:
            return self.skosmos(result)
        elif result.name == "Getty":
            return self.getty(result)
        elif result.name == "LuSTRE":
            return self.lustre(result)
        else:
            raise NameError

    @classmethod
    def purge(self, globalresults: List[GlobalResult]) -> List[GlobalResult]:
        """ Delete duplicates """

        globalresults = set(globalresults)
        return list(globalresults)

    @classmethod
    def getty(self, result):
        """ Normalize Getty data """

        return []

    @classmethod
    def lustre(self, result: Result) -> List[GlobalResult]:
        """ Normalize LuSTRE data """

        try:
            result.data['results']['bindings'] # here data format (perhaps also @context) could be verified; select already excludes None data
        except KeyError:
            pass
        else:
            bindings = result.data['results']['bindings']
            normalized = []
            for binding in bindings:  
                globalresult = GlobalResult()
                resulturi = binding["subject"]["value"]     # eg: "subject": { "type": "uri", "value": "http://www.eionet.europa.eu/gemet/group/8603" }
                globalresult.uri = resulturi
                fielduri = binding["predicate"]["value"]    # eg: "predicate": { "type": "uri", "value": "http://www.w3.org/2000/01/rdf-schema#label" }	
                fieldvalue = binding["object"]["value"]     # eg: "object": { "type": "literal", "xml:lang": "en", "value": "TRAFFIC, TRANSPORTATION" }
                field = GlobalResult.select(fielduri)
                setattr(globalresult, field, fieldvalue)
                normalized.append(globalresult)
        return self.purge(normalized)

    @classmethod
    def skosmos(self, result: Result) -> List[GlobalResult]:
        """ Normalize Skosmos data """

        try:
            result.data['results'] # here data format (perhaps also @context) could be verified; select already excludes None data
        except KeyError:
            pass
        else:
            normalized = []
            for entry in result.data['results']:
                globalresult = GlobalResult()
                for field in GlobalResult.fields():
                    try:
                        entry[field]
                    except KeyError:
                        entry[field] = None                     # missing fields are added (required for resolver) and set to None
                    setattr(globalresult, field, entry[field])  # we set each field of globalresult to the corresponding value in the entry
                normalized.append(globalresult)
        self.purge(normalized)
        return self.purge(normalized)
    
