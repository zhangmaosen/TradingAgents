from zai import ZhipuAiClient
from openai import OpenAI
import os
from dotenv import load_dotenv

# 自动加载.env文件中的环境变量
load_dotenv()

# 从环境变量读取API KEY（需在.env中设置ZHIPU_API_KEY）
api_key = os.getenv("ZHIPU_API_KEY")
if not api_key:
    raise ValueError("ZHIPU_API_KEY environment variable is not set. Please set it in your .env file.")
client = ZhipuAiClient(api_key=api_key)
response = client.embeddings.create(
    model="embedding-3", #填写需要调用的模型编码
    input=[
        "美食非常美味，服务员也很友好。",
        "这部电影既刺激又令人兴奋。",
        "阅读书籍是扩展知识的好方法。"
    ],
)
print(response)