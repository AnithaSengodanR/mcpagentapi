import asyncio
from langchain.tools import Tool
from inspect import signature, iscoroutinefunction
from main_gbp import get_account_cashblks, get_account_details, list_accounts

def convert_mcp_tools_to_langchain_tools() -> list[Tool]:
    """
    Wraps known MCP tool functions into LangChain-compatible tools.
    """
    tool_funcs = [get_account_cashblks, get_account_details, list_accounts]
    langchain_tools = []

    for func in tool_funcs:
        tool_name = func.__name__
        description = func.__doc__ or f"Tool: {tool_name}"
        sig = signature(func)
        param_names = list(sig.parameters.keys())
        param_name = param_names[0] if param_names else None  # e.g. list_accounts()

        def make_wrapper(f, pname):
            def wrapper(input_data):
                if pname:
                    arg = input_data.get(pname) if isinstance(input_data, dict) else input_data
                    return asyncio.run(f(arg)) if iscoroutinefunction(f) else f(arg)
                else:
                    return asyncio.run(f()) if iscoroutinefunction(f) else f()
            return wrapper

        langchain_tools.append(
            Tool(
                name=tool_name,
                func=make_wrapper(func, param_name),
                description=description.strip()
            )
        )

    return langchain_tools
