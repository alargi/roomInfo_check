import smtplib
from email.mime.text import MIMEText
from email.header import Header
from env import *

def send_email(to_addr, subject, content,
               smtp_server='smtp.example.com',
               smtp_port=587,
               from_addr='your_email@example.com',
               password='your_password'):
    """
    发送邮件到指定邮箱
    :param to_addr: 收件人邮箱
    :param subject: 邮件主题
    :param content: 邮件内容
    :param smtp_server: SMTP服务器地址
    :param smtp_port: SMTP端口
    :param from_addr: 发件人邮箱
    :param password: 发件人邮箱密码/授权码
    """
    # 创建邮件对象
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = Header(from_addr)
    message['To'] = Header(to_addr)
    message['Subject'] = Header(subject)

    try:
        # 连接SMTP服务器
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # 启用TLS加密
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], message.as_string())
        print('邮件发送成功')
    except Exception as e:
        print(f'邮件发送失败: {e}')
    finally:
        server.quit()

if __name__ == '__main__':
    send_email(
        to_addr='alargi@163.com',
        subject=f"邮箱发送功能测试",
        content="邮箱发送成功",
        smtp_server='smtp.163.com',
        smtp_port=25,
        from_addr='alargi@163.com',
        password=Authorization_code
    )
    print(f"邮件已发送 ")