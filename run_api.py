import typing
import yaml
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from enum import IntEnum
import tornado.web
import tornado.ioloop
# importing a database table class
from db_init import User, Algorithm


class Types(IntEnum):
    list = 0
    set = 1
    dict = 2


def database_initialization(conf: dict[str:dict[str:typing.Any]]) -> Session:
    """
    A session with the database is initialized
    @:param conf
    @:return db_session
    """
    db_url = f"postgresql://{conf['db']['user']}:{conf['db']['password']}@{conf['db']['host']}:{conf['db']['port']}/{conf['db']['name']}"
    print(f"Connection to {db_url}")
    db_engine = create_engine(db_url)
    db_session = Session(db_engine)
    return db_session


def main() -> None:
    # read the configs
    with open("config.yaml", "r") as f:
        conf: typing.Dict[str, typing.Any] = yaml.safe_load(f)

    # connect to DB
    db_session: Session = database_initialization(conf)

    # web app handlers

    class RegHandler(tornado.web.RequestHandler):
        def get(self):
            # registration page
            self.write("""<html><body>
                     <form action="/api/registration" method="post">
                            login: <input type="text" name="login"><br>
                            password: <input type="password" name="password"><br>
                            <input type="submit" value="Submit">
                     </form>
                 </body></html>""")

        def post(self):
            # getting the values from the form
            login = self.get_argument("login")
            password = self.get_argument("password")
            # checking for data in fields and entering values into the database
            if not (login and password):
                self.send_error(401)
                return
            else:
                row: int = db_session.query(User).count()
                data_row = User(id=row + 1, login=login, password=password)
                db_session.add(data_row)
                db_session.commit()
                db_session.close()

    class LoginHandler(tornado.web.RequestHandler):

        def get(self) -> None:
            user: bytes = self.get_secure_cookie("user")
            if not user:
                # authorization page
                self.write("""<html><body>
                     <form action="/api/login" method="post">
                            login: <input type="text" name="login"><br>
                            password: <input type="password" name="password"><br>
                            <input type="submit" value="Sign in">
                     </form>
                 </body></html>""")
            else:
                self.write({"Hello": user.decode('utf-8')})

        def post(self) -> None:

            login: str = self.get_argument("login")
            password: str = self.get_argument("password")

            if not (login and password):
                self.send_error(401)
                return

            # check password
            user = db_session.execute(
                select(User)
                .where(User.login == login)
                .where(User.password == password)
            ).first()

            if not user:
                self.send_error(401)
                return

            self.set_secure_cookie("user", login)
            self.write({"Hello": login})

    class DataHandler(tornado.web.RequestHandler):

        def get(self) -> None:
            user: bytes = self.get_secure_cookie("user")
            # cookie verification
            if not user:
                self.send_error(401)
                return

            # select datas from DB
            data_coll = db_session.execute(select(Algorithm)).all()
            db_json: typing.Dict[str, typing.Any] = {"data": [], "total": len(data_coll)}
            for it, row in enumerate(data_coll):
                data: Algorithm = row[0]
                db_json["data"].append({"id ": data.id, "operation ": data.operation, "example ": data.example,
                                        "complexity ": data.complexity, "note ": repr(data.note),
                                        "type ": Types(data.type).name})

            # send datas
            self.write(f"<html><body>{db_json}</body></html>")

    # web app initialization
    application = tornado.web.Application([(r"/api/login", LoginHandler),
                                           (r"/api/data", DataHandler),
                                           (r"/api/registration", RegHandler)],
                                          cookie_secret='W1fer')
    application.listen(conf['web_app']['port'])
    print("App started")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
