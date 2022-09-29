import re
import typing
import requests
import yaml
import argparse
from parsel import Selector
from prettytable import PrettyTable
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# importing a database table class
from db_init import Algorithm


def get_the_path_to_tables(url: str) -> list[str]:
    """
        Receives the url as input and returns a list of required tables
        @:param url
        @:return table_path
    """
    headers = {
        "Accept":
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User - Agent":
            "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36"
    }
    # html code of the page
    req = requests.get(url, headers=headers).text
    selector = Selector(text=req)

    # the path to the required tables
    table_path = selector.xpath('//table').getall()[:-1]
    return table_path


def get_the_contents_of_tables(selector_table_path: Selector) -> list[list[list[str]]]:
    """
    Getting values from rows of paired tables
    @:param selector_table_path:
    @:return table_contents
    """
    table_contents = []

    number_of_rows = len(selector_table_path.xpath('//td[1][descendant-or-self::text()]|//td[1][not(text())]').getall())
    for item_number in range(number_of_rows):
        table_contents.append([])
        for element in range(1, 5):
            if element == 4 or element == 1:
                # processing the first and fourth columns of the table
                table_contents[item_number].append(re.sub(r'<[^>]*>', ' ', selector_table_path.xpath(
                    f'//td[{element}][descendant-or-self::text()]|//td[{element}][not(text())]').getall()[
                    item_number]).strip())
            else:
                table_contents[item_number].append(
                    selector_table_path.xpath(f'//td[{element}]//text()').getall()[item_number])
    return table_contents


def fill_in_the_table(table: PrettyTable, content: list[list[list[list[str]]]]) -> PrettyTable:
    """
    Filling the table with fields from the list of values
    @:param table
    @:param content
    @:return table
    """
    for table_number in range(len(content)):
        # adding rows to a table
        table.add_rows(content[table_number][1:])

    return table


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


def add_data_to_the_database(list_table_content: list[list[list[list[str]]]], db_session: Session) -> None:
    """
    Entering data into the database
    @:param list_table_content
    @:param db_session
    @:return: None
    """
    id_num = 0
    for table in range(len(list_table_content)):
        for rows in range(1, len(list_table_content[table])):
            id_num += 1
            data_row = Algorithm(id=id_num, operation=list_table_content[table][rows][0],
                                 example=list_table_content[table][rows][1],
                                 complexity=list_table_content[table][rows][2], note=list_table_content[table][rows][3],
                                 type=table)
            db_session.add(data_row)
            db_session.commit()
            db_session.close()


def str_to_bool(line: str) -> bool:
    if line.lower() in ('yes', 'true', 't', 'y'):
        return True
    if line.lower() in ('no', 'false', 'f', 'n'):
        return False


def main() -> None:
    # parse script arguments
    parser = argparse.ArgumentParser(
        description="Collecting tables from the site and output to the console or database.")
    parser.add_argument("--dry_run", "-d_r",
                        help="Specify the parameter True to output the table to the console or False to write values to the database",
                        default='True', dest="dry_run")
    args: argparse.Namespace = parser.parse_args()

    url = 'https://proglib.io/p/slozhnost-algoritmov-i-operaciy-na-primere-python-2020-11-03'

    # the path to the required tables
    table_path: list[str] = get_the_path_to_tables(url)

    list_of_table_contents: list[list[list[list[str]]]] = []
    selector_table_path: list[Selector] = []

    for table_number in range(len(table_path)):
        # converting values to the Selector type
        selector_table_path.append(Selector(table_path[table_number]))

        # filling the list with values from the received tables
        list_of_table_contents.append(get_the_contents_of_tables(selector_table_path[table_number]))

    if str_to_bool(args.dry_run):

        # output in console
        table = PrettyTable()

        # adding field names to a table
        table.field_names = list_of_table_contents[0][0]

        # formation of the resulting table
        resulting_table: PrettyTable = fill_in_the_table(table, list_of_table_contents)
        print(resulting_table)
    else:
        with open("config.yaml", "r") as f:
            conf: dict[dict[str:typing.Any]] = yaml.safe_load(f)
        db_session: Session = database_initialization(conf)

        # number of rows in the Algorithm table
        rows: int = db_session.query(Algorithm).count()

        # delete old data
        if rows != 0:
            print('Deleting old data...')
            # delete
            db_session.query(Algorithm).delete()
            db_session.commit()

        # insert new data
        print('Adding new data...')
        add_data_to_the_database(list_of_table_contents, db_session)
        print(f"DB succesfull updated!")


if __name__ == "__main__":
    main()
