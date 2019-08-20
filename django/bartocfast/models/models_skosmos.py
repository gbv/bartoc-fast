""" models_skosmos.py """

import time # dev
import asyncio

from django.db import models # https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.Field
from aiohttp import ClientSession, ClientTimeout
from urllib import parse

from .models_main import Resource, Query
from ..utility import Result

class SkosmosQuery(Query):
    """ A SPARQL query """

    class Meta:
        verbose_name_plural = 'Skosmos queries'
    
    skosmosinstance = models.ForeignKey("SkosmosInstance", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.skosmosinstance.name} category {self.category}'

class SkosmosInstance(Resource):
    """ A Skosmos instance """

    def select(self, category: int) -> SkosmosQuery:
        """ Select Skosmos query by category """ 
        
        return SkosmosQuery.objects.get(skosmosinstance=self, category=category)

    def prepare(self, searchword: str) -> str:
        """ Prepare searchword for search """
        
        # remove wildcard as in color* and col*r, applies to Legilux:
        if "wildcard" in self.context:
            return parse.quote(searchword.replace("*", ""))
            
        return parse.quote(searchword)

    def construct_request(self, searchword: str, query: str) -> str:
        """ Construct REST API request """

        searchword = self.prepare(searchword)

        return self.url + query.querystring + searchword
        

    async def search(self,
                     session: ClientSession,
                     searchword: str,
                     category: int = 0) -> Result:
        """ Coroutine: send query to Skosmos instance """

        start = time.time() # dev

        if self.disabled == True:
            return Result(self.name, None, category)
        
        query = self.select(category)
        request = self.construct_request(searchword, query)
        
        async with session.get(request) as response:
            
            data = await response.json()

            end = time.time() # dev
            print(f'FETCH {self.name} took {end - start}') # dev

            return Result(self.name, data, category)
