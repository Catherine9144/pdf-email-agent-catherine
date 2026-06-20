import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional

def send_email(recipient: str, subject: str, body: str, 
               sender: Optional[str] = None, 
               password: Optional[str] = None,
               smtp_server: Optional[str] = None,
               smtp_port: Optional[int] = None) -> str:
    """
    发送纯文本邮件。
    """
    # 从环境变量读取默认值
    sender = sender or os.getenv('EMAIL_SENDER')
    password = password or os.getenv('EMAIL_PASSWORD')
    smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
    
    if not sender or not password:
        raise ValueError("发件人邮箱或密码未设置")

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()
        return f"邮件已成功发送至 {recipient}"
    except Exception as e:
        return f"邮件发送失败: {str(e)}"
