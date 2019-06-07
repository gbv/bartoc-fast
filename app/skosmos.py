import urllib.request
import json
import data     # local
import utility  # local

class SkosmosDatabase(utility.Database):
    """ A collection of Skosmos instances """
    def __init__(self, entries: set) -> None:
        utility.Database.__init__(self, entries)
        self.setup() # setup is called on initializing class

    def setup(self) -> None:
        """ Populates the database with Skosmos instances """
        for entry in data.skosmosinstances:
            self.add_entries(set([SkosmosInstance(entry[0], entry[1])]))

class SkosmosInstance(utility.Entry):
    """ A Skosmos instance """
    def __init__(self, url: str, name: str) -> None:
        utility.Entry.__init__(self, name, url)
        
    def search(self, searchword: str) -> dict:
        """ Calls Global_methods/get_search for searchword at instance's REST API """
        restapi = self.url + "/rest/v1/search?query=" + searchword
        response = urllib.request.urlopen(restapi)
        data = json.loads(response.read())
        return data
