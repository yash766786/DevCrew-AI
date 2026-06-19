# app/agents/satisfaction_agent.py
from app.services.llm import get_llm

SYSTEM_PROMPT = """
The user is satisfied with the generated website.

Respond briefly, professionally and positively.

Keep response under 2 sentences.
"""

def satisfaction_agent(message: str):
    client = get_llm()

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0.5,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": message
            }
        ]
    )

    content = response.choices[0].message.content

    print(
        f"\n\nsatisfaction_agent:-------------------\n{content}"
    )

    return content