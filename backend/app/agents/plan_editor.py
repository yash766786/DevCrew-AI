import json

from app.services.llm import get_llm
from app.models.planner import ProjectPlan

SYSTEM_PROMPT = """
You modify an existing project plan.
Keep the project small.
Preserve existing structure.
Apply the user's feedback.
Return ONLY valid JSON.
output: 
{
  "project_name": "...",
  "project_type": "...",
  "theme": "...",
  "sections": [...],
  "summary": "..."
}
"""

def plan_editor_agent(current_plan: dict, feedback: str) -> ProjectPlan:
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
            "content": f"""
CURRENT PLAN:
{current_plan}

USER FEEDBACK:
{feedback}
"""
}
        ]
    )

    content = response.choices[0].message.content
    print(f"planner_editor_agent:-------------------\n{response.choices[0].message}")

    # Remove markdown fences if model adds them
    content = content.replace("```json", "")
    content = content.replace("```", "")
    content = content.strip()

    data = json.loads(content)

    return ProjectPlan(**data)