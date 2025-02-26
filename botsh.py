#!/usr/bin/env python3
import sys
import argparse
from prompt_toolkit import PromptSession  # 新增输入处理库
from prompt_toolkit.key_binding import KeyBindings
from openai import OpenAI

# 配置信息
MODEL_ID = ""
ARK_API_KEY = ""
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

def query_llm(client, messages) -> str:
    """执行LLM查询（流式输出）"""
    try:
        stream = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            stream=True
        )
        response = []
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                response.append(content)
        print()
        return ''.join(response)
    except Exception as e:
        sys.stderr.write(f"\nError: {str(e)}\n")
        return None

def enhanced_input(prompt: str) -> str:
    """增强的输入函数（支持中文编辑/方向键）"""
    bindings = KeyBindings()
    
    @bindings.add('c-c')  # 保留Ctrl+C中断支持
    def _(event):
        event.app.exit(exception=KeyboardInterrupt)
    
    session = PromptSession(
        key_bindings=bindings,
        vi_mode=False,
        multiline=False,
        mouse_support=False
    )
    
    return session.prompt(
        message=prompt,
        wrap_lines=True,
        enable_history_search=False
    ).strip()

def interactive_mode(client, initial_input=None):
    """交互式对话模式"""
    messages = [
        {"role": "system", "content": "你是一个能干的助手。"}
    ]
    
    if initial_input:
        messages.append({"role": "user", "content": initial_input})
        print("Q\n>", initial_input)
        print("A\n> ", end="", flush=True)
        assistant_response = query_llm(client, messages)
        if assistant_response:
            messages.append({"role": "assistant", "content": assistant_response})
    
    print("\n进入对话模式（输入 exit 退出）")
    while True:
        try:
            # 使用增强输入函数
            user_input = enhanced_input("\nQ\n> ")
            
            if user_input.lower() in ['exit', 'quit']:
                break
                
            if not user_input:
                continue
                
            messages.append({"role": "user", "content": user_input})
            print("A\n> ", end="", flush=True)
            assistant_response = query_llm(client, messages)
            
            if assistant_response:
                messages.append({"role": "assistant", "content": assistant_response})
            else:
                sys.stderr.write("获取响应失败，请重试\n")
                
        except KeyboardInterrupt:
            print("\n会话已终止")
            break
        except EOFError:
            print("\n再见！")
            break

def single_query_mode(client, question):
    """单次查询模式（保持原有简单输入）"""
    messages = [
        {"role": "system", "content": "你是一个能干的助手。"},
        {"role": "user", "content": question}
    ]
    print("> ", end="", flush=True)
    assistant_response = query_llm(client, messages)
    if not assistant_response:
        sys.exit(1)

def read_piped_input():
    """读取管道输入并添加换行符"""
    if not sys.stdin.isatty():
        return sys.stdin.read().strip() + '\n'
    return None

def main():
    client = OpenAI(api_key=ARK_API_KEY, base_url=ARK_BASE_URL)
    
    parser = argparse.ArgumentParser(description='AI命令行助手')
    parser.add_argument('text', nargs='*', help='输入问题（直接模式）')
    parser.add_argument('-r', '--repl', action='store_true', help='进入交互模式')
    args = parser.parse_args()

    piped_input = read_piped_input()
    
    if piped_input:
        if args.repl:
            interactive_mode(client, piped_input.strip())
        else:
            single_query_mode(client, piped_input.strip())
    elif args.text:
        single_query_mode(client, ' '.join(args.text))
    elif args.repl:
        interactive_mode(client)
    else:
        interactive_mode(client)

if __name__ == '__main__':
    main()

