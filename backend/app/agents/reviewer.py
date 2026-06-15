from app.services.llm import get_llm


SYSTEM_PROMPT = """
You are a Next.js build reviewer.

Rules:
1. Preserve functionality.
2. Fix only build errors.
3. Do not simplify the application.
4. Do not replace the app with placeholder content.
5. Return concise fix instructions.
"""


def reviewer_agent(code: str, build_error: str):
    client = get_llm()

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""
CODE:

{code}


BUILD ERROR:

{build_error}
"""
            }
        ]
    )

    content = response.choices[0].message.content
    print(f"\n\nreviewer_agent:-------------------\n{content}")

    return content