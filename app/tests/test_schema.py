""" A test for schema.py """

import sys
sys.path.append('//itsc-pg2.storage.p.unibas.ch/ub-home$/hinder0000/Documents/GitHub/bartoc-graphql/app')
import graphene
import graphene.test
import time
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import skosmos  # local
import schema   # local

skosmosqueries = ["""{resultsSkosmosTimed(searchword:"bla") {
  uri
  type_
  preflabel
  altlabel
  hiddenlabel
  lang
  notation
  vocab
  exvocab
}}""",
                  """{resultsSkosmosTimed(searchword:"dog") {
  uri
  type_
  preflabel
  altlabel
  hiddenlabel
  lang
  notation
  vocab
  exvocab
}}""",
                  """{resultsSkosmosTimed(searchword:"rennrad") {
  uri
  type_
  preflabel
  altlabel
  hiddenlabel
  lang
  notation
  vocab
  exvocab
}}""",
                  """{resultsSkosmosTimed(searchword:"8698fqJJJJJ") {
  uri
  type_
  preflabel
  altlabel
  hiddenlabel
  lang
  notation
  vocab
  exvocab
}}""",
                  """{resultsSkosmosTimed(searchword:"logic") {
  uri
  type_
  preflabel
  altlabel
  hiddenlabel
  lang
  notation
  vocab
  exvocab
}}"""]

sparqlqueries = ["""{resultsSparqlTimed(searchword:"bla",queryname:"http://vocab.getty.edu/queries#Full_Text_Search_Query") {
  subject
  term
  parents
  descr
  scopenote
  type_
  extrakind
}}""",
                 """{resultsSparqlTimed(searchword:"dog",queryname:"http://vocab.getty.edu/queries#Full_Text_Search_Query") {
  subject
  term
  parents
  descr
  scopenote
  type_
  extrakind
}}""",
                 """{resultsSparqlTimed(searchword:"rennrad",queryname:"http://vocab.getty.edu/queries#Full_Text_Search_Query") {
  subject
  term
  parents
  descr
  scopenote
  type_
  extrakind
}}""",
                 """{resultsSparqlTimed(searchword:"8698fqJJJJJ",queryname:"http://vocab.getty.edu/queries#Full_Text_Search_Query") {
  subject
  term
  parents
  descr
  scopenote
  type_
  extrakind
}}""",
                 """{resultsSparqlTimed(searchword:"logic",queryname:"http://vocab.getty.edu/queries#Full_Text_Search_Query") {
  subject
  term
  parents
  descr
  scopenote
  type_
  extrakind
}}"""]

def test_Query():
    client = graphene.test.Client(schema.schema)
    for query in skosmosqueries:
        client.execute(query)
    for query in sparqlqueries:
        client.execute(query)
    print ("OK")
    
test_Query()
