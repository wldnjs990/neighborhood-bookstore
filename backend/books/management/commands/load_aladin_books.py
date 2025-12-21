from django.core.management.base import BaseCommand
# 프로젝트 루트 경로 출력용 settings파일
from bookmarket import settings
from decouple import config
import requests


class Command(BaseCommand):
    """
    django management commend 기능 사용
    class명은 반드시 Command로 만들어줘야 함
    django 시스템이 자동으로 Command 클래스명이 있는 코드를 찾고 실행시켜주기 때문
    """
    help = '알라딘 도서 API 받아서 json으로 저장하는 커멘드'

    def handle(self, *args, **options):

        aladin_api_key = config('ALADIN_API_KEY')
        f'?ttbkey={aladin_api_key}&QueryType=ItemNewAll&MaxResults=10&start=1&SearchTarget=Book&output=xml&Version=20131101'

        response = requests.get(f'http://www.aladin.co.kr/ttb/api/ItemList.aspx')

