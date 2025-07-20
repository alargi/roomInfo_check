import requests
from bs4 import BeautifulSoup
import execjs
from env import *

class UESTCLogin:
    def __init__(self, username, password):
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'keep-alive'
        }
        # 加载加密JS
        with open('encrypt.js', 'r', encoding='utf-8') as f:
            self.js_code = f.read()
        self.ctx = execjs.compile(self.js_code)
        self._is_logged_in = False

    def get_login_page(self):
        login_url = 'https://idas.uestc.edu.cn/authserver/login'
        response = self.session.get(login_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取表单中的隐藏字段
        execution = soup.find('input', {'name': 'execution'})['value']
        salt = soup.find('input', {'id': 'pwdEncryptSalt'})['value']
        return execution, salt

    def encrypt_password(self, password, salt):
        # 调用JS加密函数
        return self.ctx.call('encryptPassword', password, salt)

    def is_session_valid(self):
        """检查当前session是否仍然有效"""
        if not self._is_logged_in:
            return False
            
        test_url = 'https://eportal.uestc.edu.cn/qljfwapp/sys/lwUestcDormElecPrepaid/index.do'
        response = self.session.get(test_url, headers=self.headers)
        return response.status_code == 200

    def login(self):
        execution, salt = self.get_login_page()
        
        login_url = 'https://idas.uestc.edu.cn/authserver/login'
        data = {
            'username': self.username,
            'password': self.encrypt_password(self.password, salt),
            'captcha': '',
            '_eventId': 'submit',
            'cllt': 'userNameLogin',
            'dllt': 'generalLogin',
            'execution': execution
        }
        
        response = self.session.post(login_url, data=data, headers=self.headers, allow_redirects=False)
        
        # 打印详细响应信息
        print(f'Status Code: {response.status_code}')
        print(f'Response Headers: {response.headers}')
        print(f'Response Text: {response.text[:500]}...')  # 只打印前500
        
        if response.status_code == 302:
            print('登录成功')
            self._is_logged_in = True
            return True
        else:
            print('登录失败')
            return False

    def query_room_info(self, roomid:int):
        if not self.is_session_valid():
            if not self.login():
                raise Exception('登录失败，无法查询房间信息')
        
        # 首先访问 index 页面（确保会话初始化）
        index_url = 'https://eportal.uestc.edu.cn/qljfwapp/sys/lwUestcDormElecPrepaid/index.do'
        self.session.get(index_url, headers=self.headers)  # 不检查响应，只是为了初始化Cookie

        # 构造请求URL和数据
        url = 'https://eportal.uestc.edu.cn/qljfwapp/sys/lwUestcDormElecPrepaid/dormElecPrepaidMan/queryRoomInfo.do'

        # 修正请求头和请求体格式
        headers = {
            **self.headers,  # 继承原有headers
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',  # 关键：标记为AJAX请求
            'Referer': 'https://eportal.uestc.edu.cn/qljfwapp/sys/lwUestcDormElecPrepaid/index.do',
        }

        # 注意：roomIds 必须是字符串形式的JSON（非Python对象）
        payload = {
            "roomIds": '[{"DORM_ID":"'+str(roomid)+'"}]'  # 字符串格式！
        }

        # 发送请求（使用 data 而非 json）
        response = self.session.post(url, headers=headers, data=payload)

        # 调试：打印实际发送的请求头和响应
        #print("响应内容:", response.text)

        # 检查响应
        if response.status_code != 200:
            raise Exception(f"请求失败，状态码: {response.status_code}")

        try:
            data = response.json()
        except ValueError:
            raise Exception(f"JSON解析失败，响应内容: {response.text[:200]}...")

        if not data or not isinstance(data, list):
            raise Exception(f"响应数据为空或格式错误: {data}")

        room_info = data[0].get("roomInfo", {})
        if room_info.get("retcode") != 0:
            raise Exception(f"查询失败: {room_info.get('msg', '未知错误')}")

        return {
            "building_id": room_info.get("buiId"),
            "room_id": room_info.get("roomId"),
            "room_name": room_info.get("roomName"),
            "remaining_amount": room_info.get("syje"),
            "remaining_electricity": room_info.get("sydl"),
        }
if __name__ == '__main__':
    login = UESTCLogin(username, password)
    for a in range(1,60):
        b="10950"+str(a) if a<10 else "1095"+str(a)
        info = login.query_room_info(b)
        msg = f"房间 {info['room_name']} 剩余电量: {info.get('remaining_electricity', 'N/A')}度, 剩余金额: {info.get('remaining_amount', 'N/A')}元"
        print(msg)