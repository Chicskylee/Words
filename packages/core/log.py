# coding=utf-8
# =================================
# 作者声明：
# 文件用途：记录和发送日志文件
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 第三方库依赖：无
# =================================
# ---------------------------------
from .independent import path
from .independent import emails
from .independent import public
# =================================
# 日志
import logging
logger = logging.getLogger('main.log')
# =================================

# 日志记录 logger，为防止重复log应该仅允许main调用
def get_logger(log_name, log_level=None):
    logger.info('程序到达：log.py-get_logger函数')
    level_dict = {'debug':logging.DEBUG,
                  'info':logging.INFO,
                  'warn':logging.WARN,
                  'error':logging.ERROR,
                  'fatal':logging.FATAL,
                  'critical':logging.CRITICAL}
    if log_level in level_dict:
        level = level_dict[log_level]
    else:
        level = level_dict['info']
    # 全局日志记录设置
    logger = logging.getLogger(log_name)
    logger.setLevel(level=level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s')

    # 设置日志的输出流为文件
    debug_filename = path.own.debug_filename()
    file_handler = logging.FileHandler(debug_filename, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


# 将日志记录文件通过附件发送到邮箱
# e：异常提示
def send_log(e):
    logger.info('程序到达：log.py-send_log函数')
    log_filename = path.own.debug_filename()
    log_name = path.get_basename(log_filename)
    submit_time = public.get_detail_strftime()
    mail = dict()
    mail['receiver_address'] = emails.author_addr()
    body_datas = [('提交时间', submit_time),
                  ('异常原因', e)]
    mail['email_body'] = emails.mail_body(*body_datas)
    mail['email_subject'] = '单词程序异常:{}'.format(e)
    mail['attachment_filename'] = log_filename
    mail['attachment_type'] = 'text'
    mail['attachment_format'] = 'log'
    mail['attachment_name'] = log_name
    emails.send_attachment_email(**mail)


# 保存用户输入的数据，用于调试程序
def save_input_content(text, description=None):
    logger.info('程序到达：log.py-save_input_content函数')
    # 这些内容不记录：空格代表退出
    if text in ['', ]:
        return None
    if description is None:
        description = ''
    filename = path.own.input_filename()
    submit_time = public.get_detail_strftime()
    record = '{}|{}{}\n'.format(submit_time, description, text)
    public.write(record, filename=filename, mode='ab')


# 记录自动导入函数翻译失败的单词
def record_translate_failed(content, add_time=False):
    logger.info('程序到达：log.py-record_translate_failed函数')
    translate_failed_filename = path.own.debug_translate_failed_filename()
    if add_time:
        translate_failed_time = public.get_strftime(format='%Y-%m-%d %H:%M:%S')
        text = '{} - {}\n'.format(translate_failed_time, content)
    else:
        text = '{}\n'.format(content)
    public.write(text, filename=translate_failed_filename, mode='ab', coding='utf8')

