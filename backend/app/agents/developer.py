from app.services.llm import get_llm
from app.tools.file_tools import write_file, clean_code


SYSTEM_PROMPT = """
You are a senior Next.js engineer.

Create a SMALL working prototype.

Rules:

1. Generate ONLY app/page.tsx.
2. Use a single file.
3. No imports from custom components.
4. No multiple pages.
5. No routing.
6. No external libraries.
7. Use React hooks if needed.
8. Maximum 200 lines.
9. Must compile in Next.js App Router.
10. Return ONLY TSX code.
11. If React hooks are used, include:
"use client"
at the top of the file.
"""


def developer_agent(project_id: str, plan: dict):
    client = get_llm()

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0.4,
        max_tokens=4000,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
    "role": "user",
    "content": f"""
Build a small single-page prototype.

Project Name:
{plan["project_name"]}

Project Type:
{plan["project_type"]}

Theme:
{plan["theme"]}

Sections:
{plan["sections"]}

Requirements:
- Everything must be inside one page.tsx file
- Keep implementation simple
- Keep under 200 lines
- Must compile in Next.js App Router
"""
}
        ]
    )

    page_content = response.choices[0].message.content
    page_content = clean_code(page_content)

    layout_content = """
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
"""
    if len(page_content) < 300:
        raise Exception(
            "Generated code suspiciously short"
        )

    if "export default" not in page_content:
        raise Exception(
            "Missing export default"
        )


    print(f"\n\ndeveloper_agent:-------------------")
    print("Generated Length:-", len(page_content))
    print(f"Last 200 chars:---\n{page_content[-200:]}")

    write_file(project_id, "app/page.tsx", page_content)
    write_file(project_id, "app/layout.tsx", layout_content)

    return {
        "status": "generated"
    }

