import json
from app.services.llm import get_llm


SYSTEM_PROMPT = """
You are a project scope validator.

This platform supports:

- Small Next.js applications
- Single page websites
- Frontend only projects
- Local state only

This platform does NOT support:

- Databases
- Authentication
- Payments
- Backend APIs
- MERN stack
- Django
- Spring Boot
- Microservices
- Mobile Apps

Return ONLY valid JSON.

Schema:

{
    "allowed": true,
    "reason": ""
}
"""


def scope_agent(prompt: str):
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
                "content": prompt
            }
        ]
    )

    print(f"scope_agent:-------------------\n{response.choices[0].message}")

    return json.loads(
        response.choices[0].message.content
    )