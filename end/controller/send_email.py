# import smtplib
# from email.mime.text import MIMEText
# from email.header import Header
# from email.utils import formataddr
# # 創建郵件內容
# msg = MIMEText('你好呀！這是用 Python 寄的信～', 'plain', 'utf-8') # 郵件內文
# msg['Subject'] = 'test測試'            # 郵件標題
# msg['From'] = 'C110156119@nkust.edu.tw'  # 顯示發送者名稱和郵箱，MIME 編碼
# msg['To'] = 'ylt18999@gmail.com'    # 主收件人（顯示用）

# # 實際的收件人列表（包含 To, Cc, Bcc 收件人）
# to_emails = ['ylt18999@gmail.com']
# cc_emails = ['ylt18999@gmail.com', 'ylt1899@gmail.com']
# bcc_emails = ['ylt18999@gmail.com', 'ylt1899@gmail.com']

# # 組合所有的收件人
# all_recipients = to_emails + cc_emails + bcc_emails

# # 連接到 Gmail 的 SMTP 伺服器
# smtp = smtplib.SMTP('smtp.gmail.com', 587)
# smtp.ehlo()
# smtp.starttls()

# # 使用應用程式專用密碼登入
# smtp.login('C110156119@nkust.edu.tw', 'F130377949')

# # 發送郵件，傳遞所有收件人
# status = smtp.send_message(msg, from_addr='C110156119@nkust.edu.tw', to_addrs=all_recipients)

# # 檢查發送狀態
# if status == {}:
#     print('郵件傳送成功！')
# else:
#     print('郵件傳送失敗！')
# smtp.quit()
#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# def send_verification_email(email: str, verification_link: str):
#     try:
#         sender_email = "C110156119@nkust.edu.tw"  # 這裡填入你的郵箱地址
#         receiver_email = email
#         password = "gtej gnzs bqhg tskq"  # 這裡填入你的郵箱密碼或應用密碼

#         message = MIMEMultipart("alternative")
#         message["Subject"] = "smart eye"
#         message["From"] = sender_email
#         message["To"] = receiver_email

#         # 郵件的正文內容
#         html = f"""\
#         <html>
#           <body>
#             <p>Hi,<br>
#                Thank you for registering with us. Please click on the link below to verify your email address:<br>
#                <a href="{verification_link}">Verify Email</a>
#             </p>
#           </body>
#         </html>
#         """
#         part = MIMEText(html, "html")
#         message.attach(part)

#         # 創建SMTP連接
#         with smtplib.SMTP_SSL('smtp.example.com', 465) as server:  # 這裡的 SMTP 服務器地址需要替換成您的SMTP服務提供商的地址
#             server.login(sender_email, password)
#             server.sendmail(sender_email, receiver_email, message.as_string())
#             print("Verification email sent successfully!")
#     except Exception as e:
#         print(f"Failed to send verification email: {e}")

import smtplib
from email.mime.text import MIMEText

def send_email(send_text):
    # Create the email content
    msg = MIMEText(send_text, 'plain', 'utf-8')
    # Email headers
    msg['Subject'] = 'test測試'
    msg['From'] = '智慧之眸 <C110156119@nkust.edu.tw>'
    msg['To'] = 'ylt18999@gmail.com'
    msg['Cc'] = 'ylt18999@gmail.com'
    msg['Bcc'] = 'ylt18999@gmail.com'
    # Initialize the SMTP connection and set local_hostname
    smtp = smtplib.SMTP('smtp.gmail.com', 587, local_hostname='localhost')  # Use 'localhost' as a safe hostname
    smtp.ehlo('localhost')  # Explicitly set 'localhost' for EHLO command
    smtp.starttls()
    # Login with your email credentials
    smtp.login('C110156119@nkust.edu.tw', 'gtej gnzs bqhg tskq')
    # Send the email
    status = smtp.send_message(msg)
    # Quit the SMTP session
    smtp.quit()
    # Check for success
    if status == {}:
        print('郵件傳送成功！')
        return{'status':200,"message":"郵件傳送成功！"}
    else:
        print('郵件傳送失敗！')
        return{'status':400,"message":"郵件傳送失敗！"}

import time
from datetime import datetime  # 匯入 datetime 模組
current_time = time.time()
formatted_time = datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
send_email(f"camera1 有人跌倒! 時間: {formatted_time}")
