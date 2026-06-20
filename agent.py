import os
import json
import openai
from dotenv import load_dotenv
from tools.pdf_reader import extract_pdf_text
from tools.email_sender import send_email

load_dotenv()
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 工具定义（符合OpenAI function calling格式）
tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_pdf_text",
            "description": "读取本地PDF文件并提取文本内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "PDF文件的绝对或相对路径"},
                    "max_pages": {"type": "integer", "description": "最多读取页数，可选"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "发送纯文本邮件给指定收件人",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "收件人邮箱地址"},
                    "subject": {"type": "string", "description": "邮件主题"},
                    "body": {"type": "string", "description": "邮件正文内容"}
                },
                "required": ["recipient", "subject", "body"]
            }
        }
    }
]

# 工具映射
tool_map = {
    "extract_pdf_text": extract_pdf_text,
    "send_email": send_email
}

def run_agent(user_query):
    """主代理循环"""
    messages = []
    # 加载系统提示
    with open('prompts/system_prompt.txt', 'r', encoding='utf-8') as f:
        system_prompt = f.read()
    messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_query})

    while True:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        assistant_msg = response.choices[0].message
        messages.append(assistant_msg)

        # 检查是否有工具调用
        if not assistant_msg.tool_calls:
            # 最终回答
            return assistant_msg.content

        # 执行所有工具调用
        for tool_call in assistant_msg.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            # 调用对应函数
            result = tool_map[func_name](**func_args)
            # 返回结果给LLM
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
        # 继续循环，LLM会使用工具结果生成最终回复

if __name__ == "__main__":
    # 示例运行
    user_input = input("请输入您的请求（例如：请读取 test_sample.pdf，将摘要发送到 abc@example.com）: ")
    final_answer = run_agent(user_input)
    print("\n代理回复：")
    print(final_answer)
