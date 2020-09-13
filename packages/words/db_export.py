# coding=utf-8
# =================================
# 作者声明：
# 文件用途：将数据导出到TXT、CSV、Excel
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 其他依赖：无
# =================================
import re
# ---------------------------------
# 从顶层文件执行本脚本使用
from . import db_word
# ---------------------------------
# 从顶层文件执行本脚本使用
from ..core import config
from ..core import collect
from ..core.independent import path
from ..core.independent import public
from ..core.independent import compatible
# =================================
# 日志记录
import logging
logger = logging.getLogger('main.export')
# =================================

# 去除末尾的翻译成的人名译文内容
# 如果译文列表(obj)中的某个元素是翻译成的人名，
# 那么返回去掉这一部分的新列表
# 注意：这种翻译成人名的译文只在最后一个元素中出现
# 注意：该函数被print_dict(obj)调用
def strip_person_name(obj):
    logger.info('程序到达：db_export.py-strip_person_name函数')
    if all(i in obj[-1] for i in ['n.', '人名']):
        return obj[:-1]  # 去除obj[-1]
    else:
        return obj


# 对总单词字典obj进行排序
# 第一排序依据：查单词次数
# 第二排序依据：日期
def print_dict(obj):
    logger.info('程序到达：db_export.py-print_dict函数')
    # obj[key][0]是专门用来排序的依据列表
    sort_dict = {key:obj[key][0] for key in obj}
    # 排序依据，其中日期前的负号是为了排序而附加的
    sort_list = sorted(((times, -detail_time, content) for (content, (times, detail_time)) in sort_dict.items()), reverse=True)
    print_obj = dict()
    for key in obj.keys():
        if public.is_phrase(key):
            # 注意：obj[key][1][0]是一个字符串，表示音标
            # 注意：obj[key][1][1]是一个列表，表示译文
            # 如果是词组那么加分号输出
            # 注意：返回的内容之间以两个空格分隔，
            # 注意：这两个用作分隔的空格，将在后续直接影响rewords.py程序的处理方式！！！
            print_obj[key] = obj[key][1][0] + '  '+'；'.join(obj[key][1][1])
        else:
            # 如果不是词组，那么正常输出
            translation_list = obj[key][1][1]  # 译文列表
            translation_list = strip_person_name(translation_list)  # 去除部分内容后的译文列表
            print_obj[key] = obj[key][1][0] + '  '+' '.join(translation_list)
    # 不显示(不写入用户查看的单词本)的单词集合
    words_del = {'1', '2', }
    for item in sort_list:
        # item是一个元组，形式为(查询次数, -日期, '原文')，日期前的负号是为了排序而附加的
        # item形式举例：(3, -20170807165653, 'hello')
        if item[2] in words_del:
            # 当该单词在用户不显示单词集合中时，跳过该单词，不再写入用户背诵的单词本中
            continue
        else:
            # 注意：返回的内容之间以两个空格分隔，
            # 注意：这两个用作分隔的空格，将在后续直接影响user_rewords.py程序的处理方式！！！
            yield "[%02d]  %s  %s\n" % (item[0], item[2], print_obj[item[2]])



# 提取不同的单词内容
def get_extract_datas(frequency=False, date=False,
	       word=False, soundmark=False, translation=False,
	       sort_by_frequency=False, sort_by_alphabet=False,
	       sort_by_date=False):
    logger.info('程序到达：db_export.py-get_extract_datas函数')
    db_dict = db_word.collect_dicts(db='private')
    db_items = db_dict.items()
    if sort_by_alphabet:
	# 根据首字母排序
	logger.debug('使用单词首字母进行排序')
	db_items = sorted(db_items, key=lambda item:item[0])
    elif sort_by_frequency:
	# 根据词频排序
	logger.debug('使用单词频率进行排序')
	db_items = sorted(db_items, key=lambda item:item[1][0][0], reverse=True)
    elif sort_by_date:
	# 根据日期排序
	logger.debug('使用日期进行排序')
	db_items = sorted(db_items, key=lambda item:item[1][0][1], reverse=True)
    else:
        logger.info('排序参数传入异常！')
    lines = list()
    for w, ((f, date), (s, ts)) in db_items:
	line = list()
	if frequency:
	    line.append('[{:02d}]'.format(f))
	if word:
	    line.append(w)
	if soundmark:
	    line.append(s)
	if translation:
            logger.debug(ts)
            # 去除译文中的人民译文
            ts = strip_person_name(ts)
            logger.debug(ts)
            line.append(' '.join(ts))
	if line:
	    lines.append(line)
    return lines



