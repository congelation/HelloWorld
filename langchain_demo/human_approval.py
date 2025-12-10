# %% [配置]
import os
import getpass
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict

llm = ChatOpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="12a8708c-48cf-4825-9e14-4524d48d24e9", 
    model="doubao-1-5-lite-32k-250115",
)

# %% [图定义]
class State(TypedDict):
    input: str
    action: str

def planner_node(state: State):
    print("🤖 AI: 正在分析用户请求...")
    return {"action": "转账 100万"}

def action_node(state: State):
    # 这个节点是敏感操作
    action = state["action"]
    print(f"💸 系统: 正在执行操作 -> {action}")
    return {"action": "已完成"}

workflow = StateGraph(State)
workflow.add_node("planner", planner_node)
workflow.add_node("execute_money", action_node)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "execute_money")
workflow.add_edge("execute_money", END)

memory = MemorySaver()

# 关键点：interrupt_before
# 意思是：在进入 "execute_money" 节点之前，打断（暂停）程序
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["execute_money"]
)

# %% [运行与批准]
if __name__ == "__main__":
    thread_config = {"configurable": {"thread_id": "tx_001"}}
    
    print("--- 1. 启动任务 ---")
    # 这次运行会停在 planner 之后，execute_money 之前
    app.invoke({"input": "我要转账"}, config=thread_config)
    
    print("\n⚠️  程序已暂停！等待人类审批...")
    print("当前状态快照:", app.get_state(thread_config).next)
    
    user_approval = input("是否批准转账？(y/n): ")
    
    if user_approval.lower() == "y":
        print("\n--- 2. 用户批准，继续执行 ---")
        # 传入 None 表示“什么都不改，继续往下跑”
        # stream(None) 会从断点处恢复
        for event in app.stream(None, config=thread_config):
            print(event)
    else:
        print("\n--- 2. 用户拒绝，操作取消 ---")