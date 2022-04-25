import sqlalchemy
from .db_session import SqlAlchemyBase
from datetime import datetime


class Mods(SqlAlchemyBase):  # class to make table with available mods
    __tablename__ = 'mods'

    # making fields to fill them with mods' data
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    description = sqlalchemy.Column(sqlalchemy.String, default='')
    brand = sqlalchemy.Column(sqlalchemy.String)
    model = sqlalchemy.Column(sqlalchemy.String)
    year = sqlalchemy.Column(sqlalchemy.Integer)
    image = sqlalchemy.Column(sqlalchemy.String)
    link = sqlalchemy.Column(sqlalchemy.String, unique=True)
    author = sqlalchemy.Column(sqlalchemy.String)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)
