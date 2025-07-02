import datetime

class Person:
    """Used for temporary data storage when retrieving data from the database and displaying it on discord"""
    def __init__(self, name: str, birthday: datetime.date):
        self.name = name
        self.birthday = birthday