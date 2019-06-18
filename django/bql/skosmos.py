import urllib.request
import json

from .utility import Database, Entry    # local
from .data import skosmosinstances      # local

class SkosmosDatabase(Database):
    """ A collection of Skosmos instances """
    def __init__(self, entries: set = {}) -> None:
        Database.__init__(self, entries)
        self.setup() # setup is called on initializing class

    def setup(self) -> None:
        """ Populates the database with Skosmos instances """
        for entry in skosmosinstances:
            self.add_entries(set([SkosmosInstance(entry[1], entry[0])]))

class SkosmosInstance(Entry):
    """ A Skosmos instance """
    def __init__(self, name: str, url: str) -> None:
        Entry.__init__(self, name, url)
        
    def search(self, searchword: str) -> dict:
        """ Calls Global_methods/get_search for searchword at instance's REST API """
        restapi = self.url + "/rest/v1/search?query=" + searchword
        response = urllib.request.urlopen(restapi)
        results = json.loads(response.read())
        return results
