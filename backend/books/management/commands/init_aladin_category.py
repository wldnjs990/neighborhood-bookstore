from django.core.management.base import BaseCommand
# 프로젝트 루트 경로 출력용 settings파일
from bookmarket import settings
# 알라딘 API로 받아오는 책 데이터 저장하기 위해 모델 가져옴
from books.models import Category, Book
# 1Depth 카테고리들 매핑용 대분류 dict
from books.constants import CATEGORY_MAPPING
import pandas as pd
import os
import json

class Command(BaseCommand):
    """
    django management commend 기능 사용
    class명은 반드시 Command로 만들어줘야 함
    django 시스템이 자동으로 Command 클래스명이 있는 코드를 찾고 실행시켜주기 때문
    """

    help = '알라딘 Excel 파일에서 도서 카테고리 커스텀해서 저장하는 커멘드'

    # handle이란 메서드가 BaseCommand에 있나봄
    # 자동으로 emmet이 생성되네
    def handle(self, *args, **options):
        """
        실제 명령어 로직을 작성하는 메서드
        python manage.py load_aladin 실행 시 이 메서드가 호출됨
        """
        
        # 프로젝트 루트경로(settings.BASE_DIR)을 활용해 데이터에 접근
        excel_file = os.path.join(settings.BASE_DIR / 'data' / 'aladin_Category_CID_20210927.xls')
        
        # Excel 읽기
        # excel_file 경로에 있는 엑셀파일을 읽음
        # 필터용 header는 2칸 아래에 있는 3번째 row로 지정 
        df = pd.read_excel(excel_file, header=2)
        
        # 터미널에 진행 상황 출력 (선택사항)
        self.stdout.write(f'총 {len(df)}개의 카테고리를 로드합니다...')
        
        # 엑셀파일 dict로 저장-----------------------------------------------------------------
        categort_dict = {}
        # 엑셀파일 저장한 df(data frame)을 엑셀 row 기준으로 순회
        for _, row in df.iterrows():
            # 1번째 카테고리, cid 저장
            category = row['1Depth']
            cid = row['CID']
            
            # 카테고리중에 빈 값으로 들어가있는 카테고리 있으면 그건 제외하기
            if pd.isna(category):
                continue

            # 현재 category가 categort_dict에 이미 key로 저장된 값이라면
            if category in categort_dict:
                # 해당 카테고리에 cid 추가해주기
                categort_dict[category].append(cid)
            # 현재 category가 아직 categort_dict에 key로 저장되어있지 않다면
            else:
                # 해당 카테고리를 key값으로 cid 배열 새로 생성
                categort_dict[category] = [cid]
        
        # 1Depth를 기준으로 CID 그룹핑-----------------------------------------------------------------
        new_groups = []
        for idx, (category, cid_list) in enumerate(categort_dict.items(), start=1):
            new_groups.append({
                'pk': idx,
                'name': category,
                'cid_list' : cid_list
            })
        
        # new_groups 8개 대분류 나눠서 그룹핑-----------------------------------------------------------------
        new_group_mapping = {}
        # CATEGORY_MAPPING 참조해서 초기값 동적으로 생성
        for idx, (category, names) in enumerate(CATEGORY_MAPPING.items(), start=1):
            new_group_mapping[idx] = {
                "name" : category,
                "old_pks": []
            }
        # 카테고리 그룹핑
        for idx, group in enumerate(new_groups, start=1):
            pk = group['pk']
            name = group['name']
            cid_list = group['cid_list']

            for idx, (category, names) in enumerate(CATEGORY_MAPPING.items(), start=1):
                # 현재 대분류에 속한 카테고리일시
                if name in names:
                    # old_pks에 카테고리 pk값만 저장
                    new_group_mapping[idx]['old_pks'].append(pk)
                    break

        # 대분류로 나눈 데이터(new_group_mapping) 가지고 
        final_groups = []
        for new_pk, mapping_data in new_group_mapping.items():
            # 최종 저장할 cid값
            merged_cid_list = []
            # 현재 대분류의 old_pks들 순회
            for old_pk in mapping_data['old_pks']:
                # 66개짜리 1Depth 카테고리 배열(new_groups) 순회
                for group in new_groups:
                    # 해당 카테고리의 pk가 특정 대분류 pk에 속해있다면
                    if group['pk'] == old_pk:
                        # 해당하는 cid값 전부 담아주기
                        # extend = 배열의 데이터들을 집어넣어줌(*이거 쓴거랑 똑같음)
                        merged_cid_list.extend(group['cid_list'])
                        break
            # 대분류 번호(pk), 대분류 카테고리 이름(name), cid값들 담아주면 끝
            final_groups.append({
                "pk" : new_pk,
                "name" : mapping_data["name"],
                "cid" : merged_cid_list
            })

        # 완성된 카테고리 분류표 저장할 json 파일 경로
        json_file = os.path.join(settings.BASE_DIR / 'data' / 'categories.json')
        
        with open(json_file, 'w', encoding='utf-8') as f:
            # ensure_ascii = 한글깨짐 방지
            # ident = 아마도 코드 공백..?
            json.dump(final_groups, f, ensure_ascii=False, indent=4)

        # 성공 메시지 출력 (초록색)
        self.stdout.write(self.style.SUCCESS('loaddata 파일 생성 완료!'))
        
