""" schema.py """

import time
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from typing import List, Set, Dict, Tuple, Optional, Union

import graphene


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

    @classmethod
    def fields(self) -> set[str]:
        A = dir(graphene.ObjectType)
        B = dir(GlobalResult)
        C = B.difference(A)
        C.remove('_meta')
        return C
        
class Normalize():
    """ Bla """

    #@classmethod
    #def select(self, result: Result) -> 

    @classmethod
    def skosmos(self, result: Result) -> List[GlobalResult]:
        #assumes that result comes from SkosmosInstance, so checking happens before

        try:
            result.data['results']
        except KeyError:
                pass
        else:
            normalized = []
            for entry in result.data['results']:
                global_result = GlobalResult()
                for field in GlobalResult.fields:
                     try:
                        entry[field]
                    except KeyError:
                        entry[field] = None # missing fields are added (required for resolver) and set to None
                setattr(global_result, field, entry[field]) # we set each field of globalresult to the corresponding value in the entry
                normalized.append(global_result)
        return normalized




