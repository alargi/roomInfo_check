from flask import Flask, render_template, request, jsonify
import json
from getInfo import UESTCLogin
from main import send_email
from env import *

app = Flask(__name__,static_folder='static')
DATA_FILE = 'data.json'

# 初始化登录
login = UESTCLogin(username, password)

# 确保数据文件存在
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query_room():
    data = request.get_json()
    room_id = data.get('room_id')
    if not room_id:  # 检查房间号是否为空
        return jsonify({'success': False, 'message': '房间号不能为空'})
    try:
        info = login.query_room_info(int(room_id))
        return jsonify({
            'success': True,
            'data': {
                'room_name': info.get('room_name', 'N/A'),
                'remaining_electricity': info.get('remaining_electricity', 'N/A'),
                'remaining_amount': info.get('remaining_amount', 'N/A')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    room_id = data.get('room_id')
    email = data.get('email')

    try:
        with open(DATA_FILE, 'r') as f:
            subscriptions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        subscriptions = []

    subscriptions.append({'room_id': room_id, 'email': email})

    with open(DATA_FILE, 'w') as f:
        json.dump(subscriptions, f)
    
    # 添加邮件通知
    send_email(
        to_addr=email,
        subject='订阅成功通知',
        content=f'您已成功订阅房间{room_id}的电量提醒服务',
        smtp_server='smtp.163.com',
        smtp_port=25,
        from_addr='alargi@163.com',
        password=Authorization_code
    )

    return jsonify({'success': True})

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    data = request.get_json()
    email = data.get('email')

    try:
        with open(DATA_FILE, 'r') as f:
            subscriptions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        subscriptions = []

    # 过滤掉该邮箱的所有订阅
    new_subscriptions = [sub for sub in subscriptions if sub['email'] != email]

    with open(DATA_FILE, 'w') as f:
        json.dump(new_subscriptions, f)
    
    # 添加邮件通知
    send_email(
        to_addr=email,
        subject='取消订阅通知',
        content='您已成功取消所有房间的电量提醒服务',
        smtp_server='smtp.163.com',
        smtp_port=25,
        from_addr='alargi@163.com',
        password=Authorization_code
    )

    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)