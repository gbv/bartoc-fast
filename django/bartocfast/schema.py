""" schema.py """

import time # dev
import asyncio 
from typing import List, Set, Dict, Union

import graphene
from aiohttp import ClientSession, ClientTimeout

from .models import Federation, SkosmosInstance, SparqlEndpoint, LobidResource
from .utility import Result, MappingDatabase, DEF_MAXSEARCHTIME, DEF_DISABLED # local

class GlobalResult(graphene.ObjectType):
    """ Result of a global query """
    
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
    source = graphene.String(description='name of queried resource') # nb: purge deletes sources for doubles!

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
        attributes = B.difference(A)
        attributes.remove('_meta')
        for method in ["fields", "select_field"]:
            attributes.remove(method)
        return attributes

    @classmethod
    def select_field(self, uri: str) -> str:
        """ Select (the name of a) field by uri """

        mappings = MappingDatabase()
        mapping = mappings.select_by_uri(uri)
        return mapping.field

class Query(graphene.ObjectType):
    """ Query """

    results_global = graphene.List(GlobalResult,
                                   searchword=graphene.String(required=True),
                                   category=graphene.Argument(graphene.Int, default_value=0),
                                   maxsearchtime=graphene.Argument(graphene.Int, default_value=DEF_MAXSEARCHTIME),
                                   duplicates=graphene.Argument(graphene.Boolean, default_value=False),
                                   disabled=graphene.Argument(graphene.List(graphene.String), default_value=DEF_DISABLED)
                                   )

    def resolve_results_global(self, info, searchword, category, maxsearchtime, duplicates, disabled):
        """ Resolve Global query type """

        start = time.time()                                 # dev

        # initialize:
        # should already be done... if not, update federation manually

        # 

        # access resources in federation:
        resources = list(SparqlEndpoint.objects.all()) + list(SkosmosInstance.objects.all()) + list(LobidResource.objects.all()) ### 

        # remove disabled resources
        resources = Helper.remove_disabled(resources, disabled)
                            
        end_init = time.time()                              # dev
        print(f'***INITIALIZE took {end_init - start}')     # dev

        # fetch data from resources as results:
        results = asyncio.run(Helper.fetch(resources, searchword, category, maxsearchtime), debug=True)
        end_fetch = time.time()                             # dev
        print(f'***FETCH took {end_fetch - end_init}')      # dev

        # normalize results:
        
        globalresults = Normalize.main(results, duplicates)
        end = time.time()                                   # dev
        print(f'***NORMALIZE took {end - end_fetch}')       # dev
        print(f'***TOTAL took {end - start}')               # dev
        print(f'<--STOP')                                   # dev
        return globalresults

class Helper:
    """ Helper tools """

    @classmethod
    def remove_disabled(self,
                        resources: List[Union[SkosmosInstance, SparqlEndpoint]],
                        disabled: List[Union[SkosmosInstance, SparqlEndpoint]]) -> List[Union[SkosmosInstance, SparqlEndpoint]]:
        """ Remove disabled resources """
        
        while len(disabled) > 0:
            for resource in resources:
                if resource.name in disabled:
                    resources.remove(resource)
                    disabled.remove(resource.name)
        return resources

    @classmethod
    async def fetch(self,
                    resources: List[Union[SkosmosInstance, SparqlEndpoint]],
                    searchword: str,
                    category: int = 0,
                    maxsearchtime: int = DEF_MAXSEARCHTIME) -> List[Result]:
        """ Coroutine: fetch data from resources as results """

        timeout = ClientTimeout(total=maxsearchtime)
        async with ClientSession(timeout=timeout) as session:

            results = await asyncio.gather(*[resource.main(session, searchword, category) for resource in resources])
            await session.close()

            return results
  
