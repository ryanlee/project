from sqlalchemy.ext.declarative import declarative_base

##  
##  from flask_sqlalchemy import SQLAlchemy
##  from sqlalchemy.ext.hybrid import hybrid_property
##  
##  # create a new SQLAlchemy object
##  db = SQLAlchemy()

Base = declarative_base()
##  # Base model that for other models to inherit from
##  class Base(db.Model):
##      __abstract__ = True
##  
##      id = db.Column(db.Integer, primary_key=True, autoincrement=True)
##      date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
##      date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
##                                onupdate=db.func.current_timestamp())


from sqlalchemy import Column, Integer, String, DateTime

# Model to store user details
class Users(Base):
    __tablename__ = 'users'
    id            = Column(Integer, primary_key=True, autoincrement=True)
    #  date_created  = Column(DateTime, default=db.func.current_timestamp())
    #  date_modified = Column(DateTime, default=db.func.current_timestamp(),onupdate=db.func.current_timestamp())
    email         = Column(String(100), unique=True)
    username      = Column(String(50), unique=True)
    password      = Column(String(300))  # incase password hash becomes too long

    #  def __repr__(self):
    #      return self.username
##  
##  def init_app(app):
##      db.init_app(app)

def init_cli (config):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    session = sessionmaker(bind=engine)
    db = scoped_session(session)

    # Adds Query Property to Models - enables `User.query.query_method()`
    Base.query = db.query_property()
    return db

def init_app (app):
    from flask_sqlalchemy import SQLAlchemy
    #  from data import Base
    db = SQLAlchemy(model_class=Base)
    db.init_app(app)
    return db