# 导出到TXT文件中
def export_txt(extract_datas):
    logger.info('程序到达：db_export.py-export_txt函数')
    if not extract_datas:
        print('没有需要导出的内容')
        return False
    database_name = config.get_database_name()
    filename = path.user.export_fmt_filename(database_name, fmt='txt')
    with open(filename, 'wb') as f:
        for index, line in enumerate(extract_datas, start=1):
            new_line = (' '*2).join(line) + '\n'
            f.write(new_line.encode('utf-8'))
    print('导出完毕，总数：{}'.format(index))
    print('导出路径：{}'.format(filename))
    collect.get_input(prompt='请按任意键退出导出程序：')


# 导出数据库中的单词
# enabled：仅当其值为'*e'或'*export'时被激活
# index=2，导出所有(含词频)
# index=3，仅导出单词
# index=4，仅导出音标
# index=5，仅导出译文
# index=6，导出单词、音标和译文
# index=7，导出单词和音标
# index=8，导出音标和译文
# 返回：None，用户主动进入本函数后退出
# 返回：False，用户非主动进入本函数后自动退出
def export_datas(enabled, debug=False):
    logger.info('程序到达：db_export.py-export_datas函数')
    compatible.clear_screen(debug=debug)
    if enabled not in ['*e', '*export']:
        return False
    print('='*45)
    print('{}可选导出项目'.format(' '*16))
    print('-'*45)
    print('[退出]:0{}[返回上级]:1{}所有(含词频):2'.format(' '*6, ' '*5))
    print('仅单词:3{}仅音标:4{}仅译文:5'.format(' '*6, ' '*9))
    print('所有内容:6{}单词和音标:7{}音标和译文:8'.format(' '*4, ' '*5))
    print('='*45)
    index = collect.get_input('请选择序号：')
    try:
        index = int(index.strip())
    except:
        index = -1
    logger.debug('用户选择了：{}'.format(index))
    if (index < 0) or (index > 8):
        collect.get_input('输入的序号不存在，任意键退出：')
        return None
    elif (index == 0) or (index == 1):
        # 返回上一级或退出
        return None
    # 设置导出时的排序依据
    sort_by = collect.get_input('以词频(Enter)，首字母(1)，日期(2)排序：')
    try:
        sort_by = int(sort_by.strip())
        if (sort_by < 0) or (sort_by > 2):
            sort_by = 0
    except Exception as e:
        logger.info('选择排序依据异常：{}'.format(e), exc_info=True)
        sort_by = 0
    # 前面已经处理过0,1和非法索引了，这里从2开始
    if index in range(2, 9):
        kwargs = {'date':False,
            'frequency':True if index in [2, ] else False,
            'word':True if index in [2, 3, 6, 7, ] else False,
            'soundmark':True if index in [2, 4, 6, 7, 8, ] else False,
            'translation':True if index in [2, 5, 6, 8, ] else False,
            'sort_by_frequency':True if sort_by==0 else False,
            'sort_by_alphabet':True if sort_by==1 else False,
            'sort_by_date':True if sort_by==2 else False,}
        extract_datas = get_extract_datas(**kwargs)
        export_txt(extract_datas)
    else:
        raise IndexError('程序不应该到达这里！')
        logger.info('程序本不应该到达这里！')
    return None
