import sqlalchemy
from .db_session import SqlAlchemyBase
from datetime import datetime


class UserFols(SqlAlchemyBase):
    __tablename__ = 'userfols'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.String)
    brand = sqlalchemy.Column(sqlalchemy.String)
    model = sqlalchemy.Column(sqlalchemy.String)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)
