""" A test for skosmos.py """

import sys
sys.path.append('//itsc-pg2.storage.p.unibas.ch/ub-home$/hinder0000/Documents/GitHub/bartoc-graphql/app')
import skosmos  # local
import data     # local

searchwords = ["bike", "fahrrad", "velo", "rennvelo"]
url = "https://bartoc-skosmos.unibas.ch"
name = "Bartoc"

def test_SkosmosInstance():
    testinstance = skosmos.SkosmosInstance(name, url)
    for searchword in searchwords:
        result = testinstance.search(searchword)
        with open(f'files/skosmos_{searchword}.json', encoding="utf-8") as file:
            correct_result = skosmos.json.load(file) # json is imported via skosmos
            file.close()
            assert str(result) == str(correct_result), "SkosmosInstance.search failure" # compare str since dict comparison is hard 
        
def test_SkosmosDatabase():
    testbase = skosmos.SkosmosDatabase([])
    urlsprocessed = []
    for instance in testbase.get_entries():
        assert type(instance) == skosmos.SkosmosInstance, "SkosmosDatabase.setup failure: wrong type"
        urlsprocessed.append(instance.get_url())
    urlsraw = []
    for entry in data.skosmosinstances:
        urlsraw.append(entry[0])
    assert set(urlsprocessed) == set(urlsraw), "SkosmosDatabase.setup failure: incomplete"
    
def test_skosmos():
    testbase = skosmos.SkosmosDatabase([])
    for instance in testbase.get_entries():
        for searchword in searchwords:
            instance.search(searchword) # add file checking here
    
test_SkosmosInstance()
test_SkosmosDatabase()
test_skosmos()
        
        
