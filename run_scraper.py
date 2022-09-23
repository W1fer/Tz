import re
import requests
from parsel import Selector
from prettytable import PrettyTable


def getting_the_path_to_tables(url: str) -> list[str]:
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


def getting_the_contents_of_tables(selector_table_path: Selector) -> list[list[list[str]]]:
    """
    getting values from rows of paired tables
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


def filling_in_the_table(table: PrettyTable, content: list[list[list[list[str]]]]) -> PrettyTable:
    """
    filling the table with fields from the list of values
    @param table
    @param content
    @return table
    """
    for table_number in range(len(content)):
        # adding rows to a table
        table.add_rows(content[table_number][1:])

    return table


def main() -> None:
    table = PrettyTable()
    url = 'https://proglib.io/p/slozhnost-algoritmov-i-operaciy-na-primere-python-2020-11-03'
    # the path to the required tables
    table_path: list[str] = getting_the_path_to_tables(url)

    list_of_table_contents: list[list[list[list[str]]]] = []
    selector_table_path: list[Selector] = []

    for table_number in range(len(table_path)):
        # converting values to the Selector type
        selector_table_path.append(Selector(table_path[table_number]))
        # filling the list with values from the received tables
        list_of_table_contents.append(getting_the_contents_of_tables(selector_table_path[table_number]))

    # adding field names to a table
    table.field_names = list_of_table_contents[0][0]

    # formation of the resulting table
    resulting_table: PrettyTable = filling_in_the_table(table, list_of_table_contents)

    print(resulting_table)


if __name__ == "__main__":
    main()
