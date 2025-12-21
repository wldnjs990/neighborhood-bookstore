from django.core.management.base import BaseCommand
# 프로젝트 루트 경로 출력용 settings파일
from bookmarket import settings
from decouple import config
import os
import json
import re
import html

class Command(BaseCommand):
    """
    django management commend 기능 사용
    class명은 반드시 Command로 만들어줘야 함
    django 시스템이 자동으로 Command 클래스명이 있는 코드를 찾고 실행시켜주기 때문
    """
    help = 'categories.json를 활용해 카테고리별로 book_raw 데이터 분류 + loaddata 파일 생성'

    def handle(self, *args, **options):
        # book_raw, category 파일 읽기 ---------------------------------------------------------------------
        raw_json_file = os.path.join(settings.BASE_DIR / 'data' / 'book_raw.json')
        category_json_file = os.path.join(settings.BASE_DIR / 'data' / 'categories.json')
        with open(raw_json_file, 'r', encoding='utf-8') as f:
            books = json.load(f)
        with open(category_json_file, 'r', encoding='utf-8') as f:
            categories = json.load(f)
        
        # 추출 준비 ---------------------------------------------------------------------
        print('추출 준비')
        # 카테고리별로 추출된 도서 수를 추적할 딕셔너리
        category_counts = {category["pk"]: 0 for category in categories}
        # 카테고리별로 추출되는 도서를 저장할 리스트
        extracted_books = []
        # 각 도서에게 부여할 pk값
        fixture_pk = 1

        # 도서 데이터 조회 - 매핑 - 추출 --------------------------------------------------------------------
        print('도서 데이터 조회 - 매핑 - 추출 시작')
        for book in books:
            # 현재 도서 categoryId값(cid) 추출
            original_category = book.get('categoryId')
            # categoryId값(cid) int로 변환(문자열인 경우 대비용인듯?)
            original_category_int = int(original_category)
            
            # 대분류 category 8개 순회
            for category in categories:
                # category에 속해있는 cid들 추출
                cid_list = category.get("cid", [])
                # 현재 도서 cid가 category에 속해있다면
                if original_category_int in cid_list:
                    # category의 pk 가져오기
                    category_pk = category.get("pk")
                    # fixture_fields생성 + cid값 업데이트
                    fixture_fields = {"category_id": category_pk}
                    # 모델 만들때 필요한 필드값들
                    keys_to_copy = [
                        "title",
                        "isbn13",  # ← "isbn"이 아니라 "isbn13"
                        "author",
                        "publisher",
                        "pubDate",
                        "cover",
                        "description",
                        "priceStandard",
                        "priceSales",
                        "adult",
                        "itemId",
                        "mallType",
                        "customerReviewRank",
                        "bestRank",
                    ]

                    for key in keys_to_copy:
                        # 현재 도서에 들어가야할 필드값이 존재한다면
                        if key in book:
                            # 해당하는 필드값 담아주기
                            if key == "title":
                                fixture_fields["title"] = book[key]
                            # 2007년 이후로 isbn13이 책 번호 표쥰이 됨
                            elif key == "isbn13":
                                fixture_fields["isbn"] = book[key]
                            elif key == "author":
                                fixture_fields["author"] = book[key]
                            elif key == "publisher":
                                fixture_fields["publisher"] = book[key]
                            elif key == "pubDate":
                                fixture_fields["pub_date"] = book[key]
                            elif key == "cover":
                                fixture_fields["cover"] = book[key]
                            elif key == "description":
                                fixture_fields["description"] = book[key]
                            elif key == "priceStandard":
                                fixture_fields["price_standard"] = book[key]
                            elif key == "priceSales":
                                fixture_fields["price_sales"] = book[key]
                            elif key == "adult":
                                fixture_fields["adult"] = book[key]
                            elif key == "itemId":
                                fixture_fields["item_id"] = book[key]
                            elif key == "mallType":
                                fixture_fields["mall_type"] = book[key]
                            elif key == "customerReviewRank":
                                fixture_fields["customer_review_rank"] = book[key]
                            elif key == "bestRank":
                                fixture_fields["best_rank"] = book[key]

                    # auto_now_add, auto_now 필드 추가 (loaddata 시 필수)
                    from django.utils import timezone
                    current_time = timezone.now().isoformat()
                    fixture_fields["created_at"] = current_time
                    fixture_fields["updated_at"] = current_time

                    # fixture에 저장하기 위한 딕셔너리 형태로 구성(model, pk, fields) 
                    fixture_entry = {
                        "model": "books.book",
                        "pk": fixture_pk,
                        "fields": fixture_fields
                    }
                    # 만든 도서 데이터를 extracted_books 리스트에 저장 
                    extracted_books.append(fixture_entry)
                    fixture_pk += 1
                    category_counts[category_pk] += 1
        print('도서 데이터 조회 - 매핑 - 추출 완료')
        extracted_json_file = os.path.join(settings.BASE_DIR / 'data' / 'extracted_books.json')
        # extracted_books를 JSON으로 저장
        with open(extracted_json_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_books, f, ensure_ascii=False, indent=4)

        # 데이터 전처리        
        print('도서 데이터 전처리 작업 실행')
        with open(extracted_json_file, 'r', encoding="utf-8") as f:
            books = json.load(f)
        
        # 도서 순회하면서 전처리 진행
        for book in books:
            fields = book.get('fields', {})
            # 1. description 수정
            
            
            def clean_field(field):
                """
                도서 설명 HTML 엔티티 디코딩 및 태그 제거
                """
                if not field:
                    return ""
                
                # 1. HTML 엔티티 디코딩
                text = html.unescape(field)
                
                # 2. HTML 태그 제거
                text = re.sub(r'<[^>]+>', '', text)
                
                # 3. 연속 공백 정리
                text = re.sub(r'\s+', ' ', text)
                
                # 4. 앞뒤 공백 제거
                return text.strip()

            # description 값 저장
            if 'description' in fields:
                fields['description'] = clean_field(fields['description'])

            # 2. author 수정

            # author 값 저장
            if 'author' in fields:
                original_author = fields['author']
                # '(' 이전까지의 텍스트를 추출 (괄호가 ㅇ벗으면 원본 그대로 사용)
                match = re.search(r'^(.*?)\(', original_author)
                if match:
                    processed_author = match.group(1).strip()
                else:
                    processed_author = original_author
                # 수정한 description 값 fields에 재할당
                fields["author"] = processed_author

                # 추가 필드 정리
                fields['author'] = clean_field(fields['author'])

            # 3. title 수정
            if 'title' in fields:
                fields['title'] = clean_field(fields['title'])

        print('도서 데이터 전처리 작업 완료')
        # extracted_books를 JSON으로 저장
        with open(extracted_json_file, 'w', encoding='utf-8') as f:
            json.dump(books, f, ensure_ascii=False, indent=4)