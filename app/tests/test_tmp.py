##DEPENDENCIES:
import sys
sys.path.append('//itsc-pg2.storage.p.unibas.ch/ub-home$/hinder0000/Documents/GitHub/bartoc-graphql/app')
#local:
import schema
import skosmos
import sparql

def sparql_test(searchword, queryname):
    base = sparql.SparqlDatabase([])
    endpoints = base.get_entries()
    for endpoint in endpoints:
        jsondata = endpoint.search(searchword, queryname)
        test = schema.normalize_sparql(jsondata)
        print (test)

sparql_test("lambda", "http://vocab.getty.edu/queries#Full_Text_Search_Query")


"""sparql.py:
def test():
    a = SparqlDatabase([])
    a.setup()
    print (a.get_entries())

def test2():
    a = SparqlDatabase([]).setup()
    print (a.get_entries())

def test3(searchword, queryname):#visualizes data structure
    base = SparqlDatabase([])
    endpoints = base.get_entries()
    print (endpoints)
    for endpoint in endpoints:
        print (endpoint)
        print (endpoint.get_queries())
        print (endpoint.search(searchword, queryname))
        print (endpoint.search2(searchword, queryname))

#a = test3("lambda", "http://vocab.getty.edu/queries#Full_Text_Search_Query")
"""


"""schema.py:
#prints result of query which is written in GraphQL syntax

def test():
    test1()
    test2()
    
def test1():
    query = ""{resultsParallel(searchword:"rennrad") {
  uri
  kind
  preflabel
  altlabel
  hiddenlabel
  lang
  notation
  vocab
  exvocab
}}""
    result = schema.execute(query)
    print (result.data)

def test2():
    query = ""{resultsMulti(searchword:"rennrad", language:"de") {
  uri
  kind
  preflabel
  altlabel
  hiddenlabel
  lang
  notation
  vocab
  exvocab
}}""
    result = schema.execute(query)
    print (result.data)

def sparql_test(searchword, queryname):
    base = sparql.SparqlDatabase([])
    endpoints = base.get_entries()
    for endpoint in endpoints:
        jsondata = endpoint.search(searchword, queryname)
        test = normalize_sparql(jsondata)

#test()
#sparql_test("lambda", "http://vocab.getty.edu/queries#Full_Text_Search_Query")
"""
