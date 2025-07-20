import getInfo
import time
import schedule
from datetime import datetime
from emailSend import send_email
import json
from env import *

def check_and_notify():
    if not login.is_session_valid() and not login.login():
        print(f"[{datetime.now()}] 登录失败")
        return
    
    # 从data.json读取订阅信息
    try:
        with open('data.json', 'r') as f:
            subscriptions = json.load(f)
    except Exception as e:
        print(f"[{datetime.now()}] 读取订阅信息失败: {e}")
        return
    
    print(f"[{datetime.now()}] 开始查询房间信息")
    for sub in subscriptions:
        try:
            room_id = int(sub['room_id'])
            info = login.query_room_info(room_id)
            remaining_amount=float(info.get('remaining_amount'))
            msg = f"房间 {info['room_name']} 剩余电量: {info.get('remaining_electricity', 'N/A')}度, 剩余金额: {info.get('remaining_amount', 'N/A')}元"
            if remaining_amount<=20 :
                #发送邮件通知
                send_email(
                    to_addr=sub['email'],
                    subject=f"电量提醒 {info['room_name']}",
                    content=msg,
                    smtp_server='smtp.163.com',
                    smtp_port=25,
                    from_addr='alargi@163.com',
                    password=Authorization_code
                )
                print(f"[{datetime.now()}] 已发送通知给 {sub['email']}: {msg}")
            else:
                print(f"[{datetime.now()}] 该房间电费未达警戒线 {sub['email']}: {msg}")
        except Exception as e:
            print(f"[{datetime.now()}] 处理房间 {sub.get('room_id')} 失败: {e}")

if __name__ == '__main__':
    # 初始化登录
    login = getInfo.UESTCLogin(username, password)
    
    # 设置定时任务
    schedule.every(2).minutes.do(check_and_notify)
    
    # 立即执行一次
    check_and_notify()
    
    # 主循环
    while True:
        schedule.run_pending()
        time.sleep(1)#检查间隔(秒)

