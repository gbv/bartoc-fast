""" models.py """

import time # dev
import asyncio
import re

from django.db import models # https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.Field
from aiohttp import ClientSession, ClientTimeout
from SPARQLWrapper import (SPARQLWrapper, JSON)

from .models_base import Resource, Query
from ..utility import Result

class SparqlQuery(Query):
    """ A SPARQL query """

    class Meta:
        verbose_name_plural = 'Sparql queries'
    
    sparqlendpoint = models.ForeignKey("SparqlEndpoint", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.sparqlendpoint.name} category {self.category}'

    def update(self, searchword: str) -> str:
        """ Put the searchword into the query """
        
        return self.querystring.replace("!!!SEARCHWORD!!!", searchword)

class SparqlEndpoint(Resource):
    """ A SPARQL endpoint """

    def select(self, category: int) -> SparqlQuery:
        """ Select SPARQL query by category """ 
        
        return SparqlQuery.objects.get(sparqlendpoint=self, category=category)

    def prepare(self, searchword: str) -> str: 
        """ Prepare searchword for search """

        # remove excess whitespace:
        " ".join(searchword.split())            

        # virtuoso endpoints (LuSTRE) require special prep:
        if "virtuoso" in self.context:
            # connect open compounds (such as "gas station"):
            searchword = searchword.replace(" ", " AND ")
            # remove special characters (umlaute, etc)
            searchword = re.sub('[^A-Za-z0-9\s]+', '', searchword)
            " ".join(searchword.split())
            
        return searchword

    def construct_request(self, searchword: str, query: str) -> str:
        """ Construct request with SPARQLWrapper """

        searchword = self.prepare(searchword)
        querystring = query.update(searchword)

        wrapper = SPARQLWrapper(self.url)
        wrapper.setQuery(querystring)
        wrapper.setReturnFormat(JSON)
        request = wrapper._createRequest()

        return request.get_full_url()

    async def search(self,
                     session: ClientSession,
                     searchword: str,
                     category: int = 0) -> Result:
        """ Coroutine: send query to SPARQL endpoint """

        start = time.time() # dev

        if self.disabled == True:
            return Result(self.name, None, category)
        
        query = self.select(category)
        request = self.construct_request(searchword, query)

        async with session.get(request) as response:

            try:
                data = await response.json()
            except Exception:
                print(f'ERROR: Something went wrong with {self.name}!') # dev
                return Result(self.name, None, category)

            end = time.time() # dev
            print(f'FETCH {self.name} took {end - start}') # dev

            return Result(self.name, data, category)
