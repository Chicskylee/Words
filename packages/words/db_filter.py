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

# 过滤函数(filter_func)举例
# 设置过滤规则，要求传入正则表达式的匹配模式字符串
# 返回：True or False
# 正则举例：
# ^cover(\S*(?!.* )\S*)  匹配以cover开头，然后是字符，然后不能包含空格的内容，然后是一些字符；
# ^(?!.*hello)  匹配不含hello的字符
def is_match(word, pattern):
    pattern = re.compile(pattern)
    if pattern.match(word):
        return True
    return False


# 过滤符合添加的单词，打印出打印出其原文和译文
@public.retry_decorator(prompt='匹配模式错误，请检查后重试', retry=5)
def filter_translation(enabled, filter_func=None):
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
            print('不允许匹配模式为:{!r}'.format(pattern))
            continue
        logger.info('匹配模式：{}'.format(pattern))
        count = 0
        # 防止打印的数据重复(因为之前没有处理末尾空格)
        words_container = set()
        for data in datas:
            word = data[0].strip()
            if word in words_container:
                continue
            if filter_func(word, pattern):
                #soundmark = data[1][1][0]
                translation = data[1][1][1]
                print(compatible.colorize(text=word, color='green'), end='  ')
                print(compatible.colorize(text=compatible.SPACE.join(translation), color='yellow'))
                words_container.add(word)
                count += 1
        print('本次共有{}个匹配结果'.format(count))
        print('-'*45)

