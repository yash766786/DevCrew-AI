import json
from app.services.llm import get_llm

SYSTEM_PROMPT = """
You analyze human feedback on a project plan.
Possible actions:
1. approve
2. modify

Return ONLY JSON.
Schema:

{
  "action": "approve"
}
or
{
  "action": "modify"
}
"""


def intent_agent(message: str):
    client = get_llm()

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
        response_format={"type": "json_object"},
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

    print(f"scope agent:---------------------\n{response.choices[0].message}")

    return json.loads(
        response.choices[0].message.content
    )