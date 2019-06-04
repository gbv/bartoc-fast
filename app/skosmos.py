##DEPENDENCIES:
import urllib
import json
#local:
import data
import utility

##CLASSES:
#a collection of SkosmosInstances
class SkosmosDatabase(utility.Database):
    def __init__(self, entries=set):
        utility.Database.__init__(self, entries)
        self.setup() #setup is called on initializing class

    def setup(self):
        for entry in data.skosmosinstances:
            self.add_entries(set([SkosmosInstance(entry[0], entry[1])]))

#s skosmos instance with a name and singular search method
class SkosmosInstance:
    def __init__(self, url=str, name=str):
        self.url = url
        self.name = name

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    #returns as dictionary the output of http://api.finto.fi/doc/#!/Global_methods/get_search of word on url 
    def search(self, word):
        restapi = self.url + "/rest/v1/search?query=" + word
        response = urllib.request.urlopen(restapi)
        data = json.loads(response.read())
        return data
