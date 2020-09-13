# coding=utf-8
# =================================
# 作者声明：
# 文件用途：将数据导入数据库
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 其他依赖：无
# =================================
import os
# ---------------------------------
# 从顶层文件执行本脚本使用
from . import db_word
from . import translate
# ---------------------------------
# 从顶层文件执行本脚本使用
from ..core import log
from ..core import config
from ..core import collect
from ..core.independent import path
from ..core.independent import public
# =================================
# 日志记录
import logging
logger = logging.getLogger('main.db_import')
# =================================

# 查单词，并将查找的译文写入数据库
def automatic_lookup_content(content, db_dict_private, db_dict_public):
    logger.debug('程序到达：db_import.py-automatic_lookup_content函数')
    logger.info('content:{}'.format(content))
    # 从数据库中获取翻译内容
    # 首先进入当前数据库尝试获取译文
    translation_list = db_word.get_translation_from_dict(content, db_dict_private)
    if translation_list is not None:
        db_word.print_to_user(content, translation_list)
    # 未获取译文，则尝试从综合数据库中进行查询
    else:
        translation_list = db_word.get_translation_from_dict(content, db_dict_public)
        # 查询到了译文，将单词从综合数据库拷贝到当前数据库
        if translation_list is not None:
            db_word.add_content(content, translation_list[1], db='private')
            db_word.print_to_user(content, translation_list)
        # 如果综合数据库也没有查询到译文，则用爬虫获取译文
        else:
            translation = translate.get_translation(content)
            if translation is None:
                logger.info('爬虫没有获取译文，原单词：{}'.format(content))
                # 将这个单词记录下来
                log.record_translate_failed(content, add_time=False)
                return None
            # 将爬取的数据打印给用户
            db_word.print_to_user(content, translation)
            # 如果翻译不存在，不再进行接下来的行为
            if isinstance(translation, list):
                # 翻译不存在时translation：['', False]
                if not translation[0] and not translation[1]:
                    logger.info('翻译不存在，不再执行音频获取等操作')
                    log.record_translate_failed(content, add_time=True)
                    return None
                # 爬取到译文内容后，要保存在当前数据库中
                db_word.add_content(content, translation, db='private')


# =================================


@public.timeit
def main(enabled):
    logger.debug('程序到达logger.debug('程序到达：db_import.py-main函数')
    if enabled not in ['*i', '*import']:
        return None
    # 第零步、确认是否将单词自动汇入当前数据库中
    database_name = config.get_database_name()
    choice = collect.get_input(prompt='即将把单词汇入数据库{}中(确认*)：'.format(database_name))
    if choice != '*':
        public.exit_program(prompt='已退出！')
    # 第一步、获取需要导入的单词列表
    words = set()
    # 获取文件名列表
    names = os.listdir(path.user.user_import)
    for name in names:
        filename = os.path.join(path.user.user_import, name)
        current_words = public.read(filename).split('\n')
        for word in current_words:
            if word:
                words.add(word)
    words = sorted(list(words))
    # 第二步、将单词依次写入数据库(自动查找)
    words_total = len(words)
    if words_total == 0:
        input('请将需导入的单词表放在{}目录下：'.format(path.user.user_import))
        return None
    collect.get_input(prompt='本次将汇入单词数{}(确认*)：'.format(words_total))
    db_dict_private = db_word.collect_dicts(db='private')
    db_dict_public = db_word.collect_dicts(db='public')
    for index, word in enumerate(words, start=1):
        print(words_total-index, word, end=' ')
        automatic_lookup_content(word, db_dict_private, db_dict_public)
    collect.get_input(prompt='自动单词导入程序结束，本次共导入单词量{}(Enter)：'.format(words_total))



