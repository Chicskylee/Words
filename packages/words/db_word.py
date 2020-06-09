# coding=utf-8
# =================================
# 作者声明：
# 文件用途：处理单词及其译文数据
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 其他依赖：无
# =================================
# ---------------------------------
# 从顶层文件执行本脚本使用
from ..core import config
from ..core.independent import path
from ..core.independent import public
from ..core.independent import compatible
# =================================
# 日志记录
import logging
logger = logging.getLogger('main.db_word')
# =================================

# obj的结构：[['次数','时间'], ['音标', ['译文']]]
# 打印给用户查看的内容音标(字符串)和译文(列表)
# 注意：这里的obj是一个列表，表示给用户查看的音标和翻译
def print_to_user(content, obj):
    logger.debug('进入给用户打印译文的函数')
    logger.debug('obj:{}'.format(obj))
    if (not obj[0]) and (not obj[1]):
        public.my_print('译文不存在')
        return None
    if isinstance(obj[0], str):
        # 这里的obj结构为['音标', ["译文"]]
        if public.is_english(content):
            if public.is_phrase(content):
                # 词语的译文之间加上分号隔开
                # 由于有道词典接口给出的长短语的不同意思之间没有用分号隔开，因此添加该代码
                public.my_print('{}{}{}'.format(obj[0], compatible.SPACE*2, ';'.join(obj[1])))         	
            else:
                # 单词的译文之间用空格隔开
                public.my_print('{}{}{}'.format(obj[0], compatible.SPACE*2, compatible.SPACE.join(obj[1])))
        else:
            # 中文的译文之间用分号隔开
            if isinstance(obj[1], str) and len(obj)==2:
                public.my_print('{}{}{}'.format(obj[0], compatible.SPACE*2, obj[1]))
            else:
                public.my_print('{}{}{}'.format(obj[0], compatible.SPACE*2, ';'.join(obj[1])))
        return True
    elif isinstance(obj[0], list):
        # obj结构为[['次数','时间'], ['音标', ['译文']]]
        if public.is_english(content):
            if public.is_phrase(content):
                # 词语的译文之间加上分号隔开
                public.my_print('{}{}{}'.format(obj[1][0], compatible.SPACE*2, ';'.join(obj[1][1])))
            else:
                # 单词的译文之间用空格隔开
                public.my_print('{}{}{}'.format(obj[1][0], compatible.SPACE*2, compatible.SPACE.join(obj[1][1])))
        else:
            # 中文的译文之间用分号隔开
            public.my_print('{}{}{}'.format(obj[0], compatible.SPACE*2, ';'.join(obj[1])))
        return True
    else:
        raise TypeError("异常，给定的对象不是列表！")

# =================================
# 不区分综合数据库和用户数据库的函数

# 检查一个单词是否为单词或词组
def is_word_or_phrase(content):
    word = word.lower()
    # 定义合法符号
    symbols = "abcdefghijklmnopqrstuvwxyz/'-. ,1234567890"
    for s in word:
        if s not in symbols:
            return False
    else:
        return True


# content：要查找翻译和音标的单词或词组
# 根据单词从综合数据库中获取音标和译文
# 返回形式1：['音标', ['译文1','译文2']]
# 返回形式2：None，表示所查单词在综合数据库中不存在
def get_translation_from_dict(content, db_dict):
    # 由于本程序不保存中文翻译，故直接返回省得浪费时间
    if not public.is_english(content):
        return None
    translation = db_dict.get(content, None)
    return translation


# 判断单词是否在字典中，如果存在，返回结果True
def content_in_dict(content, db_dict):
    if not db_dict:
        return False
    if content in db_dict:
        return True
    else:
        return False

# =================================
# 根据传参变化决定操作什么数据库的函数


