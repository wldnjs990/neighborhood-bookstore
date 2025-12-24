# books/services/ai_client.py
import json
import requests
from django.conf import settings


class LLMClient:
    """
    SSAFY GMS OpenAI 프록시 호출 클라이언트
    """

    ENDPOINT = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY # 👉 GMS KEY

    def recommend_books(self, prompt: str) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "developer",
                    "content": "You are a professional book curator.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.5,
        }

        response = requests.post(
            self.ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code != 200:
            return {
                "error": "GMS OpenAI API error",
                "status_code": response.status_code,
                "detail": response.text,
            }

        content = response.json()["choices"][0]["message"]["content"]

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "error": "AI response is not valid JSON",
                "raw_response": content,
            }


# 전역 인스턴스
llm_client = LLMClient()



''' 서버 실행 확인용 더미
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
'''