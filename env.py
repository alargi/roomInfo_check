from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()  # 默认加载当前目录下的 .env 文件

# 读取变量
username = os.getenv("API_USERNAME")
password = os.getenv("API_PASSWORD")
Authorization_code=os.getenv("Authorization_code")
if __name__ == "__main__":
    print(f"Username: {username}, Password: {password},Authorization_code:{Authorization_code}")