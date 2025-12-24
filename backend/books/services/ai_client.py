# books/services/ai_client.py

import json
import openai
from django.conf import settings

class LLMClient:
    """
    AI 모델 호출 전용 클라이언트
    (현재 OpenAI 미사용 → 서버 실행용 더미)
    """

    def recommend_books(self, prompt: str) -> dict:
        # 서버 실행 및 API 테스트용 더미 응답
        return {
            "recommendations": [
                {
                    "book_id": 1,
                    "title": "더미 추천 도서 1",
                    "reason": "OpenAI 키 없이 추천 API 흐름을 테스트하기 위한 더미 데이터입니다."
                },
                {
                    "book_id": 2,
                    "title": "더미 추천 도서 2",
                    "reason": "카테고리 및 MBTI 필터가 정상적으로 동작했습니다."
                },
                {
                    "book_id": 3,
                    "title": "더미 추천 도서 3",
                    "reason": "추천 후보 50권 생성 로직이 정상입니다."
                }
            ]
        }


# 전역 인스턴스
llm_client = LLMClient()

# class LLMClient:
#     """
#     AI 모델 호출 전용 클라이언트
#     - 프롬프트 입력 → AI 응답(JSON) 반환
#     """

#     def __init__(self):
#         openai.api_key = settings.OPENAI_API_KEY

#     def recommend_books(self, prompt: str) -> dict:
#         """
#         :param prompt: build_recommend_prompt()로 생성된 최종 프롬프트
#         :return: AI 응답 (dict)
#         """
#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "You are a professional book curator.",
#                 },
#                 {
#                     "role": "user",
#                     "content": prompt,
#                 },
#             ],
#             temperature=0.7,
#         )

#         content = response.choices[0].message.content

#         try:
#             return json.loads(content)
#         except json.JSONDecodeError:
#             # JSON 파싱 실패 시 안전 처리
#             return {
#                 "error": "AI response is not valid JSON",
#                 "raw_response": content,
#             }


# # 전역 인스턴스
# llm_client = LLMClient()
