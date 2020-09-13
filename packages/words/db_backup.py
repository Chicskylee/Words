# coding=utf-8
# =================================
# 作者声明：
# 文件用途：对用户字典进行备份
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 其他依赖：无
# =================================
import sys
import os
import zipfile
# ---------------------------------
from ..core import config
from ..core.independent import path
from ..core.independent import public
from ..core.independent import emails
# =================================
# 日志记录
import logging
logger = logging.getLogger('main.db_backup')
# =================================

# 压缩进度条的实现
def progress_bar(completed, total, prompt=''):
    logger.debug('程序到达：db_backup.py-progress_bar函数')
    rate = completed / total
    symbols_all_len = 35
    compressed_symbols_len = int(symbols_all_len*rate)
    other_symbols_len = symbols_all_len - compressed_symbols_len
    compressed_symbols = compatible.colorize(' '*compressed_symbols_len, color='white')
    other_symbols = compatible.colorize(' '*other_symbols_len, color='black')
    if completed != total:
        sys.stdout.write(' 已压缩:|{}{}|{:>6.2f}%\r'.format(compressed_symbols, other_symbols, rate*100))
    else:
        sys.stdout.write(' 已压缩:|{}{}|{:>6.2f}%\n'.format(compressed_symbols, other_symbols, rate*100))
    sys.stdout.flush()


# 获取文件夹中内容的总大小
def get_filesize(path):
    logger.debug('程序到达：db_backup.py-get_filesize函数')
    size_total = 0
    for path, _, names in os.walk(path):
        for name in names:
            filename = os.path.join(path, name)
            size = os.path.getsize(filename)
            size_total += size
    return size_total


# 压缩指定文件夹下的所有文件和文件夹及其内容
# 成功压缩，则返回：(压缩文件个数，压缩文件名)
# source_path:资源文件目录的路径
# zip_filename:要压缩成的zip文件名的字符串
# ban_names:不压缩文件列表，必须传入可迭代的序列
def make_zip(source_path, zip_filename,
             ban_names=None, auto=False,
             print_prompt=True):
    logger.debug('程序到达：db_backup.py-mate_zip函数')
    # 把所有的windows文件路径分隔符'\'改为'/'
    source_path = source_path.replace('\\', '/')
    # 去除行尾的路径分隔符
    source_path = source_path.rstrip('/')
    # ------------------------------------------
    # 不压缩文件集合，source_path下的该文件不压缩
    if ban_names is None:
        ban_names = set()
    elif isinstance(ban_names, (tuple, set, list)):
        ban_names = set(ban_names)
    else:
        raise ValueError('ban_names只能是集合、元组或列表！')
    zip_name = os.path.basename(zip_filename)
    # 不压缩自身，否则会造成永远也压缩不完的问题
    ban_names.add(zip_name)
    # QPython自动生成的临时文件也不压缩
    ban_names.add('.last_tmp.py')
    # -----------------------------
    if os.path.exists(zip_filename):
        # 若存储路径中已存在同名压缩包,要求用户判断是否继续
        if auto:
            return False
        else:
            print('注意！存储目录下已存在同名zip文件，继续将覆盖原zip文件！')
            print(zip_filename)
            choice = str(input('继续输入星号(*)，停止请按任意键：'))
            if choice != '*':
                print("已终止压缩任务")
                return False
    try:
        z = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED)
    except IOError as e:
        logger.error('出现异常：{}'.format(e), exc_info=True)
        public.exit_program(prompt=None, pause=False)
    delLength = len(os.path.dirname(source_path))  # 获取父目录
    # 获取文件夹大小，用于打印进度条
    source_size = get_filesize(source_path)
    # 对已经压缩的文件进行统计
    compressed_size = 0
    # 对压缩的文件计数
    n = 0
    for path, _, names in os.walk(source_path):
      for name in names:
          filename = os.path.join(path, name)
          if name in ban_names:
              # 跳过压缩自身，并跳过不压缩文件
              continue
          inZipName = filename[delLength:].strip('/')  # 相对路径
          file_size = os.path.getsize(filename)
          compressed_size += file_size
          if print_prompt:
              progress_bar(compressed_size,
                           source_size,
                           prompt=filename.replace(source_path, '~'))
          z.write(filename, inZipName)
          if os.path.isfile(filename):
              n += 1
    z.close()
    if print_prompt:
        print()
    return (n, zip_filename)


# 备份单词数据文件
# 返回：一个元组：(备份文件个数, 备份文件名路径)
# 注意：备份文件的默认存储路径必须是全路径
# 例如：'/sdcard/__temp__'
# per_day：用来指定每几天备份一次
# auto：当为False时，如果当天已经备份，会询问是否重新备份
def backup_words_data(per_day=4, auto=True, print_prompt=False):
    logger.debug('程序到达：db_backup.py-backup_words_data函数')
    # 获取今天的日期
    today = int(public.get_strftime("%d"))
    # 首先判断今天是否需要备份，如果计算结果是0则需要备份
    if (today % per_day) == 0:
        # 注意：备份需要一段时间，应该提示用户备份时等待……
        database_name = config.get_database_name()
        source_path = path.user.word(database_name)
        # 获取备份文件名路径
        zip_filename = path.user.zip_filename(database_name)
        zip_result = make_zip(source_path,
            zip_filename,
            ban_names=None,
            auto=auto,
            print_prompt=print_prompt)
        if zip_result:
            n, target_filename = zip_result
            if print_prompt:
                print('备份文件个数：{}\n备份文件路径：{}'.format(n, target_filename))
            # 如果压缩包内一个文件也没有，就把压缩包删除
            if n < 1:
                # 删除压缩包
                path.os_remove(target_filename)
                return None
            return (n, target_filename)
        else:
            return None
    else:
        # 如果计算结果不等于0，说明今天不需要备份数据库
        return None


# 备份数据以及配置文件更新
# per_day：每几天备份一次
# auto：如果当天已经备份，该参数传入False将允许用户确认重新备份，否则不再备份
def backup_data(per_day=5, auto=True):
    logger.debug('程序到达：db_backup.py-backup_data函数')
    logger.info('程序进入备份数据和配置文件更新函数')
    # 备份数据
    backup_result = backup_words_data(per_day=per_day, auto=auto)
    if backup_result is None:
        logger.info('不存在压缩过的备份数据，不需要备份')
        return None
    backup_amount, backup_filename = backup_result
    # 当不存在需要备份的文件时，直接退出
    if backup_amount < 1:
        logger.info('不存在需要备份的文件，不需要备份')
        return None
    backup_name = path.get_basename(backup_filename)
    user_name = config.get_user_name()
    init_time = config.get_init_time()
    submit_time = public.get_detail_strftime()
    mail = dict()
    # 应当填入用户邮址，不是user_name
    mail['receiver_address'] = config.get_user_email()
    body_datas = [
        ('归属用户', user_name),
        ('创建时间', init_time),
        ('备份时间', submit_time),
        ('备份包名', backup_name),
        ('文件数量', backup_amount)]
    mail['email_body'] = emails.mail_body(*body_datas)
    mail['email_subject'] = '{}_{}'.format(user_name, backup_name)
    mail['attachment_filename'] = backup_filename
    mail['attachment_type'] = 'Compressed Package'
    mail['attachment_format'] = 'zip'
    mail['attachment_name'] = backup_name
    emails.send_attachment_email(**mail)
    logger.info('存在备份数据的压缩包，已经成功备份')




