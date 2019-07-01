""" A test for schema.py: py -3.7 ./manage.py test bql.tests.test_schema """

from django.test import SimpleTestCase

import time
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from typing import List, Set, Dict, Tuple, Optional

import json
import graphene

from ..skosmos import SkosmosInstance, SkosmosDatabase          # local
from ..sparql import SparqlEndpoint, SparqlDatabase             # local
from ..schema import GlobalResult, Query, Helper, Normalize     # local
from ..utility import Result                                        # local

class TestQueryFetch(SimpleTestCase):

    def setUp(self) -> None:
        self.query = Query()

    def test_fetch(self):
        info = None
        searchword = "cow"
        category = 0
        results = self.query.resolve_results_global(info, searchword, category)
        print(results)
        print(len(results))
        for result in results:
            print(result.name)
            try:
                print(len(result.data))
            except TypeError:
                print(None)

    def test_select(self):
        info = None
        searchword = "dog"
        category = 0
        results = self.query.resolve_results_global(info, searchword, category)

        print(f'results: {len(results)}')
        global_results = []
        for result in results:
            global_results.append(Normalize.select(result))

        print(f'global results: {len(global_results)}')

class TestQuery(SimpleTestCase):

    def setUp(self) -> None:
        self.query = Query()

    def test_fetchandnormalize(self):
        info = None
        searchword = "dog"
        category = 0
        globalresults = self.query.resolve_results_global(info, searchword, category)
        # print(globalresults)
        print(len(globalresults))
        for globalresult in globalresults:
            print(globalresult.uri)
        
class TestGlobalResult(SimpleTestCase):

    def test_fields(self):
        print(GlobalResult.fields())

    def test_flat(self):
        print(GlobalResult.flat("prefLabel"))
        print(GlobalResult.flat("MUH"))   

class TestNormalizeSkosmos(SimpleTestCase):

    def setUp(self) -> None:
        self.searchword = "dog"
        with open(f'//itsc-pg2.storage.p.unibas.ch/ub-home$/hinder0000/Documents/GitHub/bartoc-graphql/django/bql/tests/files/schema_normalize_skosmos_{self.searchword}.json', encoding="utf-8") as file:
            data = json.load(file)
            file.close()
        self.data = data

    def test_skosmos(self):

        globalresults = Normalize.skosmos(Result("Finto", self.data))
        print (len(globalresults))
        for globalresult in globalresults:
            print(globalresult)
            print(f'uri: {globalresult.uri}')
            print(f'prefLabel: {globalresult.prefLabel}')
            print(f'altLabel: {globalresult.altLabel}')
            print(f'hiddenLabel: {globalresult.hiddenLabel}')
            print(f'definition: {globalresult.definition}')

    def test_hash(self):
            
        globalresults = Normalize.skosmos(Result("Finto", self.data))
        globalresults = set(globalresults)
        print (len(globalresults))
        for globalresult in globalresults:
            print(globalresult)
            print(f'uri: {globalresult.uri}')
            print(f'prefLabel: {globalresult.prefLabel}')
            print(f'altLabel: {globalresult.altLabel}')
            print(f'hiddenLabel: {globalresult.hiddenLabel}')
            print(f'definition: {globalresult.definition}')
        
class TestNormalizeLustre(SimpleTestCase):

    def setUp(self) -> None:
        self.searchword = "transport"
        with open(f'//itsc-pg2.storage.p.unibas.ch/ub-home$/hinder0000/Documents/GitHub/bartoc-graphql/django/bql/tests/files/lustre_0_{self.searchword}.json', encoding="utf-8") as file:
            data = json.load(file)
            file.close()
        self.data = data

    def test_lustre(self):

        globalresults = Normalize.lustre(Result("LuSTRE", self.data))
        print (len(globalresults))
        #for globalresult in globalresults:
        #    print(globalresult)
        #    print(f'uri: {globalresult.uri}')
        #    print(f'prefLabel: {globalresult.prefLabel}')
        #    print(f'altLabel: {globalresult.altLabel}')
        #    print(f'hiddenLabel: {globalresult.hiddenLabel}')
        #    print(f'definition: {globalresult.definition}')

        globalresults = set(globalresults)
        print (len(globalresults))


                                       
                        
                                   
                
