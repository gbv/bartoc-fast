""" A test for schema.py: py -3.7 ./manage.py test bartocfast.tests.test_schema """

from django.test import SimpleTestCase

import time
from typing import List, Set, Dict, Tuple, Optional

import json
import graphene

from ..schema import GlobalResult, Query, Normalize     # local
from ..utility import Result                            # local

class Test_normalize_sparql(SimpleTestCase):
    """ Test Normalize.normalize_sparql """

    def setUp(self) -> None:
        self.searchword = "turtle"
        with open(f'//itsc-pg2.storage.p.unibas.ch/ub-home$/hinder0000/Documents/GitHub/bartocfast/django/bartocfast/tests/files/schema_normalize_sparql_{self.searchword}.json', encoding="utf-8") as file:
            data = json.load(file)
            file.close()
        self.result = Result("Getty", data, 0)

    def test_aggregation(self) -> List[GlobalResult]:
        """ Test whether results get correctly aggregated """

        output = Normalize.normalize_sparql(self.result)
        fields = GlobalResult.fields()
        print(fields)
        for globalresult in output:
            for field in fields:
                pass
                # print(getattr(globalresult, field))

