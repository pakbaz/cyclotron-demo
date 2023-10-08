from sqlalchemy import Column, DateTime, Integer, String

from app import db


class Joke(db.Model):
    __tablename__ = 'joke'
    id = Column(Integer, primary_key=True)
    type = Column(String(50))
    setup = Column(String(500))
    punchline = Column(String(250))
    fetchDate = Column(DateTime)

    def __str__(self):
        return self.name
