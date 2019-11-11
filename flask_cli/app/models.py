import data

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()
