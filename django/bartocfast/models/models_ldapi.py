""" models_ldapi.py (https://documentation.ands.org.au/display/DOC/Linked+Data+API#LinkedDataAPI-Endpointtemplates) """

import time # dev
import asyncio

from django.db import models
from aiohttp import ClientSession, ClientTimeout
from urllib import parse

from .models_base import Resource, Query
from ..utility import Result

class LdapiQuery(Query):
    """ A Linked-Data-API query """

    class Meta:
        verbose_name_plural = 'Ldapi queries'
    
    ldapiendpoint = models.ForeignKey("LdapiEndpoint", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.ldapiendpoint.name} category {self.category}'

class LdapiEndpoint(Resource):
    """ A Linked-Data-API endpoint """

    def select(self, category: int) -> LdapiQuery:
        """ Select Linked-Data-API query by category """ 
        
        return LdapiQuery.objects.get(ldapiendpoint=self, category=category)

    def prepare(self, searchword: str) -> str:
        """ Prepare searchword for search """
        
        return parse.quote(searchword)

    def construct_request(self, searchword: str, query: str) -> str:
        """ Construct Linked-Data-API request """

        searchword = self.prepare(searchword)

        return self.url + query.querystring + searchword
        

    async def search(self,
                     session: ClientSession,
                     searchword: str,
                     category: int = 0) -> Result:
        """ Coroutine: send query to Linked-Data-API endpoint """

        start = time.time() # dev
        
        query = self.select(category)
        request = self.construct_request(searchword, query)
        
        async with session.get(request) as response:
            
            try:
                data = await response.json()
            except Exception:
                print(f'ERROR: Something went wrong with {self.name}.search method!') # dev
                return Result(self.name, None, category)

            end = time.time() # dev
            print(f'FETCH {self.name} took {end - start}') # dev

            return Result(self.name, data, category)
    
