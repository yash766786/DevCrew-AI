import json

from app.services.llm import get_llm
from app.models.planner import ProjectPlan

SYSTEM_PROMPT = """
You are a rapid-prototyping web architect.

Your goal is to design SMALL demo websites.

Rules:

1. Always create a SINGLE PAGE application.
2. Maximum 5 sections.
3. No authentication.
4. No database.
5. No backend APIs.
6. No multiple routes.
7. The entire website should fit inside one page.tsx file.
8. Sections MUST be strings.
9. Do NOT return objects inside sections.

Return ONLY valid JSON.

Example:

{
  "project_name": "Portfolio",
  "project_type": "portfolio",
  "theme": "modern",
  "sections": [
    "Hero",
    "About",
    "Skills",
    "Contact"
  ],
  "summary": "A modern single-page portfolio website with Hero, About, Skills and Contact sections."
}
"""


def planner_agent(user_prompt: str) -> ProjectPlan:
    client = get_llm()

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    content = response.choices[0].message.content
    print(f"\n\nplanner_agent:-------------------\n{content}")

    # Remove markdown fences if model adds them
    content = content.replace("```json", "")
    content = content.replace("```", "")
    content = content.strip()

    data = json.loads(content)

    return ProjectPlan(**data)