""" models_base.py """

import asyncio

from django.db import models # https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.Field
from aiohttp import ClientSession, ClientTimeout, ClientOSError

from ..utility import Database, Entry, Result, LOCAL_APP_PATH

class Query(models.Model): # confusing, same name as schema.Query
    """ Abstract query class """
    
    querystring = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    category = models.IntegerField()
    timeout = models.IntegerField()

    class Meta:
        abstract = True

class Resource(models.Model):
    """ Abstract resource class """

    federation = models.ForeignKey("Federation", on_delete=models.CASCADE) ### Federation.resource.all() should work... or not since related_name='resource',  does not work
    name = models.CharField(max_length=100)
    url = models.URLField()
    disabled = models.BooleanField(default=False)
    context = models.CharField(max_length=200) #special, wildcard

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f'{self.name}'

    async def main(self,
                   session: ClientSession,
                   searchword: str,
                   category: int = 0) -> Result:
        """ Coroutine: send query to resource """

        try:
            result = await self.search(session, searchword, category)
            return result
        
        except asyncio.TimeoutError:
            print(f'FETCH {self.name} ran out of time!') # dev
            return Result(self.name, None, category)
        except ClientOSError:
            print(f'FETCH {self.name} did not respond!') # dev
            return Result(self.name, None, category)

class Federation(models.Model):
    """ The federation of resources (there is only one) """
    
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'federation'

    def __str__(self) -> str:
        return 'Main federation'

    def get_timestamp(self):
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")

