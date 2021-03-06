# coding=utf-8
# =================================
# 作者声明：
# 文件用途：过滤出需要的单词
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 其他依赖：无
# =================================
import re
# ---------------------------------
# 从顶层文件执行本脚本使用
from . import translate
from . import db_audio
from . import db_word
from . import db_backup
from . import db_export
# ---------------------------------
# 从顶层文件执行本脚本使用
from ..core import config
from ..core import collect
from ..core.independent import path
from ..core.independent import emails
from ..core.independent import public
from ..core.independent import compatible
# =================================
# 日志记录
import logging
logger = logging.getLogger('main.db_filter')
# =================================

# 判断一段文字是否只包含英文符号
def is_english(content):
    logger.debug('程序到达：db_filter.py-is_english函数')
    if not content:
        return False
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
    en_alphabet = 'abcdefghijklmnopqrstuvwxyz'
    # 英文符号
    en_symbol = "/'-. ,*?{}()[]<>&^$@+%\\|~!;:-_"
    # 数字
    integer_symbol = '1234567890'
    permitted_text = en_symbol + en_alphabet + integer_symbol
    for alphabet in content:
        if alphabet.lower() not in permitted_text:
            return False
    return True



# 过滤函数(filter_func)举例
# 设置过滤规则，要求传入正则表达式的匹配模式字符串
# 返回：True or False
# 正则举例：
# ^cover(\S*(?!.* )\S*)  匹配以cover开头，然后是字符，然后不能包含空格的内容，然后是一些字符；
# ^(?!.*hello)  匹配不含hello的字符
def is_match(word, pattern):
    logger.debug('程序到达：db_filter.py-is_match函数')
    pattern = re.compile(pattern)
    if pattern.match(word):
        return True
    return False


# 过滤符合添加的单词，打印出打印出其原文和译文
@public.retry_decorator(prompt='匹配模式错误，请检查后重试', retry=5)
def filter_translation(enabled, filter_func=None):
    logger.debug('程序到达：db_filter.py-filter_translation函数')
    if enabled not in ['*f', '*filter']:
        return None
    logger.debug('进入过滤单词函数')
    if filter_func is None:
        filter_func = is_match
    while True:
        datas = db_word.collect_dicts_iterator(db='public')
        pattern = collect.get_input('请输入匹配模式(退出*，全局退出**)：')
        if pattern == '*':
            logger.info('退出过滤函数')
            return None
        elif pattern == '**':
            logger.info('全局退出')
            public.exit_program(prompt='已退出！')
        elif pattern in ['.*?', '.*', '']:
            logger.info('被禁止的匹配模式：{}'.format(pattern))
            print('不允许匹配模式为:{}'.format(pattern))
            continue
        logger.info('匹配模式：{}'.format(pattern))
        count = 0
        # 防止打印的数据重复(因为之前没有处理末尾空格)
        words_container = set()
        # 匹配译文中文
        if not is_english(pattern):
            logger.info('中文匹配模式：{}'.format(pattern))
            for data in datas:
                word = data[0].strip()
                if word in words_container:
                    continue
                translation_str = compatible.SPACE.join(data[1][1][1])
                if pattern in translation_str:
                    print(compatible.colorize(text=word, color='green'), end='  ')
                    print(compatible.colorize(text=translation_str, color='yellow'))
                    # 打印过的不再打印
                    words_container.add(word)
                    count += 1
        # 匹配英文单词
        else:
            logger.info('英文匹配模式：{}'.format(pattern))
            for data in datas:
                word = data[0].strip()
                if word in words_container:
                    continue
                if filter_func(word, pattern):
                    #soundmark = data[1][1][0]
                    translation = data[1][1][1]
                    print(compatible.colorize(text=word, color='green'), end='  ')
                    print(compatible.colorize(text=compatible.SPACE.join(translation), color='yellow'))
                    # 打印过的不再打印
                    words_container.add(word)
                    count += 1
        print('本次共有{}个匹配结果'.format(count))
        print('-'*45)

