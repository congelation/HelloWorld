# %% [第1部分] 导入和配置

# 从typing模块导入TypedDict和Literal，用于类型提示
# TypedDict用于创建具有特定键和类型的字典
# Literal用于限制变量只能是几个特定的值之一
from typing import TypedDict, Literal
# 导入ChatOpenAI类，用于与OpenAI兼容的API进行交互
from langchain_openai import ChatOpenAI
# 导入消息类型，用于构建对话
from langchain_core.messages import HumanMessage, SystemMessage
# 导入StateGraph和常量，用于构建状态图工作流
from langgraph.graph import StateGraph, START, END

# 创建ChatOpenAI实例，配置为使用豆包大模型API
llm = ChatOpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",  # API基础URL
    api_key="12a8708c-48cf-4825-9e14-4524d48d24e9",      # API密钥
    model="doubao-1-5-lite-32k-250115",                   # 使用的模型名称
    temperature=0.7,                                      # 控制输出的随机性，0-1之间，越高越随机
)

# %% [第2部分] 定义逻辑 (State 和 Nodes)
# 定义State类，继承自TypedDict，用于在工作流中传递状态
class State(TypedDict):
    messages: list    # 存储对话消息列表
    next_step: str    # 存储下一步要执行的节点名称

# 定义路由节点函数，用于判断用户输入的类型
def router_node(state: State):
    # 获取最新一条消息的内容
    last_msg = state["messages"][-1].content
    print(f"--- 正在分析用户意图: {last_msg} ---")
    
    # 构建分类提示词，让LLM判断是技术问题还是闲聊
    classifier_prompt = f"请判断这句话是'技术问题'还是'闲聊'。只回答 'tech' 或 'chat'。句子：{last_msg}"
    # 调用LLM进行分类，并获取结果
    category = llm.invoke(classifier_prompt).content.strip().lower()
    
    # 根据分类结果返回下一步的状态
    if "tech" in category:
        return {"next_step": "tech"}
    else:
        return {"next_step": "chat"}

# 定义技术专家节点函数，处理技术相关的问题
def tech_expert_node(state: State):
    print("--- 进入技术专家节点 ---")
    # 添加系统消息，定义LLM为技术专家角色，并调用LLM生成回复
    return {"messages": [llm.invoke([SystemMessage(content="你是技术专家")] + state["messages"])]}

# 定义闲聊节点函数，处理日常对话
def chat_node(state: State):
    print("--- 进入闲聊节点 ---")
    # 添加系统消息，定义LLM为热情客服角色，并调用LLM生成回复
    return {"messages": [llm.invoke([SystemMessage(content="你是热情客服")] + state["messages"])]}

# 定义决策函数，根据状态决定下一个要执行的节点
def decide_next_node(state: State) -> Literal["tech_expert", "general_chat"]:
    # 检查next_step字段，决定路由到哪个节点
    if state["next_step"] == "tech":
        return "tech_expert"
    else:
        return "general_chat"

# %% [第3部分] 组装图和编译
# 创建StateGraph实例，传入State类作为状态类型
workflow = StateGraph(State)
# 向图中添加节点，每个节点对应一个处理函数
workflow.add_node("router", router_node)        # 添加路由节点
workflow.add_node("tech_expert", tech_expert_node)  # 添加技术专家节点
workflow.add_node("general_chat", chat_node)     # 添加闲聊节点

# 添加从START节点到router节点的边，表示工作流从router开始
workflow.add_edge(START, "router")
# 添加条件边，根据decide_next_node函数的返回值决定下一个节点
workflow.add_conditional_edges(
    "router",           # 源节点
    decide_next_node,   # 决策函数
    {"tech_expert": "tech_expert", "general_chat": "general_chat"}  # 节点映射
)
# 添加从tech_expert节点到END节点的边，表示技术专家处理完成后结束
workflow.add_edge("tech_expert", END)
# 添加从general_chat节点到END节点的边，表示闲聊处理完成后结束
workflow.add_edge("general_chat", END)

# 编译工作流，生成可执行的应用
app = workflow.compile()
print("✅ 图编译完成")

# %% [第4部分] 运行测试
# 使用if __name__ == "__main__":确保只有直接运行此脚本时才执行测试代码
if __name__ == "__main__":
    # 使用 if __name__ == "__main__": 是好习惯，防止被别的文件导入时自动运行
    print("\n--- 测试开始 ---")
    # 调用应用的invoke方法，传入初始状态，包含一个关于Python GIL的技术问题
    result = app.invoke({"messages": [HumanMessage(content="今天天气怎么样？")]})
    
    # 必须用 print 才能看到结果
    # 从结果中获取最后一条消息的内容，即AI的回复
    print(f"\n最终回复: {result['messages'][-1].content}")
# %%
    