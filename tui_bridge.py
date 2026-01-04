import sys
import json
import io
import os
from agent import AliceAgent

# 强制切换到脚本所在目录（根目录）
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 强制 stdout 使用 utf-8 编码，并禁用 buffering 以便实时传输 JSON
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

def main():
    try:
        alice = AliceAgent()
    except Exception as e:
        print(json.dumps({"type": "error", "content": f"Initialization failed: {str(e)}"}), flush=True)
        return
    
    # 向 Rust 发送就绪信号
    print(json.dumps({"type": "status", "content": "ready"}), flush=True)

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            user_input = line.strip()
            if not user_input:
                continue
            
            alice.messages.append({"role": "user", "content": user_input})
            
            while True:
                extra_body = {"enable_thinking": True}
                response = alice.client.chat.completions.create(
                    model=alice.model_name,
                    messages=alice.messages,
                    stream=True,
                    extra_body=extra_body
                )

                full_content = ""
                thinking_content = ""
                
                # 发送开始思考信号
                print(json.dumps({"type": "status", "content": "thinking"}), flush=True)

                for chunk in response:
                    if chunk.choices:
                        delta = chunk.choices[0].delta
                        t_chunk = getattr(delta, 'reasoning_content', '')
                        c_chunk = getattr(delta, 'content', '')
                        
                        if t_chunk:
                            thinking_content += t_chunk
                            print(json.dumps({"type": "thinking", "content": t_chunk}), flush=True)
                        elif c_chunk:
                            full_content += c_chunk
                            print(json.dumps({"type": "content", "content": c_chunk}), flush=True)

                # 检查工具调用
                import re
                python_codes = re.findall(r'```python\s*\n?(.*?)\s*```', full_content, re.DOTALL)
                bash_commands = re.findall(r'```bash\s*\n?(.*?)\s*```', full_content, re.DOTALL)
                
                if not python_codes and not bash_commands:
                    alice.messages.append({"role": "assistant", "content": full_content})
                    print(json.dumps({"type": "status", "content": "done"}), flush=True)
                    break
                
                # 有工具调用
                alice.messages.append({"role": "assistant", "content": full_content})
                results = []
                
                print(json.dumps({"type": "status", "content": "executing_tool"}), flush=True)

                # 捕获工具执行过程中的 print，防止污染 stdout
                # 虽然 execute_command 内部通常使用 subprocess 捕获了输出，但安全起见
                for code in python_codes:
                    res = alice.execute_command(code.strip(), is_python_code=True)
                    results.append(f"Python 代码执行结果:\n{res}")
                
                for cmd in bash_commands:
                    res = alice.execute_command(cmd.strip(), is_python_code=False)
                    results.append(f"Shell 命令 `{cmd.strip()}` 的结果:\n{res}")
                
                feedback = "\n\n".join(results)
                alice.messages.append({"role": "user", "content": f"容器执行反馈：\n{feedback}"})
                alice._refresh_system_message()
                
        except EOFError:
            break
        except Exception as e:
            # 捕获所有运行时错误并通过 JSON 传回，而不是直接打印
            print(json.dumps({"type": "error", "content": str(e)}), flush=True)
            break

if __name__ == "__main__":
    main()
