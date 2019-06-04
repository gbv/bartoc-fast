##DEPENDENCIES:
#None

##CLASSES:
#a database with entries
class Database:
    def __init__(self, entries=set):
        self.entries = entries

    def set_entries(self, entries):
        self.entries = entries

    def add_entries(self, entries):
        self.entries = entries.union(self.entries)

    def get_entries(self):
        return self.entries
