# %% [1. 配置环境]
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage

llm = ChatOpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="12a8708c-48cf-4825-9e14-4524d48d24e9", 
    model="doubao-pro-4k-240515",
    temperature=0.1, # 用工具时温度低一点更准
)

# %% [2. 定义工具]
# 使用 @tool 装饰器，AI 会自动读取函数名和 docstring（注释）
@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气。"""
    # 这里我们模拟一下，实际可以调天气API
    print(f"--- 正在调用天气工具: {city} ---")
    if "北京" in city:
        return "北京今天晴，25度，适合写代码。"
    elif "上海" in city:
        return "上海正在下雨，记得带伞。"
    else:
        return f"{city} 天气未知。"

@tool
def multiply(a: int, b: int) -> int:
    """计算两个数字的乘积。"""
    print(f"--- 正在调用乘法工具: {a} * {b} ---")
    return a * b

# 将工具放入列表
tools = [get_weather, multiply]

# 关键一步：将工具“绑定”到 LLM
# 这样 LLM 才知道它有哪些技能
llm_with_tools = llm.bind_tools(tools)

# %% [3. 构建图]
class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

def chatbot_node(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# 定义判断逻辑：如果 AI 返回了 tool_calls，就去 tools 节点，否则结束
def should_continue(state: State):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

workflow = StateGraph(State)

# 节点 1: 思考节点
workflow.add_node("chatbot", chatbot_node)
# 节点 2: 工具执行节点 (LangGraph 自带的，专门用来运行 tool)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "chatbot")

# 条件边：chatbot -> (有工具调用) -> tools -> chatbot (循环)
#             -> (无工具调用) -> END
workflow.add_conditional_edges(
    "chatbot",
    should_continue,
    ["tools", END]
)
# 工具执行完后，必须把结果传回给 AI 让他继续生成回复
workflow.add_edge("tools", "chatbot")

app = workflow.compile()
print("✅ Agent 构建完成")

# %% [4. 测试]
if __name__ == "__main__":
    print("\n--- 测试 1: 简单对话 ---")
    app.invoke({"messages": [HumanMessage(content="你好")]})

    print("\n--- 测试 2: 调用工具 ---")
    # 观察输出：你会看到它先决定调用工具，执行函数，然后再回答
    # final_state = app.invoke({"messages": [HumanMessage(content="上海今天天气怎么样？另外算一下 123 乘以 4")]})
    final_state = app.invoke({"messages": [HumanMessage(content="123 乘以 2")]})
    print(f"\n最终回复: {final_state['messages'][-1].content}")
# %%
