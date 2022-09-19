import typing

import yaml

from sqlalchemy import create_engine, text
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import Engine

# getting declarative class
Base = declarative_base()
class Algorithm(Base):
    __tablename__ = 'algorithms'

    id = Column(Integer, nullable=False, primary_key=True)
    operation = Column(String)
    example = Column(String)
    complexity = Column(String)
    #type (int)




class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, nullable=False, primary_key=True)
    login = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)#default=datetime.utcnow
    last_request = Column(DateTime)

    def __str__(self):
        return f"<User: id={self.id} login={self.login} password={self.password}>"


def main() -> None:
    # read the configs
    with open("config.yaml", "r") as f:
        conf: typing.Dict[str, typing.Any] = yaml.safe_load(f)

    #create engine
    db_url: str = f"postgresql://{conf['db']['user']}:{conf['db']['password']}@{conf['db']['host']}:{conf['db']['port']}/{conf['db']['name']}"
    print(f"Connection to {db_url}")
    db_engine: Engine = create_engine(db_url)

    # create the tables
    Base.metadata.create_all(db_engine)
    print("Tables created.")

if __name__ == "__main__":
    main()