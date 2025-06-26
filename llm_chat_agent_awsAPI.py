import asyncio
import re
from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain.tools import Tool
#from main_gbp import get_account_cashblks, get_account_details, list_accounts
from main_gbp import mcp  # This is your FastMCP instance
from mcptolangchain import convert_mcp_tools_to_langchain_tools

tools = convert_mcp_tools_to_langchain_tools()

for tool in tools:
    print(f"Tool loaded: {tool.name}")
# -------------------------
# Regex Utility
# -------------------------
def extract_account_number(text: str) -> str:
    match = re.search(r"\b\d{10,18}\b", text)
    if match:
        return match.group(0)
    raise ValueError("No valid account number found in the input.")

# -------------------------
# MCP -> LangChain Tools
# -------------------------
# tools = [
#     Tool(
#         name="GetAccountCashBlocks",
#         func=lambda input_text: asyncio.run(get_account_cashblks(extract_account_number(input_text))),
#         description="Fetch cash blocks for a given account number."
#     ),
#     Tool(
#         name="GetAccountDetails",
#         func=lambda input_text: asyncio.run(get_account_details(extract_account_number(input_text))),
#         description="Fetch balance and account details for a given account number."
#     ),
#     Tool(
#         name="ListAccounts",
#         func=lambda: list_accounts(),
#         description="List all accounts in the local database."
#     )
# ]

# -------------------------
# Ollama LLM
# -------------------------
llm = Ollama(model="llama3")

# -------------------------
# Correct ReAct Prompt
# -------------------------
prompt_template = PromptTemplate.from_template("""
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original question

Begin!

Question: {input}
{agent_scratchpad}
""")

# -------------------------
# Agent & Executor
# -------------------------
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt_template)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,handle_parsing_errors=True)

# -------------------------
# CLI Loop
# -------------------------
def main():
    print("Ask your banking assistant (type 'exit' to quit)")
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ("exit", "quit"):
            break
        try:
            result = agent_executor.invoke({"input": user_input})
            print("\nAgent:\n", result["output"])
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
