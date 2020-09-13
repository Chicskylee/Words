# coding=utf-8
# =================================
# 作者声明：
# 文件用途：公共函数
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 其他依赖：无
# 编写时间：2018-07-08 11:37
# =================================
import os
import re
import sys
import time
import pickle
import datetime
import functools
# =================================
# 日志记录
import logging
logger = logging.getLogger('main.public')
# =================================
# 全局调用该参数，DEBUG = True 时，不执行清屏
DEBUG = False
# =================================

# 重写print函数，不兼容Py2(因为get)
def my_print(*args, **kargs):
    logger.debug('程序到达：public.py-my_print函数')
    sep = kargs.get('sep', ' ')
    end = kargs.get('end', '\n')
    flush = kargs.get('flush', True)
    length = len(args)
    for index, line in enumerate(args):
        sys.stdout.write(line)
        if index < (length-1):
            sys.stdout.write(sep)
        if flush:
            sys.stdout.flush()
    sys.stdout.write(end)
    sys.stdout.flush()

# =================================
# 文本处理函数

# 判断一段文字是否是英文
# 注意：因获取音标所用网址中不能有非英文，必须进行判断
def is_english(content):
    logger.debug('程序到达：public.py-is_english函数')
    if isinstance(content, list):
        logger.info('注意：传入内容是列表，不是字符串！')
        return False
    if isinstance(content, tuple):
        logger.info('注意：传入内容是元组，不是字符串！')
        return False
    if isinstance(content, dict):
        logger.info('注意：传入内容是字典，不是字符串！')
        return False
    # 英文字母
    en_alphabet = "abcdefghijklmnopqrstuvwxyz"
    # 英文符号
    en_symbol = "/'-. ,"
    # 数字
    integer_symbol = "1234567890"
    english_text = en_symbol + en_alphabet + integer_symbol
    pure_english_text = en_alphabet + integer_symbol
    for alphabet in content:
        if alphabet.lower() not in english_text:
            return False  # 非英文
    # 通过第一层测试以后可能还有只有符号没有字母和数字的字符串
    for alphabet in content:
        # 对于只包含英文符号的字符串，
        # 只要有一个字母或数字，即可认为是英文单词、词组或句子等
        if alphabet.lower() in pure_english_text:
            return True  # 英文
    # 如果到这里还没有遇到return说明不是英文
    return False  # 非英文


# 判断一段内容是单词还是词组
def is_phrase(content):
    logger.debug('程序到达：public.py-is_phrase函数')
    content = content.strip(' ')  # 首先去除字符串两端的空格
    for alphabet in content:
        if alphabet == ' ':
            return True
    return False


# 对输入进行处理
def deal_content(content):
    logger.debug('程序到达：public.py-deal_content函数')
    # 首先去除两端的空白符
    content = content.strip()
    if is_english(content):
        # 如果是英文，则处理掉其中的省略号
        if '…' in content:
            # 将英文省略号替换为空格
            content = content.replace('…', ' ')
            # 将多个空格替换为单个空格
            content = content.replace('  ',' ')
            # 最后将两端多余空格去除
            content = content.strip()
            return content
    return content


# 确定某一字符串中是否包含序列中的任一元素
# 即，只要sequence中的任何一个元素在s中，返回True
# sequence：序列
# s：字符串
# 返回：True 或 False
def any_element(sequence, s):
    logger.debug('程序到达：public.py-any_element函数')
    for element in sequence:
        if element in s:
            return True
    return False


# 确定某一字符串中是否包含序列中的所有元素
# 即，只有sequence中的每个元素都在s中，返回True
# sequence：序列
# s：字符串
# 返回：True 或 False
def all_element(sequence, s):
    logger.debug('程序到达：public.py-all_element函数')
    for element in sequence:
        if element not in s:
            return False
    return True


# =================================
# 退出程序函数

# 退出程序，并在退出前给出提示(prompt)
# 如果pause是True，则在给出提示时暂停
def exit_program(prompt=None, pause=False):
    logger.debug('程序到达：public.py-exit_program函数')
    if pause:
        input(prompt if prompt is not None else '')
    elif prompt is not None:
        print(prompt)
    # 退出前关闭日志记录，写入所有该写入的数据
    logging.shutdown()
    sys.exit()


# 根据用户输入的内容，判断是否退出程序
def judge_exit(content, prompt=None, debug=False):
    logger.debug('程序到达：public.py-judge_exit函数')
    if debug and (content == '**'):
        logger.info('-----DEBUG:虽然程序正以debug模式运行但是强制执行了退出！')
    elif content not in ['@', ',', '，', '']:
        return None
    elif debug:
        print('-----DEBUG:\033[96m程序正以debug模式运行，因此不执行退出命令\033[0m')
        logger.info('程序正以debug模式运行，因此不执行退出命令')
        return None
    if prompt is None:
        prompt = '已退出！'
    exit_program(prompt=prompt)

# =================================

# 写入pickle文件
def write_pickle(object, filename):
    logger.debug('程序到达：public.py-write_pickle函数')
    with open(filename, 'wb') as f:
        pickle.dump(object, f)


# 读取pickle文件
def read_pickle(filename):
    logger.debug('程序到达：public.py-read_pickle函数')
    with open(filename, 'rb') as f:
        return pickle.load(f)

