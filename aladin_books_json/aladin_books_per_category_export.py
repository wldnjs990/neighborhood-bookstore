import requests
import time
import json

# from pprint import pprint as print


API_KEY = ''

url = 'http://www.aladin.co.kr/ttb/api/ItemList.aspx'



# params = {
#     'ttbkey': API_KEY,
#     'Query': '그',
#     'QueryType': 'Title',
#     'MaxResults': 100,
#     'start': 1,
#     'SearchTarget': 'Book',
#     'output': 'js',
#     'Version': 20131101
# }

# response = requests.get(url, params=params).json()
# print(response)


QueryType = ['Bestseller', 'ItemNewAll', 'ItemNewSpecial', 'BlogBest']
books_by_qt = {
    "domestic": {},
    "foreign": {},
}

CATEGORY = {
    "domestic": 0,
    "foreign": 90854
}
for country, cat_id in CATEGORY.items():
    for qt in QueryType:

        books_by_qt[country][qt] = []

        for page in range(1, 21):
            params = {
                "ttbkey": API_KEY,
                "QueryType": qt,
                "MaxResults": 50,
                "start": page,
                "CategoryId": cat_id,
                "SearchTarget": "Book",
                "output": "js",
                "Version": "20131101",
            }

            res = requests.get(url, params=params)
            data = res.json()
            items = data.get("item", [])

            books_by_qt[country][qt].extend(items)
            print(f"[{qt}] {page}페이지 수집 완료 ({len(items)}권)")
            time.sleep(1)

        print(f"[{qt}] 총 수집 권수: {len(books_by_qt[country][qt])}")

        filename = f"aladin_{country}_{qt}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(books_by_qt[country][qt], f, ensure_ascii=False, indent=2)

        print(f"[{country}_{qt}] JSON 파일 저장 완료 → {filename}")
