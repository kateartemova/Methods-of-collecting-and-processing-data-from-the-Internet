from lxml import html
import requests
from pprint import pprint
from pymongo import MongoClient

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36'}
main_url = 'https://yandex.ru/news/'

response = requests.get(main_url, headers=headers)

client = MongoClient('localhost', 27017)
db = client['news']
news = db.news

dom = html.fromstring(response.text)
items = dom.xpath("//div[contains(@class, 'news-feed')]")

list_items = []
for item in items[1:]:
    item_info = {}
    name = item.xpath(".//a[contains(@class, 'mg-card__link')]/text()")
    source = item.xpath(".//a[contains(@class, 'mg-card__source-link')]/text()")
    link = item.xpath(".//a[contains(@class, 'mg-card__link')]/@href")
    date = item.xpath(".//span[@class = 'mg-card-source__time']/text()")

    item_info['name'] = name
    item_info['source'] = source
    item_info['link'] = link
    item_info['date'] = date
    list_items.append(item_info)

pprint(list_items)

for item in list_items:
    news.update_one(item, {'$setOnInsert': item}, upsert=True)
    print(item)
