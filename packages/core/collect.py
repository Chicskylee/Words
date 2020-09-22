# coding=utf-8
# =================================
# 作者声明：
# 文件用途：数据的收集和处理
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 其他依赖：无
# 编写时间：2018-07-08 11:37
# =================================
import sys
import getpass
import random
# ---------------------------------
from . import log
# ---------------------------------
from .independent import public
# ---------------------------------
# 日志记录
import logging
logger = logging.getLogger('main.collect')
# =================================

# 定义非法符号
# 注意：下划线默认为是合法符号
def invalid_symbols():
    logger.debug('程序到达：collect.py-invalid_symbols函数')
    symbols = [',', '.', '=', '+', '-', '*', '/',
    '%', '￥', '!', ':', ';', '…', '?', "'", '"',
    '~', '"', '@', '(', ')', '<', '>', '{', '}',
    '[', ']', '$', '|', '\\', '♀', '♂', '¥', '£',
    '¢', '€', '^', '`', '#',
    # 中文符号等
    '，', '。', '？', '！', '：', '；', '…', '～', '”',
    '”', '、', '（', '）', '—', '‘', '’', '·', '＠',
    '＆', '＊', '＃', '《', '》', '￥', '〈', '〉', '＄',
    '［', '］', '￡', '｛', '｝', '￠', '【', '】', '％',
    '〖', '〗', '／', '〔', '〕', '＼', '『', '』', '＾', '「',
    '」', '｜', '﹁', '﹂', '｀', '．', '«', '»', 'ˇ',
    '︾', '︽', '︷', '︸', '‥', '︻', '︼', '﹁', '﹁',
    '﹃', '﹄', '︹', '︺', '︿', '﹀', '︵', '︶', '╭',
    '╮', '╰', '╯', '†', '‡', '㈱', '§', '〓', '₩',
    '¤', 'Θ', '㊣', 'Ψ', '⊕', '⊙', '®', '©', '™', '◎',
    '◈', '♭', '♯', '‖', '¶', '♬', '♫', '♪', '♩', '︴',
    '￣', '﹊', '﹉', '﹌', '―', '﹎', '﹍', '﹏', '▓',
    '囍', '卍', '卐', '№', '╳', '※', '℡', '꧂', '꧁',

    'ᨐ', 'ᝰ', '☞', '☜', '♂', '♀', '↕', '↹', '⇔',
    '↔', '→', '↘', '↓', '↙', '←', '↗', '↑', '↑',
    '↖', '↣', '✔', '✘', '♝', '♞', '♛', '♚', '♟',
    '◥', '◤', '◣', '◢', '▼', '▲', '▽', '△', '★',
    '♣', '♠', '♥', '☆', '♧', '♤', '♡', '♦', '■',
    '■', '◆', '●', '♢', '●', '♢', '□', '◇', '○',
    # 数学符号
    '≠', '≈', '±', '÷', '×', '>', '<', '≥', '≤', '√',
    '‰', 'π', '³√', '℃', '℉', ]
    return symbols


def my_input(prompt):
    logger.debug('程序到达：collect.py-my_input函数')
    sys.stdout.write(prompt)
    sys.stdout.flush()
    content = sys.stdin.readline()[:-1]
    log.save_input_content(content, description='用户输入：')
    return content


# 获取用户输入，并返回用户输入的内容
# retry：出现异常后允许重新获取输入的次数
# getpwd：传入True时，将隐藏输入内容
# getnum：传入True时，只有获得一个数字才会返回
# error_exit：当为True时，函数将在未正确获取内容时退出程序；当为False时将抛出异常NameError
# error_prompt：函数退出时的提示
# strip_all：传入True时，将去除输入内容两端的空白符
# default：如果传入了值，则当用户输入值与activate_default相同时返回default的值
# activate_default：为字符串时，当用户输入内容与该值相同时返回default
# activate_default：为列表时，当用户输入内容为该值元素时返回default
def get_input(prompt=None, retry=0,
              getpwd=False, getnum=False,
              strip_all=False,
              error_exit=False, error_prompt=None,
              default=None, activate_default=None):
    prompt = '' if prompt is None else str(prompt)
    for i in range(retry+1):
        # 捕获QPython输入中文后再删除导致的异常
        try:
            if getpwd:
                str_input = getpass.getpass(prompt)
            elif getnum:
                str_input = my_input(prompt)
                if default is not None:
                    if isinstance(activate_default, str):
                        if activate_default == str_input:
                            return default
                    if isinstance(activate_default, (list, tuple, set)):
                        if str_input in activate_default:
                            return default
                if is_number(str_input):
                    return str_input
                else:
                    continue
            else:
                str_input = str(my_input(prompt))
                if default is not None:
                    if isinstance(activate_default, str):
                        if activate_default == str_input:
                            return default
                    if isinstance(activate_default, (list, tuple, set)):
                        if str_input in activate_default:
                            return default
            if strip_all:
                str_input = str_input.strip()
            return str_input
        except UnicodeDecodeError:
            print('输入异常，请重试！')
            continue
    if error_exit:
        if error_prompt is None:
            error_prompt='没有正确获取内容，已退出！'
        public.exit_program(error_prompt, pause=False)
    else:
        raise NameError('没有正确获取输入内容！')


