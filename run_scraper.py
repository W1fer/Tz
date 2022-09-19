import requests
from parsel import Selector
from prettytable import PrettyTable

table = PrettyTable()

url = 'https://proglib.io/p/slozhnost-algoritmov-i-operaciy-na-primere-python-2020-11-03'
headers = {
    "Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User - Agent":
        "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36"
}
req = requests.get(url, headers=headers).text

print(1)
