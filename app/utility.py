""" utility.py """

class Database:
    """ A database """
    def __init__(self, entries: set) -> None:
        self.entries = entries

    def set_entries(self, entries: set) -> None:
        self.entries = entries

    def add_entries(self, entries: set) -> None:
        self.entries = entries.union(self.entries)

    def get_entries(self) -> set:
        return self.entries

class Entry:
    """ A named and linked entry of a database """
    def __init__(self, name: str, url: str) -> None:
        self.name = name
        self.url = url
        
    def set_url(self, url: str) -> None:
        self.url = url

    def get_url(self)-> str:
        return self.url

    def set_name(self, name: str) -> None:
        self.name = name

    def get_name(self) -> str:
        return self.name
