# %%
import os
import getpass
from typing import TypedDict, Annotated, List, Literal

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# 定义工具
@tool
def get_weather(city: str) -> str:
    """查询天气"""
    return f"{city} 的天气是晴天，25度。"

@tool
def multiply(a: int, b: int) -> int:
    """计算乘法"""
    return a * b

tools = [get_weather, multiply]

# 初始化模型并绑定工具
llm = ChatOpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="12a8708c-48cf-4825-9e14-4524d48d24e9", 
    model="doubao-1-5-lite-32k-250115",
    temperature=0.1, # 用工具时温度低一点更准
)
llm_with_tools = llm.bind_tools(tools)

# ============================
# 2. 定义图逻辑 (修复点在这里)
# ============================

class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

def chatbot_node(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# 关键修复：必须有这个判断函数
def should_continue(state: State) -> Literal["tools", END]:
    messages = state["messages"]
    last_message = messages[-1]
    
    # 如果模型想调用工具，就去 'tools' 节点
    if last_message.tool_calls:
        return "tools"
    
    # 否则（只是普通说话），就结束，去 END
    return END

# ============================
# 3. 构建图
# ============================
workflow = StateGraph(State)

# 添加节点
workflow.add_node("chatbot", chatbot_node)
workflow.add_node("tools", ToolNode(tools))

# 添加边
workflow.add_edge(START, "chatbot")

# 添加条件边：这决定了是继续循环还是停止
workflow.add_conditional_edges(
    "chatbot",
    should_continue, # 使用上面的判断函数
    ["tools", END]   # 可能的去向
)

# 工具跑完后，必须回到 chatbot 让他根据工具结果继续回答
workflow.add_edge("tools", "chatbot")

# 加入记忆
memory = MemorySaver()

# 编译
app = workflow.compile(checkpointer=memory)
print("✅ 带记忆的 Agent 构建完成")

# ============================
# 4. 运行测试
# ============================
if __name__ == "__main__":
    # 配置线程 ID (这就是记忆的钥匙)
    config = {"configurable": {"thread_id": "user_001"}}

    print("\n--- 第一轮对话 ---")
    # 这句只是打招呼，模型不应该调用工具，should_continue 会返回 END，从而避免死循环
    input1 = {"messages": [HumanMessage(content="我叫小明，是一个Python程序员。")]}
    res1 = app.invoke(input1, config=config)
    print(f"AI: {res1['messages'][-1].content}")
    
    print("\n--- 第二轮对话 ---")
    # 测试记忆能力
    input2 = {"messages": [HumanMessage(content="你还记得我叫什么吗？另外帮我算一下 5 乘以 8 是多少")]}
    res2 = app.invoke(input2, config=config)
    print(f"AI: {res2['messages'][-1].content}")
# %%