class Normalize:
    """ Normalize results """

    @classmethod
    def main(self, results: List[Result], duplicates: bool = False) -> List[GlobalResult]: 
        """ Normalize results """

        globalresults = []
        for result in results:
            start = time.time() # dev
            globalresult = self.normalize(result)
            globalresults.extend(globalresult)
            end = time.time() # dev
            print(f'NORMALIZE {result.name} took {end - start}') # dev

        howmany = len(globalresults) # dev
        if duplicates == False:
            globalresults = self.purge(globalresults)
        print(f'TOTAL has {howmany - len(self.purge(globalresults))} duplicates and {len(self.purge(globalresults))} unique results') # dev
            
        return globalresults
        
    @classmethod
    def normalize(self, result: Result) -> List[GlobalResult]: # not very nice yet
        """ Normalize result (select and execute method) """

        skosmosnames = []
        for instance in SkosmosInstance.objects.all():
            skosmosnames.append(instance.name)

        sparqlnames = []
        for endpoint in SparqlEndpoint.objects.all():
            sparqlnames.append(endpoint.name)

        lobidnames = []
        for resource in LobidResource.objects.all():
            lobidnames.append(resource.name)

        if result.data == None: # here we catch timed out resources
            return []
        elif result.name in skosmosnames:
            return self.normalize_skosmos(result)
        elif result.name in sparqlnames:
            return self.normalize_sparql(result)
        elif result.name in lobidnames:
            return self.normalize_lobid(result)
        else:
            raise NameError

    @classmethod
    def normalize_sparql(self, result: Result) -> List[GlobalResult]:
        """ Normalize SPARQL data """

        try:
            result.data['results']['bindings']
        except KeyError:
            print(f'ERROR: Something is wrong with Normalize.normalize_sparql {result.name}!')
            return []
        else:
            bindings = result.data['results']['bindings']
            normalized = []
            for binding in bindings:  
                globalresult = GlobalResult()
                subject = binding["subject"]["value"]       # eg: "subject": { "type": "uri", "value": "http://www.eionet.europa.eu/gemet/group/8603" }
                predicate = binding["predicate"]["value"]   # eg: "predicate": { "type": "uri", "value": "http://www.w3.org/2000/01/rdf-schema#label" }	
                obj = binding["object"]["value"]            # eg: "object": { "type": "literal", "xml:lang": "en", "value": "TRAFFIC, TRANSPORTATION" }

                globalresult.uri = subject
                field = GlobalResult.select_field(predicate)

                # check if globalresult (defined by uri) is already collected:
                if globalresult in normalized:
                    normal = normalized[normalized.index(globalresult)]

                    # check if field is still empty:
                    try:
                        assert(getattr(normal, field) == None)
                    except AssertionError:
                        pass
                    else:
                        setattr(normal, field, obj)
                else:
                    setattr(globalresult, field, obj)
                    globalresult.source = result.name
                    normalized.append(globalresult)
                    
            howmany = len(normalized) # dev
            normalized = self.purge(normalized)
            print(f'{result.name} has {howmany - len(normalized)} duplicates and {len(normalized)} unique results') # dev
            return normalized # self.purge(normalized) w/o dev

    @classmethod
    def normalize_skosmos(self, result: Result) -> List[GlobalResult]:
        """ Normalize Skosmos data """

        try:
            result.data['results'] # here data format (perhaps also @context) could be verified; select already excludes None data
        except KeyError:
            print(f'ERROR: Something is wrong with Normalize.normalize_skosmos {result.name}!')
            return []
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
                globalresult.source = result.name               # we set the source of globalresult to the name of the result (i.e., name of the resource where the result was queried)
                normalized.append(globalresult)

            howmany = len(normalized) # dev
            merged = self.merge(normalized)
            print(f'{result.name} has {howmany - len(merged)} duplicates and {len(merged)} unique results') # dev
            return merged

    @classmethod
    def normalize_lobid(self, result: Result) -> List[GlobalResult]:
        """ Normalize lobid-gnd data """

        try:
            result.data['member']
        except KeyError:
            print(f'ERROR: Something is wrong with Normalize.normalize_lobid {result.name}!')
            return []
        else:
            members = result.data['member']
            normalized = []
            for member in members:  
                globalresult = GlobalResult()

                try:
                    member["id"]
                except KeyError:
                    continue # skip to next member
                else:
                    globalresult.uri = member["id"]

                try:
                    member["preferredName"]
                except KeyError:
                    globalresult.prefLabel = None
                else:
                    globalresult.prefLabel = member["preferredName"]

                try:
                    member["variantName"]
                except KeyError:
                    globalresult.altLabel = None
                else:
                    variants = []
                    for variant in member["variantName"]:
                        variants.append(variant)
                    globalresult.altLabel = "; ".join(variants)

                try:
                    member["definition"]
                except KeyError:
                    globalresult.definition = None
                else:
                    definitions = []
                    for definition in member["definition"]:
                        definitions.append(definition)
                    globalresult.definition = "; ".join(definitions)

                globalresult.source = result.name
                normalized.append(globalresult)
                    
            howmany = len(normalized) # dev
            merged = self.merge(normalized)
            print(f'{result.name} has {howmany - len(merged)} duplicates and {len(merged)} unique results') # dev
            return merged
        
    @classmethod
    def purge(self, globalresults: List[GlobalResult]) -> List[GlobalResult]:
        """ Delete duplicates """

        globalresults = set(globalresults)
        return list(globalresults)

    @classmethod
    def partition(self, globalresults: List[GlobalResult]) -> Dict[str, List[GlobalResult]]:
        """ Make partition: {x in List[GlobalResult] | x ~ uri} """

        partition = dict()

        for globalresult in globalresults:
            if globalresult.uri in partition:
                value = partition[globalresult.uri]
                value.append(globalresult)
                partition[globalresult.uri] = value
            else:
                partition.update({globalresult.uri : [globalresult]})
                
        return partition

    @classmethod
    def merge(self, globalresults: List[GlobalResult]) -> List[GlobalResult]:
        """ Merge duplicates: for a given block of a partition, merge each field for each element in the block """

        partition = self.partition(globalresults)

        globalresults = []

        for key in partition:
            if len(partition[key]) == 1:
                globalresults.append(partition[key][0])
            else:
                globalresult = GlobalResult()
                fields = GlobalResult.fields()
                for field in fields:
                    merged = []
                    for element in partition[key]:
                        value = getattr(element, field)
                        if value is not None:
                            merged.append(value)
                    merged = set(merged)
                    if len(merged) > 0:
                        merged = "; ".join(merged)
                    else:
                        merged = None
                    setattr(globalresult, field, merged)
                globalresults.append(globalresult)

        return globalresults
    
