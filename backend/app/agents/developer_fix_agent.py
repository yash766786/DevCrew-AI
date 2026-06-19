from app.services.llm import get_llm
from app.tools.file_tools import write_file
from app.tools.file_tools import clean_code

SYSTEM_PROMPT = """
You are fixing a Next.js page.

Rules:
1. Preserve all original functionality.
2. Preserve all UI sections.
3. Do not remove features.
4. Do not return placeholder content.
5. Do not return "Hello World".
6. Only make the minimal changes required to pass the build.
7. Return the full corrected TSX file.
"""

def developer_fix_agent(code: str, fix_instructions: str):
    client = get_llm()

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
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
{code}

FIX INSTRUCTIONS:
{fix_instructions}
"""
            }
        ]
    )

    content = response.choices[0].message.content
    content = clean_code(content)


    print(f"\n\ndeveloper_fix_agent:-------------------")
    print("Generated Fixed Length:-", len(content))
    print(f"Last 200 chars:---\n{content[-200:]}")

    return content

