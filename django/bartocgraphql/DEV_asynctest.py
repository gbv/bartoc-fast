import time # for dev
from typing import List, Set, Dict, Tuple, Optional, Union
import asyncio

import aiohttp
from aiosparql.client import SPARQLClient
from SPARQLWrapper import (SPARQLWrapper, JSON)

from DEV_sparql import SparqlDatabase, SparqlEndpoint
from DEV_skosmos import SkosmosDatabase, SkosmosInstance
from utility import Result

DATABASE = SkosmosDatabase()
for entry in DATABASE.entries:
    if entry.name == "UNESCO":
        global UNESCO
        UNESCO = entry
    elif entry.name == "Bartoc":
        global BARTOC
        BARTOC = entry
    elif entry.name == "AgroVoc":
        global AGROVOC
        AGROVOC = entry

SPARQLDB = SparqlDatabase()
for entry in SPARQLDB.entries:
    if entry.name == "LuSTRE":
        global LUSTRE
        LUSTRE = entry

ALLENTRIES = set()
ALLENTRIES = ALLENTRIES.union(SPARQLDB.entries)
ALLENTRIES = ALLENTRIES.union(DATABASE.entries)

SEARCHWORDS = ["rennrad", "water", "kohl"]

# orginal:
async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

# working:
async def fetch_UNESCO(session, searchword, category):    
    restapi = UNESCO.url + "/rest/v1/search?query=" + searchword
    async with session.get(restapi) as response:
        return await response.json()

async def fetch_BARTOC(session, searchword, category):    
    restapi = BARTOC.url + "/rest/v1/search?query=" + searchword
    async with session.get(restapi) as response:
        return await response.json()

async def fetch_AGROVOC(session, searchword, category):    
    restapi = AGROVOC.url + "/rest/v1/search?query=" + searchword
    async with session.get(restapi) as response:
        return await response.json()

async def fetch_AGROVOC_2(session, searchword, category):    
    restapi = AGROVOC.url + "/rest/v1/search?query=" + searchword
    async with session.get(restapi) as response:
        data = await response.json()
        return Result(AGROVOC, data, category)

async def main():
    async with aiohttp.ClientSession() as session:

        output = await asyncio.gather(*[entry.a_search(session, "water", 0) for entry in DATABASE.entries])

        # output is a list of all JSONs:
        output = await asyncio.gather(
            AGROVOC.a_search(session, "water", 0),
            fetch_AGROVOC_2(session, "water", 0),
            fetch_BARTOC(session, "water", 0),
            fetch_UNESCO(session, "water", 0),
            )

        print(output)
        print(len(output))
        print(type(output))
    
        await session.close()


async def main_2():
    async with aiohttp.ClientSession() as session:

        # output is list of Results
        output = await asyncio.gather(*[entry.a_search(session, "water", 0) for entry in DATABASE.entries])

        print(output)
        print(len(output))
        print(type(output))
    
        await session.close()

# working prototype:
async def main_3(searchword: str, category: int = 0) -> List[Result]:
    async with aiohttp.ClientSession() as session:
        start = time.time()

        # output is list of Results
        output = await asyncio.gather(*[entry.a_search(session, searchword, 0) for entry in DATABASE.entries])

        print(output)
       
        await session.close()
        
        end = time.time()
        print(end - start)

        return output

# new stuff:
async def main_4(searchword: str, category: int = 0) -> List[Result]:
    async with aiohttp.ClientSession() as session:
        start = time.time()

        # output is list of Results
        # output = await asyncio.gather(*[entry.a_search(session, searchword, 0) for entry in DATABASE.entries])

        output = await asyncio.gather(
            AGROVOC.a_search(session, "water", 0),
            LUSTRE.a_search(session, "water", 0),
            )

        print(output)
       
        await session.close()
        
        end = time.time()
        print(end - start)

        return output

# working but slow???
async def main_5(searchword: str, category: int = 0) -> List[Result]:
    async with aiohttp.ClientSession() as session:
        start = time.time()

        # output is list of Results
        output = await asyncio.gather(*[entry.a_search(session, word, 0) for entry in ALLENTRIES for word in SEARCHWORDS])
       
        await session.close()
        
        end = time.time()
        print(f'ASYNC TOTAL took {end - start}')

        return output

        
def bla(searchword):
    start = time.time()
    results = []
    for entry in ALLENTRIES:
        for searchword in SEARCHWORDS:
            results.append(entry.search(searchword))
    end = time.time()
    print(f'SYNC TOTAL took {end - start}')
    return results

#a = asyncio.run(main_3("water"))


a = asyncio.run(main_5("rennrad"))
bla("rennrad")





