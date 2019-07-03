# not in use atm:
                         
class LanguageDatabase(Database):
    """ A collection of languages """
    
    def __init__(self, entries: set = {}) -> None:
        Database.__init__(self, entries)
        self.setup() # setup is called on initializing class

    def setup(self) -> None:
        """ Populate the database with languages """
        
        wb = load_workbook("//itsc-pg2.storage.p.unibas.ch/ub-home$/hinder0000/Documents/GitHub/bartoc-graphql/django/bartocgraphql/fixtures/languages.xlsx") # required for unittest; fixtures/languages.xlsx in production
        for ws in wb:
            vocabulary = []
            for row in ws.iter_rows(min_row=3, min_col=4, max_col=5, values_only=True):
                uri = row[0]
                name = row[1]
                vocabulary.append(Word(uri, name))
            self.add_entries({Language(ws['A3'].value, Namespace(ws['B3'].value, ws['C3'].value), vocabulary)})
        
class Language:
    """ A Language """
    
    def __init__(self, name: str = None, namespace: Namespace = None, vocabulary: List[Word] = None) -> None:
        self.name = name
        self.namespace = namespace
        self.vocabulary = vocabulary

    def flat(self, word):
        """ Return flattened word """
        
        try:
            assert word in self.vocabulary
        except AssertionError:
            return None
        return self.namespace.uri + word.name

class Namespace:
    """ A namespace """
    
    def __init__(self, uri: str = None, prefix: str = None) -> None:
        self.uri = uri
        self.prefix = prefix    
        
class Word:
    """ A word """

    def __init__(self, uri: str = None, name: str = None) -> None:
        self.uri = uri
        self.name = name