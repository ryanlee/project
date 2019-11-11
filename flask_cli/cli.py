#!/usr/bin/env python

#  from sqlalchemy import *
#  from sqlalchemy.ext.declarative import declarative_base
#  from sqlalchemy import Column, Integer, String, DateTime
#  from sqlalchemy import create_engine
#  from sqlalchemy.orm import scoped_session, sessionmaker
#

import config
#  SQLALCHEMY_DATABASE_URI = 'postgresql:///flask'

from data import init_cli, Users
db = init_cli(config)


# Create Tables
#  Base.metadata.create_all(bind=engine)
def dump (msg=""):
    print(msg)
    for i in Users.query.all() :
        print(f"user {i.id} : {i.username}, {i.email} ")

dump("before add user")

user = Users(username="cli", email="cli@not-exists.com")
db.add(user)
db.commit()

dump("after add user")
