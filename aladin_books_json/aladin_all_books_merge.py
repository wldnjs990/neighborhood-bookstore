import json

CATEGORY = ["domestic", "foreign"]

for category in CATEGORY:
    FILES = [
        f"aladin_{category}_Bestseller.json",
        f"aladin_{category}_BlogBest.json",
        f"aladin_{category}_ItemNewAll.json",
        f"aladin_{category}_ItemNewSpecial.json",
    ]

    unique_books = {}
    stats = {}
    for file in FILES:
        with open(file, "r", encoding="utf-8") as f:
            books = json.load(f)

        stats[file] = len(books)

        for book in books:
            isbn = book.get("isbn13")
            if not isbn:
                continue
            # isbn13 기준 중복 제거
            if isbn not in unique_books:
                unique_books[isbn] = book

    # 최종 결과
    final_books = list(unique_books.values())

    print("📊 파일별 원본 개수")
    for k, v in stats.items():
        print(f"- {k}: {v}권")

    print("\n✅ 중복 제거 후 총 권수:", len(final_books))

    # JSON 저장
    with open(f"aladin_{category}_books.json", "w", encoding="utf-8") as f:
        json.dump(final_books, f, ensure_ascii=False, indent=2)

    print(f"\n📁 aladin_{category}_books.json 저장 완료")



FILES = [
        "aladin_domestic_books.json",
        "aladin_foreign_books.json",
    ]

unique_books = {}
stats = {}
for file in FILES:
    with open(file, "r", encoding="utf-8") as f:
        books = json.load(f)

    stats[file] = len(books)

    for book in books:
        isbn = book.get("isbn13")
        if not isbn:
            continue
        # isbn13 기준 중복 제거
        if isbn not in unique_books:
            unique_books[isbn] = book

# 최종 결과
final_books = list(unique_books.values())

print("📊 파일별 원본 개수")
for k, v in stats.items():
    print(f"- {k}: {v}권")

print("\n✅ 중복 제거 후 총 권수:", len(final_books))

# JSON 저장
with open("aladin_total_books.json", "w", encoding="utf-8") as f:
    json.dump(final_books, f, ensure_ascii=False, indent=2)

print("\n📁 aladin_total_books.json 저장 완료")