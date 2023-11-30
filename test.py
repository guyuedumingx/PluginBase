import requests
from bs4 import BeautifulSoup
import dataset

url = "https://www.qqxiuzi.cn/bianma/dianbao.html"
resp = requests.get(url)
resp.encoding = resp.apparent_encoding
soup = BeautifulSoup(resp.content)
db = dataset.connect("sqlite:///plug.db")
table = db['中文商用电码表']

res = {}
for line in soup.find_all("tr"):
    key = line.td
    value = key.next_sibling
    table.insert(dict(key=key.text, value=value.text))
items = table.all()
print(items)
