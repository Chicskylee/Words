# coding=utf-8
# =================================
# 作者声明：
# 文件用途：重要路径设置
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 其他依赖：无
# 编写时间：2018-07-08 11:37
# =================================
import os
import sys
import time
import datetime
import functools
# ---------------------------------
from . import public
# =================================
# 日志记录
import logging
logger = logging.getLogger('main.path')
# =================================

# 用于给其他模块调用，以避免多次导入os的函数

# 包装os.remove()
def os_remove(filename):
    logger.debug('程序到达：path.py-os_remove函数')
    os.remove(filename)
    logger.info('程序删除了文件：{}'.format(filename))


# 包装os.path.exists()
def path_exist(filename):
    logger.debug('程序到达：path.py-path_exist函数')
    if os.path.exists(filename):
        return True
    return False


# 包装os.path.basename()
def get_basename(filename):
    logger.debug('程序到达：path.py-get_basename函数')
    return os.path.basename(filename)

# =================================
# 用于创建路径的辅助函数

# 获取时间字符串
def _get_strftime(format='%y-%m-%d %H:%M:%S'):
    logger.debug('程序到达：path.py-_get_strftime函数')
    return time.strftime(format)


# 获取精确时间字符串
def _get_detail_strftime():
    logger.debug('程序到达：path.py-_get_detail_strftime函数')
    return str(datetime.datetime.now())


# 获取纯数字的20位的精确时间字符串
def _get_detail_time_now():
    logger.debug('程序到达：path.py-_get_detail_time_now函数')
    detail_time = str(datetime.datetime.now())
    # 去除不需要的符号，设置替换表，并完成替换
    table = '*'.maketrans({sub:None for sub in '-: .'})
    detail_time = detail_time.translate(table)
    # 不足20位，用0补齐
    return '{:<020s}'.format(detail_time)


# 判断content是否是用于设置path合法的字符串
# 返回：False，当content含有中文、句子过长时
# 返回：True，当content只含有英文，或是词组时
def valid_content(content):
    logger.debug('程序到达：path.py-valid_content函数')
    if len(content) > 50:
        logger.info('原文过长，禁止创建数据库！')
        return False
    elif not public.is_english(content):
        logger.info('原文中含有中文，禁止创建数据库！')
        return False
    return True


# 合法的开头英文字符列表
def get_valid_initial():
    logger.debug('程序到达：path.py-get_valid_initial函数')
    alphabets = 'abcdefghijklmnopqrstuvwxyz'
    numbers = '0123456789'
    # 符号中，仅英文下划线可以作为合法字符
    symbols = '_'
    return alphabets + numbers + symbols


# 获取一段字符的首字符小写
def get_initial(content):
    logger.debug('程序到达：path.py-get_initial函数')
    # 去除两端空白符，并将内容变小写
    content = content.strip().lower()
    initial = content[0]
    if initial not in get_valid_initial():
        initial = '_'
    return initial


# 获取单词前两个字母
def get_initial2(content):
    logger.debug('程序到达：path.py-get_initial2函数')
    content = content.strip().lower()
    initial2 = content[:2]
    # 不足两位的数字用0补齐，单词用a补齐
    if len(initial2) == 1:
        # 判断initial2是否全是数字
        if initial2.isdecimal():
            initial2 = '{}0'.format(initial2)
        else:
            initial2 = '{}a'.format(initial2)
    # 有非法符号的用下划线占位取代
    valid_initial = get_valid_initial()
    if initial2[0] not in valid_initial:
        initial2 = '_{}'.format(initial2[1])
    if initial2[1] not in valid_initial:
        initial2 = '{}_'.format(initial2[0])
    return initial2

# =================================
# 自带数据路径


# 检查路径是否存在，如果不存在，则创建后再返回该路径，否则直接返回
def create_path(func, count=set()):
    logger.debug('程序到达：path.py-create_path函数')
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


