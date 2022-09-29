import datetime
import typing

import yaml

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.future import Engine
from sqlalchemy_utils import create_database, database_exists, drop_database

# getting declarative class
Base = declarative_base()


class Algorithm(Base):
    __tablename__ = 'algorithms'

    id = Column(Integer, nullable=False, primary_key=True)
    operation = Column(String)
    example = Column(String)
    complexity = Column(String)
    note = Column(String)
    type = Column(Integer)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, nullable=False, primary_key=True)
    login = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
    last_request = Column(DateTime)



def main() -> None:
    # read the configs
    with open("config.yaml", "r") as f:
        conf: typing.Dict[str, typing.Any] = yaml.safe_load(f)

    # create engine
    db_url: str = f"postgresql://{conf['db']['user']}:{conf['db']['password']}@{conf['db']['host']}:{conf['db']['port']}/{conf['db']['name']}"
    print(f"Connection to {db_url}")
    db_engine: Engine = create_engine(db_url)

    # check and deleting the database
    if database_exists(db_engine.url):
        drop_database(db_engine.url)

    # database initialization
    create_database(db_engine.url)
    print("Сreating a database.")

    # Tables created
    Base.metadata.create_all(db_engine)
    print("Creating tables.")


if __name__ == "__main__":
    main()
