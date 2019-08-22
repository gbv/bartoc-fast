""" models_lobid.py based on http://lobid.org/gnd/api """

import time # dev
import asyncio

from django.db import models # https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.Field
from aiohttp import ClientSession, ClientTimeout
from urllib import parse

from .models_base import Resource, Query
from ..utility import Result

class LobidQuery(Query):
    """ A lobid-gnd query """

    class Meta:
        verbose_name_plural = 'lobid-gnd queries'
    
    lobidresource = models.ForeignKey("LobidResource", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.lobidresource.name} category {self.category}'

class LobidResource(Resource):
    """ A lobid-gnd resource """

    def select(self, category: int) -> LobidQuery:
        """ Select lobid-gnd query by category """ 
        
        return LobidQuery.objects.get(lobidresource=self, category=category)

    def prepare(self, searchword: str) -> str: ### check if needed
        """ Prepare searchword for search """
        
        # remove wildcard as in color* and col*r:
        if "wildcard" in self.context:
            return parse.quote(searchword.replace("*", ""))
            
        return parse.quote(searchword)

    def construct_request(self, searchword: str, query: str) -> str:
        """ Construct lobid-gnd request """

        searchword = self.prepare(searchword)

        return self.url + query.querystring.replace("!!!SEARCHWORD!!!", searchword)
        

    async def search(self,
                     session: ClientSession,
                     searchword: str,
                     category: int = 0) -> Result:
        """ Coroutine: send query to Lobid resource """

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