# 获取当前目录的上层目录
def get_path(p=__file__, n=1):
    logger.debug('程序到达：path.py-get_path函数')
    p = os.path.abspath(p)
    for _ in range(n):
        p = os.path.dirname(p)
    return p


# 连接路径，然后检查该路径的存在性，创建路径
# default：路径，如果该路径存在则用该路径代替结果路径
# exist=True：检查路径存在性，不存在则退出
# 注意：由于增加了装饰器，将在最后创建返回的路径(单层)
@create_path
def path_init(dirpath, basepath,
              default=None, exist=False):
    logger.debug('程序到达：path.py-path_init函数')
    if default and path_exist(default):
         return default
    path = os.path.join(dirpath, basepath)
    if exist and not os.path.exists(path):
        logger.fatal('不存在路径：{}'.format(path), exc_info=True)
        print('已退出：不存在路径{}'.format(path))
        sys.exit()
    return path

# =================================


# 必存在路径应该设置path_init的参数exist=True
class OriginPath(object):
    def __init__(self):
        self.root = get_path(n=5)
        self.app = get_path(n=4)
        self.packages = path_init(self.app, 'packages',  exist=True)
        self.core = path_init(self.packages, 'core',  exist=True)
        self.independent = path_init(self.core, 'independent', exist=True)


# 所有的文件皆要用函数写成
class OwnPath(OriginPath):
    def __init__(self):
        OriginPath.__init__(self)
        # 自带的数据目录
        self.own = path_init(self.app, 'own')
        # 配置文件路径
        self.conf = path_init(self.own, 'conf')
        # 日志目录
        self.log = path_init(self.own, 'log')
        # 输入数据目录
        self.i = path_init(self.log, 'input')
        # 调试数据目录
        self.d = path_init(self.log, 'log')
        # 音频目录
        self.mp3 = path_init(self.own, 'mp3')
        # 公共单词数据库目录
        self.public = path_init(self.own, 'PUBLIC')
        # 公共音频数据库外层目录
        self.audios = path_init(self.own, 'audios',
                    default='/storage/emulated/0/_audios')


    # 开发者配置数据文件
    def author_filename(self):
        return os.path.join(self.conf, '.author.conf')

    # 用于记录用户名、邮箱，及创建时间等
    def init_filename(self):
        return os.path.join(self.conf, '.init.conf')

    # 配置文件
    def config_filename(self):
        return os.path.join(self.conf, '.config.conf')

    # 公共音频数据库目录：'~/Words/data/audios/[a-z0-9]'
    # 禁止为中文、长英文句子创建数据库文件
    def audio(self, content):
        if not valid_content(content):
            logger.info('禁止为中文、长英文句子创建音频文件夹，返回None')
            return None
        subdir = get_initial(content)
        return path_init(self.audios, subdir)

    # 调试文件
    def debug_filename(self):
        now_time = _get_strftime(format=('%Y%m%d'))
        log_name = '{}.log'.format(now_time)
        return os.path.join(self.d, log_name)

    # 翻译失败单词记录文件
    def debug_translate_failed_filename(self):
        name = 'translate_failed_words.log'
        return os.path.join(self.d, name)

    # 输入数据文件
    def input_filename(self):
        now_time = _get_strftime(format=('%Y%m'))
        input_name = '{}.log'.format(now_time)
        return os.path.join(self.i, input_name)

    # 音频数据库文件，如果首字母不合法，将返回None
    def audio_filename(self, content):
        audio_path = self.audio(content)
        if audio_path is None:
            logger.info('文件路径返回的是None，因此不创建音频文件夹')
            return None
        # 获取单词前两个字母
        initial2 = get_initial2(content)
        if initial2[0] not in get_valid_initial():
            return None
        if initial2[1] not in get_valid_initial():
            return None
        # 音频数据库名称
        name = '{}_pickle'.format(initial2)
        # 音频数据库文件名路径
        return os.path.join(audio_path, name)

    # 音频文件
    def mp3_filename(self):
        detail_time = _get_detail_time_now()
        name = '{}_mp3'.format(detail_time)
        return os.path.join(self.mp3, name)

    # 音频删除失败记录文件
    def del_mp3_record_filename(self):
        return os.path.join(self.mp3, 'del_record.rcd')

    # 综合数据库文件
    # 禁止为中文、长英文句子创建数据库文件
    # initial：指单词的首字母小写
    # 返回：'~/Words/data/_word/PUBLIC/dict_(initial).pk'
    # 返回：None，当不允许创建路径时返回None
    def public_filename(self, content):
        if not valid_content(content):
            return None
        initial = get_initial(content)
        name = 'dict_{}.pk'.format(initial)
        return os.path.join(self.public, name)


