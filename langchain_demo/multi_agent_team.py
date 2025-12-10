# %% [配置]
import os
import getpass
from typing import TypedDict, Annotated, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# API 配置
llm = ChatOpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="12a8708c-48cf-4825-9e14-4524d48d24e9", 
    model="doubao-1-5-lite-32k-250115",
    temperature=0.7,
)

# %% [定义状态]
class State(TypedDict):
    # 消息历史，所有 Agent 共享
    messages: Annotated[List[BaseMessage], add_messages]
    # 下一步轮到谁
    next_speaker: str

# %% [定义角色节点]

def researcher_node(state: State):
    """研究员：负责补充数据（这里我们用模拟数据）"""
    print("--- 🕵️ 研究员正在工作 ---")
    
    # 获取用户的需求
    last_msg = state["messages"][-1].content
    
    # 这里通常会调用搜索工具，我们简化一下，直接模拟“查到了数据”
    # 假设用户问的是 Python
    mock_data = f"【研究员报告】：关于 '{last_msg}' 的最新数据：1. 版本是3.12; 2. 它是动态类型语言; 3. 广泛用于AI。"
    
    # 只有研究员生成的消息
    return {
        "messages": [AIMessage(content=mock_data, name="Researcher")],
        "next_speaker": "writer" # 比如这里强行规定，研究完就交给作家
    }

def writer_node(state: State):
    """作家：负责根据上下文写文章"""
    print("--- ✍️ 作家正在写作 ---")
    messages = state["messages"]
    
    # 给 LLM 一个特定的人设
    prompt = [SystemMessage(content="你是一个专业的科技博主。请根据'Researcher'提供的数据，写一篇短小精悍的推文。")] + messages
    response = llm.invoke(prompt)
    
    return {
        "messages": [response],
        "next_speaker": "finish"
    }

# %% [构建图]
workflow = StateGraph(State)

workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)

workflow.add_edge(START, "researcher")

# 简单的逻辑：Researcher -> Writer -> END
# 在更复杂的系统中，这里可以用 conditional_edge 让它们互相以此对话多次
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", END)

app = workflow.compile()

# %% [运行]
if __name__ == "__main__":
    print("\n--- 启动虚拟团队 ---")
    input_data = {"messages": [HumanMessage(content="Python 编程语言")]}
    
    for event in app.stream(input_data):
        for key, value in event.items():
            print(f"\n[{key} 节点完成]")
            print(f"内容: {value['messages'][-1].content[:50]}...") # 只打印前50个字
            
    print("\n--- 最终结果 ---")
    # 获取最后一条消息（Writer 写的）
    # 注意：因为我们用了 add_messages，所以最后一条就是 writer 的
    final_output = app.invoke(input_data)["messages"][-1].content
    print(final_output)