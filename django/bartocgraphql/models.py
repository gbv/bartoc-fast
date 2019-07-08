import time                                     # dev
import asyncio

from django.db import models # https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.Field
from aiohttp import ClientSession
from openpyxl import load_workbook
from SPARQLWrapper import (SPARQLWrapper, JSON)
from urllib import parse

from .utility import Database, Entry, Result    # local

LOCALPATH = "//itsc-pg2.storage.p.unibas.ch/ub-home$/hinder0000/Documents/GitHub/bartocgraphql/django/bartocgraphql/"

# queries:
class Query(models.Model):
    """ Abstract query class """
    
    querystring = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    category = models.IntegerField()
    timeout = models.IntegerField()

    class Meta:
        abstract = True

class SparqlQuery(Query):
    """ A SPARQL query """
    
    sparqlendpoint = models.ForeignKey("SparqlEndpoint", on_delete=models.CASCADE)

    def update(self, searchword: str) -> str:
        """ Put the searchword into the query """
        
        return self.querystring.replace("!!!SEARCHWORD!!!", searchword)

class SkosmosQuery(Query):
    """ A SPARQL query """
    
    skosmosinstance = models.ForeignKey("SkosmosInstance", on_delete=models.CASCADE)

# resources:
class Resource(models.Model):
    """ Abstract resource class """

    federation = models.ForeignKey("Federation", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.URLField()
    timeout = models.IntegerField()

    class Meta:
        abstract = True

class SkosmosInstance(Resource):
    """ A Skosmos instance """

    def select(self, category: int) -> SkosmosQuery:
        """ Select Skosmos query by category """ 
        
        return SkosmosQuery.objects.get(skosmosinstance=self, category=category)

    def clean(self, searchword: str) -> str:
        """ Prepare searchword for search """

        return parse.quote(searchword)   

    async def search(self, session: ClientSession, searchword: str, category: int = 0) -> Result:
        """ Coroutine: send query to Skosmos instance """

        start = time.time()                                 # dev
        query = self.select(category)

        searchword = self.clean(searchword)
        
        if query.timeout == 1:
            return Result(self.name, None, category)
        
        restapi = self.url + query.querystring + searchword
        async with session.get(restapi) as response:
            
            data = await response.json()

            end = time.time()                               # dev
            print(f'ASYNC {self.name} took {end - start}')  # dev

            return Result(self.name, data, category)

class SparqlEndpoint(Resource):
    """ A SPARQL endpoint """

    def select(self, category: int) -> SparqlQuery:
        """ Select SPARQL query by category """ 
        
        return SparqlQuery.objects.get(sparqlendpoint=self, category=category)     

    async def search(self, session: ClientSession, searchword: str, category: int = 0) -> Result:
        """ Coroutine: send query to SPARQL endpoint """

        start = time.time()                                 # dev
        query = self.select(category)

        if query.timeout == 1:
            return Result(self.name, None, category)

        querystring = query.update(searchword)

        # we just want the flat query, not the request...
        sparqlwrapper = SPARQLWrapper(self.url)
        sparqlwrapper.setQuery(querystring)
        sparqlwrapper.setReturnFormat(JSON)
        flatquery = sparqlwrapper.query().geturl()

        # ...because the request is done here
        async with session.get(flatquery) as response:
            data = await response.json()
            end = time.time()                               # dev
            print(f'ASYNC {self.name} took {end - start}')  # dev
            return Result(self.name, data, category)
    
# federation: 
class Federation(models.Model):
    """ The federation of resources (there is only one) """
    created = models.DateTimeField(auto_now=True)

    def populate_skosmosinstances(self) -> None: 
        """ Populate federation with Skosmos instances and their queries """

        SkosmosInstance.objects.all().delete()

        skosmosinstances = load_workbook(LOCALPATH + "fixtures/skosmosinstances.xlsx") # required for unittest; simply fixtures/skosmosinstances.xlsx in production

        for ws in skosmosinstances:
            for row in ws.iter_rows(min_row=2, min_col=1, max_col=3, values_only=True):   
                instance = SkosmosInstance(federation=self,
                                                  name=row[0],
                                                  url=row[1],
                                                  timeout=row[2])
                instance.save()

                query = SkosmosQuery(skosmosinstance=instance, # constructs query of cat 0
                                     querystring="/rest/v1/search?query=",
                                     description="NA",
                                     category=0,
                                     timeout=row[2])
                query.save()

    def populate_sparqlendpoints(self) -> None:
        """ Populate federation with SPARQL endpoints and their queries """

        SparqlEndpoint.objects.all().delete()

        sparqlendpoints = load_workbook(LOCALPATH + "fixtures/sparqlendpoints.xlsx") # required for unittest; fixtures/sparqlendpoints.xlsx in production

        for ws in sparqlendpoints:
            endpoint = SparqlEndpoint(federation=self,
                                      name=ws['A3'].value,
                                      url=ws['B3'].value,
                                      timeout=0)
            endpoint.save()
            
            for row in ws.iter_rows(min_row=3, min_col=3, max_col=6, values_only=True):
                query = SparqlQuery(sparqlendpoint=endpoint,
                                    querystring=row[0],
                                    description=row[1],
                                    category=row[2],
                                    timeout=row[3])
                query.save()

    def populate(self) -> None:
        """ Populate federation with all resources """

        self.populate_skosmosinstances()
        self.populate_sparqlendpoints()

        