class UserPath(OriginPath):
    def __init__(self):
        OriginPath.__init__(self)
        # 用户的数据目录
        self.user = path_init(self.app, 'data')
        # html路径
        self.html = path_init(self.user, 'html')
        # 单词库外层路径
        self.words = path_init(self.user, 'words')
        # 备份路径
        self.backup = path_init(self.user, 'backup',
                       default='/sdcard/__temp__')
        # 单词导出路径
        self.user_export = path_init(self.user, 'export',
                       default='/sdcard/_user/export')
        # 单词导入路径
        self.user_import = path_init(self.user, 'import',
                       default='/sdcard/_user/import')
        # 用于合并音频的总音频库，默认与 self.audios 相同
        self.public_audios_path = '/storage/emulated/0/_audios'
        # 用于合并音频的私音频库，里面的音频将会合并到总音频库
        self.private_audios_path = '/storage/emulated/0/__temp__/audios'
        # 配置路径
        self.conf = path_init(self.user, 'conf')

    # 单词库路径：'~/Words/data/words/(DATABASE_NAME)'
    def word(self, DATABASE_NAME):
        return path_init(self.words, DATABASE_NAME)

    # 用户数据库文件：'~/Words/data/words/(DATABASE_NAME)/dict_(initial).pk'
    # 禁止为中文、长英文句子创建数据库文件
    # 返回：None，不允许创建路径时
    def word_filename(self, content, DATABASE_NAME):
        if not valid_content(content):
            return None
        initial = get_initial(content)
        name = 'dict_{}.pk'.format(initial)
        return  os.path.join(self.word(DATABASE_NAME), name)

    # html文件
    def html_filename(self, name):
        html_name = '{}_html'.format(name)
        return os.path.join(self.html, html_name)

    # 导出文件：'~/Words/data/export/(DATABASE_NAME).txt'
    def export_filename(self, DATABASE_NAME):
        name = '{}.txt'.format(DATABASE_NAME)
        return os.path.join(self.export, name)

    # 构造音频数据库文件名路径，仅用于合并音频到总音频库
    def get_audios_filename(self, path, initial, initial2):
        name = '{}{}_pickle'.format(initial, initial2)
        return os.path.join(path, initial, name)

    # 特定格式的导出词库文件
    # '~/Words/data/export/(DATABASE_NAME)_(date).txt'
    def export_fmt_filename(self, DATABASE_NAME, fmt='txt'):
        date = _get_strftime(format='%y%m%d%H%M%S')
        name = '{}_{}.{}'.format(DATABASE_NAME, date, fmt)
        return os.path.join(self.user_export, name)

    # 备份文件：'~/Words/data/backup/words_180725.zip'
    # 注意：调用时检查存在性，留意自动覆盖
    def zip_filename(self, DATABASE_NAME):
        now_time = time.strftime('%y%m%d')
        zip_name = '{}_{}.zip'.format(DATABASE_NAME, now_time)
        return os.path.join(self.backup, zip_name)

# =================================
origin = OriginPath()
own = OwnPath()
user = UserPath()

