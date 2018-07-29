from email.header import Header
from email.mime.text import MIMEText
import  smtplib



# 第三方 SMTP 服务
from flask import current_app

mail_host = "smtp.163.com"  # 设置服务器
mail_user = current_app.config.get('MAIL_USER') # 用户名
mail_pass = current_app.config.get('MAIL_PASS') # 口令


receivers = ['13152720003@163.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

mail_msg = """
<p>Python 邮件发送测试...</p>
<p><a href="http://www.runoob.com">这是一个链接</a></p>
"""
message = MIMEText(mail_msg, 'html', 'utf-8')

message['From'] = Header('ads', 'utf-8')
message['To'] =  Header("change", 'utf-8')

subject = 'Python SMTP 邮件'
message['Subject'] = Header(subject, 'utf-8')

smtpObj = smtplib.SMTP_SSL(mail_host,465)
smtpObj.set_debuglevel(1)
smtpObj.login(mail_user, mail_pass)
smtpObj.sendmail(mail_user, receivers, message.as_string())
smtpObj.quit()

print("邮件发送成功")
