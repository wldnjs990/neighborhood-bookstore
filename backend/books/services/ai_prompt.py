# books/services/ai_prompt.py
def build_recommend_prompt(
    mbti_info: str,
    user_prompt: str,
    books_payload: list
    ) -> str:
    return f"""
    You are a professional book curator.

    Rules:
    - You MUST recommend books ONLY from the candidate list.
    - Choose EXACTLY 3 books.
    - Explain briefly why each book matches the user.
    - Return JSON only.

    [User Reading Preference - Book MBTI]
    {mbti_info}

    [User Request]
    {user_prompt}

    [Candidate Books]
    {books_payload}
    """