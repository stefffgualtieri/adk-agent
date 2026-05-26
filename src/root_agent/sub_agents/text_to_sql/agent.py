from google.adk.agents import Agent

from tools.txt_to_sql import text_to_sql

text_to_sql = Agent(
    name="text_to_sql",
    model="gemini-2.5-flash",
    description="",
    instruction="""
    """,
    tools=[text_to_sql],
)