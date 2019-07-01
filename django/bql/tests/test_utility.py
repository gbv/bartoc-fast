""" A test for utility.py """

from django.test import SimpleTestCase

from ..utility import LanguageDatabase, MappingDatabase # local

FAILURE = "incorrect value"
        
class TestLanguageDatabase(SimpleTestCase):

    def setUp(self) -> None:
        self.languagedatabase = LanguageDatabase() 
        
    def test_setup(self) -> None:
        """ Ensure that all languages have been added from fixtures """

        self.assertEqual(len(self.languagedatabase.entries), 1, FAILURE) # check fixtures/languages.xlsx to see how many languages there should be

    def test_consistency(self) -> None:
        """ Ensure that flattened URIs match given URIs """
        
        for language in self.languagedatabase.entries:
            for word in language.vocabulary:
                # print(language.flat(word))
                # print(word.uri)
                self.assertTrue(language.flat(word) == word.uri, FAILURE)

class TestMappingDatabase(SimpleTestCase):

    def setUp(self) -> None:
        self.mappingdatabase = MappingDatabase()

    def test_setup(self) -> None:
        for mapping in self.mappingdatabase.entries:
            print(mapping.field)

    




