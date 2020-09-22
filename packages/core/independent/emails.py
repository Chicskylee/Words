# coding=utf-8
# =================================
# 作者声明：
# 文件用途：处理发送邮件
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 其他依赖：无
# 编写时间：2018-07-08 11:37
# =================================
# 构造邮件
import email
import email.header
import email.utils
import email.mime.text
import email.mime.multipart
import email.mime.base
# ---------------------------------
# 发送邮件
import smtplib
# 捕获socket.gaierror异常
import socket
# ---------------------------------
# 从顶层文件执行本脚本使用
from . import path
from . import public
# =================================
# 日志记录
import logging
logger = logging.getLogger('main.email')
# =================================

# 读取用户配置文件
# author：为True，则当无程序签名时，程序强制退出；否则继续运行
@public.execute_func(execute=public.AUTHOR, result=False)
def read_author_config():
    logger.debug('程序到达：emails.py-read_author_config函数')
    author_filename = path.own.author_filename()
    if not path.path_exist(author_filename):
        logger.info('不存在程序签名！')
        public.exit_program(prompt='不存在程序签名，已退出！')
    return public.read_pickle(author_filename)


# 作者邮箱
def author_addr():
    logger.debug('程序到达：emails.py-author_addr函数')
    return read_author_config()['addr']


# 作者密码
def author_pwd():
    logger.debug('程序到达：emails.py-author_pwd函数')
    return read_author_config()['pwd']


# =================================

# 格式化签名
def signature_format(signature, address):
    logger.debug('程序到达：emails.py-signature_format函数')
    signature_encoded = email.header.Header(signature, 'utf-8').encode('utf-8')
    return email.utils.formataddr((signature_encoded, address))


# 生成html格式的邮件正文
# args：列表，其每个元素都是二元元组，代表(描述, 具体值)
# 返回：一个字符串，代表邮件的正文
def mail_body(*args):
    logger.debug('程序到达：emails.py-mail_body函数')
    template = '<html><body>{}\n</body></html>'
    content = str()
    for describe, value in args:
        content += '\n<p>{}：{}</p>'.format(describe, value)
    return template.format(content)

# =================================

# 发送纯文本格式的邮件
@public.execute_func(execute=public.AUTHOR, result=False)
def send_plain_email(receiver_address,
           email_subject, email_body):
    logger.debug('程序到达：emails.py-send_plain_email函数')
    receiver_signature = receiver_address
    sender_address = author_addr()
    sender_password = author_pwd()
    sender_signature = sender_address
    debug=False
    # ---------------------------------------
    # 邮件的构造
    mail = email.mime.text.MIMEText(email_body, 'plain', 'utf-8')
    mail['From'] = signature_format(sender_signature, sender_address)
    mail['To'] = signature_format(receiver_signature, receiver_address)
    mail['Subject'] = email.header.Header(email_subject, 'utf-8').encode('utf-8')
    # ---------------------------------------
    # 邮件的发送
    smtp_server = 'smtp.qq.com'
    smtp_server_port = 465
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_server_port)
        server.set_debuglevel(debug)
        server.login(sender_address, sender_password)
        string_email = mail.as_string()
        receiver_addresses = [receiver_address, ]
        server.sendmail(sender_address, receiver_addresses, string_email)
        server.quit()
        return True
    except smtplib.SMTPServerDisconnected as e:
        logger.info('失败：邮件上传被迫中断：{}'.format(e))
        return False
    except socket.gaierror as e:
        logger.info('失败：网络连接失败：{}'.format(e))
        return False
    except TimeoutError as e:
        logger.info('失败：网络连接超时{}'.format(e))
        return False
    except OSError as e:
        try:
            logger.info('失败：连接异常：{}'.format(eval(str(e))[1].decode('gbk')))
        except Exception as e1:
            logger.info('失败：连接异常：{}'.format(e))
        return False
    except Exception as e:
        logger.error('失败：未知其它异常：{}'.format(e), exc_info=True)
        return False


# 发送带有附件的邮件
@public.execute_func(execute=public.AUTHOR, result=False)
def send_attachment_email(receiver_address,
        email_subject, email_body,
        attachment_filename, attachment_type,
        attachment_format, attachment_name):
    logger.debug('程序到达：emails.py-send_attachment_email函数')
    receiver_signature = receiver_address
    sender_address = author_addr()
    sender_password = author_pwd()
    sender_signature = sender_address
    debug=False
    # ---------------------------------------
    # 邮件的构造
    mail = email.mime.multipart.MIMEMultipart()
    mail['From'] = signature_format(sender_signature, sender_address)
    mail['To'] = signature_format(receiver_signature, receiver_address)
    mail['Subject'] = email.header.Header(email_subject, 'utf-8').encode('utf-8')
    mail_body = email.mime.text.MIMEText(email_body, 'html', 'utf-8')
    mail.attach(mail_body)
    attachment = email.mime.base.MIMEBase(attachment_type, attachment_format, filename=attachment_name)
    attachment.add_header('Content-Disposition', 'attachment', filename=attachment_name)
    attachment.add_header('Content-ID', '<0>')
    attachment.add_header('X-Attachment-Id', '<0>')
    with open(attachment_filename, 'rb') as f:
        attachment_content = f.read()
    attachment.set_payload(attachment_content)
    email.encoders.encode_base64(attachment)
    mail.attach(attachment)
    # ---------------------------------------
    # 邮件的发送
    smtp_server = 'smtp.qq.com'
    smtp_server_port = 465
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_server_port)
        server.set_debuglevel(debug)
        server.login(sender_address, sender_password)
        string_email = mail.as_string()
        receiver_addresses = [receiver_address, ]
        server.sendmail(sender_address, receiver_addresses, string_email)
        server.quit()
        return True
    except smtplib.SMTPServerDisconnected as e:
        logger.info('失败：邮件上传被迫中断：{}'.format(e))
        return False
    except socket.gaierror as e:
        logger.info('失败：网络连接失败：{}'.format(e))
        return False
    except TimeoutError as e:
        logger.info('失败：网络连接超时{}'.format(e))
        return False
    except OSError as e:
        try:
            logger.info('失败：连接异常：{}'.format(eval(str(e))[1].decode('gbk')))
        except Exception as e1:
            logger.info('失败：连接异常：{}'.format(e))
        return False
    except Exception as e:
        logger.error('失败：未知其它异常：{}'.format(e), exc_info=True)
        return False

