# %% [导入与配置]
# 复用之前的配置...
from langgraph.checkpoint.memory import MemorySaver # <--- 新面孔
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
    model="doubao-1-5-lite-32k-250115",
    temperature=0.1, # 用工具时温度低一点更准
)
# ... (假设你已经复制了上面练习4的 llm 和 tools 定义，这里为了省篇幅省略)
# 如果你是单独跑这个文件，记得把练习4里的 imports, llm, tools, State 定义都拷过来
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


# %% [构建带记忆的图]
# 逻辑和练习4完全一样，区别在于 compile
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


memory = MemorySaver()

# 编译时传入 checkpointer
app = workflow.compile(checkpointer=memory)
print("✅ Agent 构建完成")

# %% [测试记忆功能]
if __name__ == "__main__":
    # thread_id 就像是“会话ID”或“用户ID”
    # 只要 thread_id 不变，机器人就记得你
    config = {"configurable": {"thread_id": "user_123"}}

    print("--- 第一轮对话 ---")
    input1 = {"messages": [HumanMessage(content="我叫小明，是一个Python程序员。")]}
    # 注意：必须传入 config
    app.invoke(input1, config=config) 
    
    print("\n--- 第二轮对话 (假装过了很久) ---")
    input2 = {"messages": [HumanMessage(content="你还记得我叫什么，是做什么的吗？")]}
    result = app.invoke(input2, config=config)
    
    print(f"回复: {result['messages'][-1].content}")
    
    print("\n--- 换个用户 (user_999) ---")
    # 换个 ID，它应该就不认识了
    result_new = app.invoke(
        {"messages": [HumanMessage(content="我是谁？")]}, 
        config={"configurable": {"thread_id": "user_999"}}
    )
    print(f"新用户回复: {result_new['messages'][-1].content}")
# %%