# 将字典写入数据库
# 注意：db='private'时代表写入用户当前数据库
# 注意：db='public'时代表写入综合数据库
def write_db_dict(db_dict, content, db):
    if db == 'private':
        database_name = config.get_database_name()
        f = path.user.word_filename(content, database_name)
        logger.debug('写入路径：{}'.format(f))
    elif db == 'public':
        f = path.own.public_filename(content)
        logger.info('写入路径：{}'.format(f))
    else:
        raise ValueError('数据库指定错误')
    try:
        public.write_pickle(db_dict, f)
    except TypeError:
        return False
    return True


# 读取数据库(字典)，并返回字典内容
# 返回：字典
# 注意：db='private'时代表读取用户当前数据库
# 注意：db='public'时代表读取综合数据库
def read_db_dict(content, db):
    if db == 'private':
        database_name = config.get_database_name()
        f = path.user.word_filename(content, database_name)
        logger.debug('读取路径：{}'.format(f))
    elif db == 'public':
        f = path.own.public_filename(content)
        logger.debug('读取路径：{}'.format(f))
    else:
        logger.warning('只能传入参数private或public，即将主动抛出异常')
        raise ValueError('数据库指定错误')
    if f is None:
        logger.info('数据库路径不存在，不进行读取，返回空字典{}')
        return dict()
    # 检查文件的存在性
    if not path.path_exist(f):
        logger.info('文件路径不是None，但数据库文件不存在，即将创建：{}'.format(f))
        public.write_pickle(dict(), f)
    return public.read_pickle(f)


# 收集所有单词到一个字典中
# 返回：字典
# 注意：db='private'时代表 读取 用户当前数据库
# 注意：db='public'时代表 读取 综合数据库
def collect_dicts(db):
    all_dict = dict()
    for initial in [chr(i) for i in range(97,123)]:
        words_dict = read_db_dict(initial, db)
        if words_dict is not None:
            all_dict.update(words_dict)
    return all_dict


# 每次返回一条单词数据，直到返回所有单词数据
# 返回：迭代器
# 注意：db='private'时代表 读取 用户当前数据库
# 注意：db='public'时代表 读取 综合数据库
def collect_dicts_iterator(db):
    for initial in [chr(i) for i in range(97,123)]:
        words_dict = read_db_dict(initial, db)
        if words_dict is not None:
            for data in words_dict.items():
                yield data


# 获取单词数量
# 返回：整数
# 注意：db='private'时代表 获取 用户当前数据库单词量
# 注意：db='public'时代表 获取 综合数据库单词量
def get_words_total(db):
    words_total = 0
    for initial in [chr(i) for i in range(97,123)]:
        words_dict = read_db_dict(initial, db)
        if words_dict:
            words_total += len(words_dict)
    return words_total


# 增加单词翻译
# 注意：需要手动将已经存在的错误翻译结果删除再添加
# 注意：db='private'时代表 操作 用户当前数据库
# 注意：db='public'时代表 操作 综合数据库
# 返回：添加成功的标志True或False
# 注意：该函数目前不要用，因为最好不要允许用户修改音标
def add_content(content, translation, db):
    # 译文的正确性检查
    if translation[-1] == False:
        return False
    db_dict = read_db_dict(content, db)
    # 已经存在单词，直接返回(需要手动删除该单词)
    if content_in_dict(content, db_dict):
        logger.info('当前数据库已经存在单词：{}，直接返回'.format(content))
        return False
    # 确定不存在该单词，添加
    db_dict[content] = [[1, int(public.get_strftime("%Y%m%d%H%M%S"))], translation]  # 添加一条数据
    write_db_dict(db_dict, content, db)
    logger.debug('已写入{}的数据'.format(content))
    return True


