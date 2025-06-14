#!/usr/bin/env python3

import sys
import argparse
import subprocess  # 新增subprocess模块
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from openai import OpenAI

# 配置信息
MODEL_ID = " "
ARK_API_KEY = " "
ARK_BASE_URL = " "

PROMPT_SETTINGS = {
    "role": "system",
    "content": "You are a capable assistant，please response me in Chinese。" # 此处修改提示词
    }

def execute_command(command: str) -> str:
    """执行shell命令并实时流式输出结果"""
    try:
        proc = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        output = []
        while True:
            line = proc.stdout.readline()
            if not line and proc.poll() is not None:
                break
            if line:
                # 直接输出并立即刷新
                sys.stdout.write(line)
                sys.stdout.flush()
                output.append(line)
        return "".join(output)
    except Exception as e:
        error_msg = f"\nError executing command: {str(e)}"
        sys.stdout.write(error_msg + "\n")
        return error_msg


def query_llm(client, messages) -> str:
    """执行LLM查询（流式输出）"""
    try:
        stream = client.chat.completions.create(
            model=MODEL_ID, messages=messages, stream=True
        )
        response = []
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                sys.stdout.write(content)
                sys.stdout.flush()  # 确保实时刷新
                response.append(content)
        print()
        return "".join(response)
    except Exception as e:
        sys.stderr.write(f"\nError: {str(e)}\n")
        return None


def enhanced_input(prompt: str) -> str:
    """增强的输入函数（支持中文编辑/方向键）"""
    bindings = KeyBindings()

    @bindings.add("c-c")  # 保留Ctrl+C中断支持
    def _(event):
        event.app.exit(exception=KeyboardInterrupt)

    session = PromptSession(
        key_bindings=bindings, vi_mode=False, multiline=False, mouse_support=False
    )

    return session.prompt(
        message=prompt, wrap_lines=True, enable_history_search=False
    ).strip()


def interactive_mode(client, initial_input=None):
    """交互式对话模式"""
    messages = [PROMPT_SETTINGS]

    if initial_input:
        messages.append({"role": "user", "content": initial_input})
        print("Q: ", initial_input)
        print("A: ", end="", flush=True)
        assistant_response = query_llm(client, messages)
        if assistant_response:
            messages.append({"role": "assistant", "content": assistant_response})

    print("🤖:AGNET 启动！ 输入 'exit' 或'Ctrl + c' 退出")
    while True:
        try:
            user_input = enhanced_input("Q: ")

            if user_input.lower() in ["exit", "quit"]:
                break

            # 新增 clear 命令处理
            if user_input.strip().lower() == "clear":
                # 清屏操作
                sys.stdout.write("\033[2J\033[H")  # ANSI 清屏序列
                sys.stdout.flush()
                # 重置对话历史
                messages = [PROMPT_SETTINGS]
                print("对话历史已重置")
                continue

            if not user_input:
                print()
                continue

            # 处理以!开头的命令
            if user_input.startswith("!"):
                command = user_input[1:].strip()
                if not command:
                    continue

                # 将命令加入消息历史
                messages.append({"role": "user", "content": user_input})

                # 执行命令并获取输出
                print("A: ", end="", flush=True)
                cmd_output = execute_command(command)
                print()  # 确保命令输出后换行

                # 将命令输出加入消息历史
                messages.append({
                    "role": "system",
                    "content": f"命令执行结果:\n{cmd_output}",
                })
                continue

            # 正常LLM对话流程
            messages.append({"role": "user", "content": user_input})
            print("A: ", end="", flush=True)
            assistant_response = query_llm(client, messages)

            if assistant_response:
                messages.append({"role": "assistant", "content": assistant_response})
            else:
                sys.stderr.write("获取响应失败，请重试\n")
            print()

        except KeyboardInterrupt:
            print("\n再见！")
            break
        except EOFError:
            print("\n[ERROR]再见！")
            break


def single_query_mode(client, question):
    """单次查询模式（保持原有简单输入）"""
    messages = [
        PROMPT_SETTINGS,
        {"role": "user", "content": question},
    ]
    sys.stdout.write("> ")
    sys.stdout.flush()  # 确保实时刷新

    assistant_response = query_llm(client, messages)
    if not assistant_response:
        sys.exit(1)


def read_piped_input():
    """读取管道输入并添加换行符"""
    if not sys.stdin.isatty():
        return sys.stdin.read().strip() + "\n"
    return None


def main():

    client = OpenAI(api_key=ARK_API_KEY, base_url=ARK_BASE_URL)

    parser = argparse.ArgumentParser(description="AI命令行助手")
    parser.add_argument("text", nargs="*", help="输入问题（直接模式）")
    parser.add_argument("-r", "--repl", action="store_true", help="进入交互模式")
    parser.add_argument("-t", "--translate", action="store_true", help="翻译")
    parser.add_argument(
        "-P", "--print-text", action="store_true", help="打印完整的输入文本"
    )
    parser.add_argument(
        "-p", "--prompt", type=str, help="输入提示词"
    )
    args = parser.parse_args()

    in_text = None
    in_text_list = []
    piped_input = read_piped_input()

    if piped_input:
        in_text_list.append(piped_input.strip())
    if args.text:
        in_text_list.append("".join(args.text))
    if args.translate and in_text_list:
        in_text_list.append("\n请将以上文本翻译成中文\n")

    if in_text_list:
        in_text = "".join(in_text_list)
    if args.print_text and in_text:
        sys.stdout.write(in_text)

    if args.prompt:
        PROMPT_SETTINGS["content"] = args.prompt

    if in_text:
        if args.repl:
            interactive_mode(client, in_text)
        else:
            single_query_mode(client, in_text)
    else:
        interactive_mode(client)

if __name__ == "__main__":
        main()