# ---------------------------------

# 写文本文件
def write(text, filename, mode='wb', coding='utf8'):
    logger.debug('程序到达：public.py-write函数')
    with open(filename, mode) as f:
        f.write(text.encode(coding))


# 读取文本文件
def read(filename, coding='utf8'):
    logger.debug('程序到达：public.py-read函数')
    with open(filename, 'rb') as f:
        bytes_content = f.read()
        try:
            content = bytes_content.decode(coding)
        except UnicodeDecodeError as e:
            str_e = str(e)
            logger.info('发现解码异常：{}'.format(str_e), exc_info=True)
            logger.info('发生解码异常的文件：{}'.format(filename))
            raise
        return content

# ---------------------------------

# 读取一个文件的字节大小
def get_filesize(filename):
    logger.debug('程序到达：public.py-get_filesize函数')
    with open(filename, 'rb') as f:
        return len(f.read())

# =================================
# 字符串处理


# 统计中文字符个数
def count_chinese(s):
    logger.debug('程序到达：public.py-count_chinese函数')
    pattern = '[^a-zA-Z0-9{}]'.format(''' -_/@"'\\\.%,:!''')
    return len(re.findall(pattern, s))


# 统计字符的实际打印长度
# ch_length：一个中文在屏幕上打印时的宽度，默认为2
def real_width_in_screen(s, ch_length=2):
    logger.debug('程序到达：public.py-real_width_in_screen函数')
    ch = count_chinese(s)
    return ch*ch_length + (len(s)-ch)


# 将中文字符编码
def str_encode(content, encoding='utf-8'):
    logger.debug('程序到达：public.py-str_encode函数')
    content_encode = str(content.encode(encoding))
    content_deal = content_encode.replace(r'\x', '%').lstrip("b'").rstrip("'")
    return content_deal.upper()

# =================================
# 时间相关的函数

# 获取时间字符串
def get_strftime(format='%y-%m-%d %H:%M:%S'):
    logger.debug('程序到达：public.py-get_strftime函数')
    return time.strftime(format)


# 获取精确时间字符串
def get_detail_strftime():
    logger.debug('程序到达：public.py-get_detail_strftime函数')
    return str(datetime.datetime.now())


# 获取纯数字的20位的精确时间字符串
def get_detail_time_now():
    logger.debug('程序到达：public.py-get_detail_time_now函数')
    detail_time = str(datetime.datetime.now())
    # 去除不需要的符号，设置替换表，并完成替换
    table = '*'.maketrans({sub:None for sub in '-: .'})
    detail_time = detail_time.translate(table)
    # 不足20位，用0补齐
    return '{:<020s}'.format(detail_time)


# =================================
# 装饰器


# 装饰器工厂之捕获异常并重试
# prompt：每次重试的提示，默认设置为None，表示不提示
# retry：允许重试的次数，默认 3
# exception：单一异常类型或元组，用来指明要捕获的异常，默认捕获所有一般异常 Exception
# 注意：当exception是元组时，不会捕获没有指明的异常
# abnormal_return：如果重试次数用尽，返回该值，默认为None
# force_return：如果是True，则尝试失败后，即使abnormal_return是None，也返回None
# 注意：重试成功，则返回函数的返回值
# 注意：在没有指定异常返回值时，尝试次数用尽，则再次抛出异常
def retry_decorator(prompt=None,
          retry=3, exception=None,
          abnormal_return=None, force_return=False):
    logger.debug('程序到达：public.py-retry_decorator函数')
    if exception is None:
        exception = Exception
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for times in range(retry, 0, -1):
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    logger.info('装饰器捕获函数的异常：{} ===> {}'.format(func.__name__, e), exc_info=True)
                    if prompt is not None:
                        print('[{}]'.format(times)+prompt)
                    if times != 1: continue
                    if force_return or (abnormal_return is not None):
                        return abnormal_return
                    else:
                        raise
        return wrapper
    return decorator


# 计算函数运行时间：用于评估算法效率
# 注意：本装饰器可以装饰递归函数
def timeit(func, count=set()):
    logger.debug('程序到达：public.py-timeit函数')
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if func not in count:
            count.add(func)
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print('用时：{:.2f}s'.format(end-start))
            count.remove(func)
        else:
            result = func(*args, **kwargs)
        return result
    return wrapper


# 捕获严重异常：当程序意外崩溃时调用
def catch_exception(func, count=set()):
    logger.debug('程序到达：public.py-catch_exception函数')
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if func not in count:
            count.add(func)
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                logger.fatal('程序崩溃了:{}'.format(e), exc_info=True)
                exit_program(prompt='程序崩溃了！请联系程序开发者！')
            count.remove(func)
        else:
            result = func(*args, **kwargs)
        return result
    return wrapper



# 检查路径是否存在，如果不存在，则创建后再返回该路径，否则直接返回
def create_path(func, count=set()):
    logger.debug('程序到达：public.py-create_path函数')
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if func not in count:
            count.add(func)
            path = func(*args, **kwargs)
            if not os.path.exists(path):
                os.mkdir(path)
            count.remove(func)
        else:
            path = func(*args, **kwargs)
        return path
    return wrapper

