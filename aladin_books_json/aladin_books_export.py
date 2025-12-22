import requests
import time
import json

API_KEY = ''


url = 'http://www.aladin.co.kr/ttb/api/ItemList.aspx'


QueryType = ['Bestseller', 'ItemNewAll', 'ItemNewSpecial', 'BlogBest']

CATEGORY = {
    "domestic": 0,
    "foreign": 90854
}

unique_books = {}

for country, cat_id in CATEGORY.items():
    for qt in QueryType:
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

            for book in items:
                key = book.get("isbn13") or book.get("itemId")

                if key:
                    unique_books[key] = book

            print(f"[{qt}] {page}페이지 완료 ({len(items)}권)")
            time.sleep(1)

print("\n✅ 전체 수집 완료")

# ✅ dict → list 변환
total_books = list(unique_books.values())

print(f"📚 최종 수집 도서 수 (중복 제거 후): {len(total_books)}")

# ✅ 하나의 JSON 파일로 저장
filename = "Total_books_json.json"
with open(filename, "w", encoding="utf-8") as f:
    json.dump(total_books, f, ensure_ascii=False, indent=2)

print(f"💾 JSON 파일 저장 완료 → {filename}")