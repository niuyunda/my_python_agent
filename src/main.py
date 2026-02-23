import os
import sys

# 将 src 添加到模块路径以便直接运行
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent import Agent
# 为了让 registry 注册工具，虽然不在 main 里直接调，但也需要 import 初始化
import src.sandbox_tools 

def main():
    print("="*60)
    print(" 欢迎来到极简 AI Agent 终端 (参考 pi-mono 设计) ")
    print(" 核心: 无 Controller、无 Repository，纯粹的 Tool Calling")
    print("="*60)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.environ.get("OPENAI_API_KEY"):
        print("[警告] 没有检测到 OPENAI_API_KEY 环境变量。")
        print("       Agent 将在 Mock 模式下运行（无法真正使用工具）。")
        print("       请随时按 Ctrl+C 退出。")
    
    # 实例化我们的极简 Agent
    agent = Agent(system_prompt="""
        你是一个拥有物理文件操作和计算能力的极简终端 Agent。
        你会尽力使用你拥有的 tools 来分步解决用户的难题。
        如果任务完成，使用中文礼貌地汇报你的结果。
    """)
    
    while True:
        try:
            user_input = input("\n[You] > ")
            if not user_input.strip():
                continue
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
                
            final_answer = agent.run(user_input)
            print(f"\n[Agent 结论]:\n{final_answer}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\n[System Error]: {str(e)}")

if __name__ == "__main__":
    main()