# 将单词本(字典)中已经存在的单词计数增加(或减少)1
# 返回：操作结果True或False
# 注意：db='private'时代表 操作 用户当前数据库
# 注意：db='public'时代表 操作 综合数据库
def change_content_count(content, db, operate='+'):
    db_dict = read_db_dict(content, db)
    # 字典为空，直接返回
    if not db_dict: return False
    # 不存在单词，直接返回
    if not content_in_dict(content, db_dict): return False
    # 确定存在该单词，则变更计数次数
    if operate == '+':
        db_dict[content][0][0] += 1
    elif operate == '-':
        db_dict[content][0][0] -= 1
        if db_dict[content][0][0] <1:
            db_dict[content][0][0] = 1
    # 更新时间标识
    db_dict[content][0][1] = int(public.get_strftime("%Y%m%d%H%M%S"))
    logger.info('修改单词{}计数为：{}'.format(content, db_dict[content][0][0]))
    write_db_dict(db_dict, content, db)
    return True


# 从单词库中删除一个单词
# 返回：执行结果删除成功True，删除失败False
# 注意：db='private'时代表 操作 用户当前数据库
# 注意：db='public'时代表 操作 综合数据库
def delete_content_from_dict(content, db):
    db_dict = read_db_dict(content, db)
    # 字典为空，直接返回
    if not db_dict: return False
    # 不存在单词，直接返回
    if not content_in_dict(content, db_dict):
        print('不存在单词：{}'.format(content))
        return False
    # 确定存在该单词，则尝试删除
    db_dict.pop(content)
    write_db_dict(db_dict, content, db)
    logger.info('单词{}的数据已被删除'.format(content))
    return True


# 数据库中导出所有纯单词到txt文件
# 注意：db='private'时代表 操作 用户当前数据库
# 注意：db='public'时代表 操作 综合数据库
@public.timeit
def export_pure_content_to_txt(db):
    database_name = config.get_database_name()
    filename = path.user_path.export_fmt_filename(database_name, fmt='txt')
    with open(filename, 'wb') as f:
            count = 0
            for initial in [chr(i) for i in range(97,123)]:
                db_dict = read_db_dict(initial, db)
                # 字典为空，直接跳过
                if not db_dict: continue
                content_list = sorted(db_dict)
                for content in content_list:
                    line = (content+'\n').encode('utf-8')
                    f.write(line)
                    print(word)
                    count += 1
    print('{}导出完毕，位置：\n{}'.format(database_name, filename))
    print('本次共导出单词数：{}'.format(count_words))
    return filename



# =================================
# 用户数据库与综合数据库的交互

# 检查两个字典中存在的差异
# 函数需要检查出哪部分是增加和减少的键值对，哪部分是值被修改的
def dict_difference(dict1, dict2):
    print('不同内容不同：')
    # 新增
    # 减少
    # 变更值
    pass

# 合并当前用户的单词库到综合数据库
# 不需要传入参数
def _add_user_words_to_public_db():
    # 汇总以initial开头的词库
    # 当 check=True 时，并未真正汇总
    def summary_db(initial, check=True):
        # 这两个都是字典
        public = read_db_dict(initial, db='public')
        user = read_db_dict(initial, db='private')
        # 用户词库总量，合并前综合词库总量
        len_user, len_public = len(user), len(public)
        # 将用户数据并入到综合词库
        public.update(user)
        # 合并后综合词库总量：
        len_public_changed = len(public)
        # 综合词库改变量：
        len_change = len_public_changed - len_public
        # 只有数据有所增加时才写入综合词库
        if len_public_changed > len_public:
            if not check:
                write_db_dict(public, initial, db='public')
            else:
                dict_difference(public, user)
        return (initial, len_user, len_public, len_public_changed, len_change)

    # 开始汇总到公共词库
    total_change = 0
    initials = 'abcdefghijklmnopqrstuvwxyz'
    print('='*42)
    print('词库  用户库  公共库  汇总后公共库  改变量')
    for initial in initials:
        print(' 正在汇总：{}'.format(initial), end='\r')
        result = summary_db(initial, check=False)
        print('{:4s}  {:6d}  {:6d}  {:12d}  {:6d}'.format(*result))
        total_change += result[4]
    print('-'*42)
    print('改变量合计  {:30d}'.format(total_change))
    print('='*42)
    print('汇总结束！')

