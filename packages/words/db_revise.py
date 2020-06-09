# coding=utf-8
# =================================
# 作者声明：
# 文件用途：
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 其他依赖：无
# =================================
import time
# ---------------------------------
# 从顶层文件执行本脚本使用
from . import db_word
from . import db_audio
from . import db_export
# ---------------------------------
# 从顶层文件执行本脚本使用
from ..core.independent import compatible
# =================================
# 日志记录
import logging
logger = logging.getLogger('main.db_revise')
# =================================

# 获取当前数据库中的 词频 和 单词
def get_words_list():
    db_dict = db_word.collect_dicts(db='private')
    db_items = db_dict.items()
    # 根据词频排序
    db_items = sorted(db_items, key=lambda item:item[1][0][0], reverse=True)
    words_list = list()
    for w, ((f, date), (s, ts)) in db_items:
        words_list.append((f, w, s, ts))
    return words_list


def main(enabled):
    if enabled not in ['*r', '*revise']:
        return None
    # 第一步、获取当前词库中的纯单词
    words_list = get_words_list()
    # 第二步、依次查找并播放每个单词
    for (frequency, content, soundmark, translation) in words_list:
        print('-'*45)
        # 给每个元素上色
        frequency = '[{:02d}]'.format(frequency)
        word = compatible.colorize(content, color='yellow')
        word_detail = '{} {}  '.format(frequency, word)
        print(word_detail, end='')
        # 播放音频
        db_audio.audio_play(content)
        soundmark = compatible.colorize(soundmark, color='default')
        translation = db_export.strip_person_name(translation)
        translation = compatible.colorize(' '.join(translation), color='default')
        words_translation = '{} {}'.format(soundmark, translation)
        print(words_translation)
        time.sleep(2)