# ---------------------------------
# 获取要翻译的内容
def get_content():
    logger.debug('程序到达：collect.py-get_content函数')
    print('-'*45)
    prompt = '请输入要翻译的内容：'
    content = get_input(prompt=prompt, retry=3)
    logger.info('获取到原文:{!r}'.format(content))
    return content

# ---------------------------------
# 判断database_name是否为合法的格式
def valid_database_name(database_name):
    logger.debug('程序到达：collect.py-valid_database_name函数')
    # 屏幕宽度不可以超过11
    if public.real_width_in_screen(database_name) > 11:
        return False
    if len(database_name) < 1:
        return False
    for i in database_name:
        if i in invalid_symbols():
            return False
    return True


# 让用户输入数据库名称
# 返回：数据库名称，字符串
# 异常返回：None
def get_database_name(prompt=None):
    logger.debug('程序到达：collect.py-get_database_name函数')
    if prompt is None:
        prompt = '请输入数据库名称：'
    for times in range(3, 0, -1):
        left_times = '[{}]'.format(times)
        database_name = get_input(prompt=left_times+prompt)
        if database_name == '':
            prompt = '没有输入内容，请重新输入：'
            continue
        elif valid_database_name(database_name):
            # 注意：数据库名称不允许超过13个英文字符长度
            # 注意：数据库名称不允许有非法字符
            verify = get_input('数据库名称：{}(确认*，重新输入Enter)：'.format(database_name))
            if verify == '*':
                return database_name
            else:
                prompt = '请重新输入：'
                continue
        else:
            prompt = '名称长度不可以超过11，请重新输入：'
            continue
    else:
        return None

# ---------------------------------

# 检查用户名的输入是否符合正确格式
def valid_username(username):
    logger.debug('程序到达：collect.py-valid_username函数')
    if not isinstance(username, str):
        return False
    if len(username) < 3:
        # 最短的超级用户名应该至少有3个字母
        return False
    return True


# 从用户获取用户名
@public.execute_func(execute=public.AUTHOR, result='user')
def get_username(prompt=None):
    logger.debug('程序到达：collect.py-get_username函数')
    if prompt is None:
        prompt = '请输入用户名：'
    for times in range(3, 0, -1):
        left_times = '[{}]'.format(times)
        username = get_input(left_times+prompt)
        if username == '':
            prompt = '没有输入内容，请重新输入：'
            continue
        if valid_username(username):
            # 格式正确，让用户核查
            verify_username = get_input('用户名：{}(确认*，重新输入Enter)：'.format(username))
            if verify_username == '*':
                return username
            else:
                prompt = '请重新输入用户名：'
                continue
        else:
            prompt = '用户名格式错误，请重新输入：'
            continue
    else:
        public.exit_program('次数用尽，已经退出！')


# ---------------------------------

# 检查email合适是否正确
def valid_email(email):
    logger.debug('程序到达：collect.py-valid_email函数')
    if not isinstance(email, str):
        return False
    if len(email) < 5:
        # 最短的邮址应该至少有5个字符：a@b.c
        return False
    email_split = email.split('@')
    if len(email_split) == 2:
        if '.' in email_split[1]:
            return True
        else:
            return False
    else:
        return False


# 从用户获取邮箱
# 返回：电子邮件地址
# 异常返回：None
@public.execute_func(execute=public.AUTHOR, result='x@x.x')
def get_email(prompt=None):
    logger.debug('程序到达：collect.py-get_email函数')
    if prompt is None:
        prompt = '请输入邮箱：'
    for times in range(3, 0, -1):
        left_times = '[{}]'.format(times)
        email = get_input(left_times+prompt)
        if email == '':
            prompt = '没有输入内容，请重新输入：'
            continue
        if valid_email(email):
            # 检查格式正确，用户确认检查
            verify_email = get_input('邮箱：{}(确认*，重新输入Enter)：'.format(email))
            if verify_email == '*':
                return email
            else:
                prompt = '请重新输入：'
                continue
        else:
            prompt = '格式错误，请重新输入：'
            continue
    else:
        return None
