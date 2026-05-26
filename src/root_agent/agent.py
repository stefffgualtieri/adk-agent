from google.adk.agents import Agent

from .sub_agents.text_to_sql.agent import text_to_sql

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="""
    Root agent that receives the user request and routes it to the most appropriate sub-agent. 
    In this MVP it forwards all requests to the TextToSQL sub-agent.
    """,
    instruction="""
    You are the Root Agent of AskNetwork. Your job is:
    1) Understand the user intent.
    2) If the request is about network data, devices, IPs, sites, inventory, or any query over the dataset, delegate to the "TextToSQL" sub-agent.
    3) If the request is unclear, ask ONE clarifying question before delegating.
    4) Never fabricate data: if information is missing, ask for it.
    5) Keep the final answer short and clear.

    For this MVP: when in doubt, delegate to "TextToSQL".
    """,
    sub_agents=[text_to_sql],
)