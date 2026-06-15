from app.services.llm import get_llm
from app.tools.file_tools import clean_code

SYSTEM_PROMPT = """
You are a senior Next.js engineer.

You will receive:

1. Existing page.tsx code
2. User modification request

Your task:

- Modify the existing code
- Preserve existing functionality
- Apply requested changes
- Keep everything in a single page.tsx file
- Return ONLY valid TSX code
- No markdown
- No explanations
"""

def editor_agent(current_code: str, user_request: str):
    client = get_llm()

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0.2,
        max_tokens=4000,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""
CURRENT CODE:
{current_code}


MODIFICATION REQUEST:
{user_request}
"""
            }
        ]
    )

    content = response.choices[0].message.content
    print(f"\n\neditor_agent:-------------------\n{content}")

    return clean_code(content)