# ---------------------------------

# 检查密码的输入是否符合正确格式
def valid_password(password):
    logger.debug('程序到达：collect.py-valid_password函数')
    if not isinstance(password, str):
        return False
    if 6 <= len(password) <= 50:
        # 最短的密码应该至少有6个字符
        return True
    return False


# 检查密码长度是否符合正确格式
def valid_password_length(password_length):
    logger.debug('程序到达：collect.py-valid_password_length函数')
    if not isinstance(password_length, int):
        return False
    if 6 <= password_length <= 50:
        # 密码长度应该不少于6个字符，不大于50个字符
        return True
    return False


# 生成指定长度的随机密码，并返回密码字符串
def create_password(length):
    logger.debug('程序到达：collect.py-create_password函数')
    # 所有数字字符
    numbers = '0123456789'
    # 所有小写字母
    alphabets = 'abcdefghijklmnopqrstuvwxyz'
    # 所有大写字母
    capital_alphabets = alphabets.upper()
    # 允许的符号
    symbols = '@?!-=+*._%&$#'
    choice_add_symbol = input('允许密码中加入符号({})，确认Enter：'.format(symbols)) or '*'
    if choice_add_symbol == '*':
        strings = numbers + alphabets + capital_alphabets + symbols
    else:
        strings = numbers + alphabets + capital_alphabets
    # 密码生成
    return ''.join(random.sample(strings, length))


# 从用户获取将要自动生成的密码长度
def get_password_length(prompt=None):
    logger.debug('程序到达：collect.py-get_password_length函数')
    if prompt is None:
        prompt = '请输入密码长度：'
    for times in range(3, 0, -1):
        left_times = '[{}]'.format(str(times))
        password_length = get_input(left_times+prompt)
        if password_length == '':
            prompt = '没有输入内容，请重新输入：'
            continue
        try:
            password_length = int(password_length)
        except:
            prompt = '密码长度(整数)格式错误，请重新输入：'
            continue
        if valid_password_length(password_length):
            # 检查格式正确，用户确认检查
            verify_password_length = get_input('密码长度：{}(确认*，重新输入Enter)：'.format(password_length))
            if verify_password_length == '*':
                return password_length
            else:
                prompt = '请重新输入：'
                continue
        else:
            prompt = '密码长度(整数)格式错误，请重新输入：'
            continue
    else:
        public.exit_program('次数用尽，已经退出！')


# 自动生成随机密码
# 如果3此生成的密码都令人不满意，返回None
def auto_create_password():
    logger.debug('程序到达：collect.py-auto_create_password函数')
    for times in range(3, 0, -1):
        length = get_password_length()
        password = create_password(length=length)
        verify_password = get_input('密码：{}(确认*，重新生成Enter)：'.format(password))
        if verify_password == '*':
            return password
        else:
            prompt = '请重新输入：'
            continue
    else:
        print('次数用尽，已经退出，自动跳至手动收入！')


# 手动输入密码
def manual_create_password(prompt=None):
    logger.debug('程序到达：collect.py-manual_create_password函数')
    if prompt is None:
        prompt = '请输入密码(6<=长度<=50)：'
    for times in range(3, 0, -1):
        left_times = '[{}]'.format(times)
        password = get_input(left_times+prompt, getpwd=True)
        if password == '':
            prompt = '没有输入内容，请重新输入：'
            continue
        if valid_password(password):
            verify_password = get_input('请重新密码输入以确认：', getpwd=True)
            if verify_password == password:
                return password
            else:
                prompt = '两次输入的密码不同，请重新输入：'
                continue
        else:
            prompt = '密码(6<=长度<=50)格式不符合要求，请重新输入：'
            continue
    else:
        public.exit_program('次数用尽，已退出！')


# 获取密码
@public.execute_func(execute=public.AUTHOR, result='user')
def get_password(prompt=None):
    logger.debug('程序到达：collect.py-get_password函数')
    if prompt is None:
        prompt = '自动生成密码(确认Enter，手工输入*)：'
    for times in range(3, 0, -1):
        left_times = '[{}]'.format(times)
        choice_auto = get_input(left_times+prompt)
        if choice_auto == '':
            password = auto_create_password()
            if password is None:
                password = manual_create_password()
            return password
        elif choice_auto == '*':
            password = manual_create_password()
            return password
        else:
            prompt = '输入错误，自动生成密码(确认Enter，手工输入*)：'
            continue

