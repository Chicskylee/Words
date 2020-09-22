# coding=utf-8
# =================================
# 作者声明：
# 文件用途：
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 其他依赖：无
# =================================
import threading
# ---------------------------------
# 从顶层文件执行本脚本使用
from .words import db_audio
from .words import db_word
from .words import db_backup
from .words import db_export
from .words import db_import
from .words import db_filter
from .words import db_revise
from .words import translate
from .words import translate_expend
# ---------------------------------
# 从顶层文件执行本脚本使用
from .core import config
from .core import collect
from .core.independent import path
from .core.independent import public
from .core.independent import compatible
# =================================
# 日志记录
import logging
logger = logging.getLogger('main.manager')
# =================================

# 更新配置文件，并重新导出单词数据到TXT格式的单词本
@public.timeit
def update_config():
    logger.debug('程序到达：manager.py-update_config函数')
    logger.info('程序进入配置文件更新函数')
    print('正在更新配置文件，请稍后……')
    # 获取单词总数
    words_total = db_word.get_words_total(db='private')
    # 更新配置文件
    database_name = config.get_database_name()
    config.set_words_total(database_name, words_total=words_total)


# 根据用户输入的内容，判断是否退出程序
def judge_exit(content, prompt=None):
    logger.debug('程序到达：manager.py-judge_exit函数')
    logger.info('程序进入判定程序是否退出函数')
    if content not in ['@', ',', '，', '']:
        return None
    if prompt is None:
        prompt = '更新完成，已退出！'
    # 更新配置信息，并导出单词数据到单词本
    update_config()
    public.exit_program(prompt=prompt)


# 从数据库中获取翻译
# 存在译文，返回：译文内容
# 不存在译文，返回：None
def get_translation_from_db(content, write_flag=True):
    logger.debug('程序到达：manager.py-get_translation_from_db函数')
    logger.info('程序进入从数据库获取译文函数')
    # 首先进入当前数据库尝试获取译文
    db_dict = db_word.read_db_dict(content, db='private')
    logger.info('数据库读取数据库完毕')
    translation_list = db_word.get_translation_from_dict(content, db_dict)
    logger.info('在当前数据库获取的单词{}的译文内容：{}'.format(content, translation_list))
    logger.info('当前数据库查找译文完毕')
    if translation_list is not None:
        if write_flag:
            logger.info('根据用户输入，所查译文的查询次数将增加1')
            # 查询到了译文，则增加当前数据库中的查询次数
            db_word.change_content_count(content, db='private', operate='+')
        # 然后返回译文内容
        return translation_list
    else:
        logger.info('程序进入综合数据库获取译文函数')
        # 未获取译文，则尝试从综合数据库中进行查询
        db_dict = db_word.read_db_dict(content, db='public')
        logger.info('综合数据库读取完毕')
        translation_list = db_word.get_translation_from_dict(content, db_dict)
        logger.info('综合数据库查找译文完毕')
        if translation_list is not None:
            logger.debug('综合数据库获取的译文内容：{}'.format(translation_list))
            logger.info('在综合数据库中查询到了单词：{}'.format(content))
            # 查询到了译文，将单词从综合数据库拷贝到当前数据库
            # 并设置当前数据库中的查询次数为1
            if write_flag:
                logger.info('将译文写入个人数据库')
                db_word.add_content(content, translation_list[1], db='private')
            else:
                logger.info('译文被要求不写入个人数据库')
            return translation_list
        logger.info('程序在综合数据库没有找到译文，跳出数据库获取译文函数')
        return None


# 查单词
# 仅当write_flag=True时，查找的译文记录将写入数据库
def lookup_content(content, write_flag=True):
    logger.debug('程序到达：manager.py-lookup_content函数')
    logger.info('程序进入正常查找译文函数')
    # 从数据库中获取翻译内容
    translation_list = get_translation_from_db(content, write_flag=write_flag)
    if translation_list is not None:
        db_word.print_to_user(content, translation_list)
        # 尝试音频播放：播放中删除音频会导致异常(PermissionError)
        try:
            db_audio.audio_play(content)
        except Exception as e:
            logger.warning('音频文件使用中，无法删除，故而产生了异常，请忽略', exc_info=True)
    else:
        logger.info('程序进入爬取有道翻译译文函数')
        # 如果综合数据库也没有查询到译文，则用爬虫获取译文
        translation = translate.get_translation(content)
        logger.info('爬取到的译文内容：{}'.format(translation))
        if translation is None:
            logger.info('爬取结果是None，说明爬取失败，结束本函数')
            return None
        # 将爬取的数据打印给用户
        db_word.print_to_user(content, translation)
        # 如果翻译不存在，不再进行接下来的行为
        if isinstance(translation, list):
            # 翻译不存在时translation：['', False]
            if not translation[0] and not translation[1]:
                logger.info('翻译不存在，不再执行音频获取等操作')
                return None
        if write_flag:
            logger.info('根据用户输入，所查译文将写入数据库')
            # 爬取到译文内容后，要保存在当前数据库中
            db_word.add_content(content, translation, db='private')
        else:
            logger.info('根据用户输入，所查译文将不写入数据库，已跳过写入步骤')
        # 尝试音频播放：播放中删除音频会导致异常(PermissionError)
        try:
            db_audio.audio_play(content)
        except Exception as e:
            logger.warning('音频文件使用中，无法删除，故而产生了异常，请忽略', exc_info=True)


# =================================

# 给用户提供的帮助文档
# enabled：仅当其值为'*h'或'*help'时被激活
def help_user(enabled):
    logger.debug('程序到达：manager.py-help_user函数')
    if enabled not in ['*h', '*help']:
        return False
    compatible.clear_screen()
    # 取代空格
    space = compatible.SPACE
    print('='*45)
    print('符号{}意义'.format(space*15))
    print('-'*45)
    print('*h(help){}查看帮助'.format(space*7))
    print('*f(filter){}单词过滤'.format(space*5))
    print('*e(export){}导出数据库'.format(space*5))
    print('*i(import){}导入数据库'.format(space*5))
    print('*s(summary){}汇总数据库'.format(space*4))
    print('*m(merge){}汇总音频'.format(space*6))
    print('*r(revise){}单词复习'.format(space*5))
    print('*{}设置数据库'.format(space*14))
    print('[单词]*a(again){}重播音频'.format(space*6))
    print('[单词]*c(change){}译文修改'.format(space*5))
    print('[单词]*d(delete){}删除单词'.format(space*5))
    print('[单词]+{}查找单词时显示更多内容'.format(space*14))
    print('[单词]-{}不将查找的单词写入数据库'.format(space*14))
    print('-'*45)
    print('{}Android操作指南'.format(space*14))
    print('想要导出综合库：请复制综合库到用户库文件夹\n'
          '设置导出文件夹：请创建空文件夹_user/export\n'
          '设置导入文件夹：请创建空文件夹_user/import')
    print('='*45)
    collect.get_input(prompt='按任意键退出帮助：')


# 解析enabled和content
# 解析enabled命令有如下要求
def parse_enabled_and_content(content):
    logger.debug('程序到达：manager.py-parse_enabled_and_content函数')
    # 注意：此处星号必须放在最后；完整的必须放在简写之前！！
    symbols = (
        '*filter', '*f',  # 正则匹配过滤单词
        '*again', '*a',   # 重听音频
        '*export', '*e',  # 导出词库
        '*import', '*i',  # 导入词库
        '*change', '*c',  # 修改译文
        '*delete', '*d',  # 删除单词
        '*revise', '*r',  # 单词复习
        '*summary', '*s', # 汇总用户单词到公共词库
        '*merge',  '*m',  # 汇总用户音频到总音频库
        '*help', '*h',    # 查看帮助
        '-', '+', '*')
    enabled = ''
    for symbol in symbols:
        if content.startswith(symbol):
            index = content.index(symbol)
            content = content[index+len(symbol):]
            content = content.strip()
            enabled = symbol
    for symbol in symbols:
        if content.endswith(symbol):
            index = content.rindex(symbol)
            content = content[:index]
            content = content.strip()
            enabled = symbol
    result = (enabled, content)
    logger.info('(enabled, content)===>({!r},{!r})'.format(enabled, content))
    return result


# 让用户可以重听音频
# enabled：仅当传入'*a'和'*again'时激活此函数
def audio_repeat(enabled, content):
    logger.debug('程序到达：manager.py-audio_repeat函数')
    if enabled not in ['*a', '*again']:
        # 用户未要求重播音频
        return None
    logger.debug('用户进入音频重播模式')
    # 用户要求重播音频，但是中文和长英文不能重播音频
    if not public.is_english(content):
        print('中文、长英文不能重听音频')
        return None
    # 进入重听模式
    while True:
        logger.info('准备播放音频：{}'.format(content))
        choice = collect.get_input(prompt='清屏(**)，退出(*)，重播(Enter)：')
        if choice == '':
            db_audio.audio_play(content)
        elif choice == '*':
            return None
        elif choice == '**':
            compatible.clear_screen(debug=public.DEBUG)
            config.print_config()
            print('-'*45)
        else:
            compatible.clear_screen(debug=public.DEBUG)
            config.print_config()
            return None


# 汇总用户词库到公共词库
def summary_user_words(enabled):
    logger.debug('程序到达：manager.py-summary_user_words函数')
    if enabled not in ['*s', '*summary']:
        # 用户未要求汇总用户词库到公共词库
        return None
    logger.debug('用户进入汇总用户词库到公共词库函数')
    print('注意：汇总操作无法撤销！')
    choice = collect.get_input(prompt='确认汇总当前单词到公共词库(*)，退出(Enter)：')
    if choice == '':
        return None
    elif choice == '*':
        compatible.clear_screen(debug=public.DEBUG)
        db_word._add_user_words_to_public_db()
        choice = collect.get_input(prompt='清屏(Enter)，退出(*)：')
        if choice == '':
            compatible.clear_screen(debug=public.DEBUG)
            config.print_config()
        elif choice == '*':
            return None
    else:
        return None


# 汇总用户音频到总音频库
def merge_audios(enabled):
    logger.debug('程序到达：manager.py-merge_audios函数')
    if enabled not in ['*m', '*merge']:
        # 用户未要求汇总用户音频到总音频库
        return None
    public_path = path.user.public_audios_path
    private_path = path.user.private_audios_path
    print('用户音频库路径：{}'.format(private_path))
    print('总的音频库路径：{}'.format(public_path))
    if not path.path_exist(public_path):
        print('总的音频库路径设置错误，已退出音频汇总！')
        return False
    if not path.path_exist(private_path):
        print('用户音频库路径设置错误，已退出音频汇总！')
        return False
    choice = collect.get_input('请确认已经在path模块设置好了音频路径(*)：')
    if choice == '*':
        db_audio._merge_audios(public_path, private_path)
        compatible.clear_screen(debug=public.DEBUG)
        config.print_config()
        return True
    else:
        compatible.clear_screen(debug=public.DEBUG)
        config.print_config()
        return False


# 仅查找译文内容，译文内容不写入数据库
# enabled：仅当传入'-'时激活此函数
def lookup_only(enabled, content):
    logger.debug('程序到达：manager.py-lookup_only函数')
    if enabled != '-':
        return None
    logger.debug('进入仅查找译文函数')
    # 此处write_flag必须为False
    lookup_content(content, write_flag=False)
    return None


# 获得更多译文内容，且译文内容不写入数据库
# enabled：仅当传入'+'时激活此函数
def lookup_more(enabled, content):
    logger.debug('程序到达：manager.py-lookup_more函数')
    if enabled != '+':
        return None
    logger.debug('进入扩展翻译函数，将可以翻译句子')
    # 扩展核心代码，增加句子翻译功能
    translate_expend.youdao_translate(content)
    # 尝试音频播放：播放中删除音频会导致异常(PermissionError)
    try:
        db_audio.audio_play(content)
    except Exception as e:
        logger.warning('音频文件使用中，无法删除，故而产生了异常，请忽略', exc_info=True)
    return None


# 用于更改个人单词译文
def change_main(enabled, content):
    logger.debug('程序到达：manager.py-change_main函数')
    if enabled not in ['*c', '*change']:
        return None
    if not content:
        print(compatible.colorize(text='要修改译文请用命令：[单词] *c', color='cyan'))
        print(compatible.colorize(text='要修改译文请用命令：[单词] *change', color='cyan'))
        return None
    logger.debug('进入自定义译文函数，用户将自定义译文')
    translation_list = get_translation_from_db(content, write_flag=False)
    translation = translation_list[1][1]
    default_translation = '*'.join(translation)
    print(compatible.colorize(text='原译文：', color='green'), translation)
    # 调用 sl4a 从程序框获取自定义译文
    custom_translation = compatible.get_custom_translation(
                default=default_translation,
                prompt="自定义译文(不同词性以*分隔)",
                subprompt=default_translation)
    if not custom_translation:
        logger.debug('用户没有输入译文，退出译文修改函数')
        print('没有修改单词{}的译文'.format(content))
        return None
    # 不同的词性用星号分隔
    new_translation = custom_translation.split('*')
    print(compatible.colorize(text='新译文：', color='red'), new_translation)
    choice = collect.get_input(prompt='取消更改(Enter)，确认更改(*)：')
    if choice == '':
        compatible.clear_screen(debug=public.DEBUG)
        config.print_config()
        return None
    elif choice == '*':
        # 首先删除原来的不想要的译文
        if db_word.delete_content_from_dict(content, db='private'):
            # 然后添加新的译文到数据库
            logger.info('已删除个人单词表中{}的译文{}'.format(content, translation))
            translation_list[1][1] = new_translation
            db_word.add_content(content, translation_list[1], db='private')
            logger.info('已将{}的译文{}写入个人数据库'.format(content, new_translation))
            print('已经成功更改{}的译文！'.format(content))
            # 以下同步修改公共数据库
            choice_modify_public = collect.get_input(prompt='同步更改公共库(*)，不同步更改(Enter)：')
            # 删除原来不想要的译文，返回删除成功标识
            if choice_modify_public == '*':
                if db_word.delete_content_from_dict(content, db='public'):
                    logger.info('已删除公共单词表中{}的译文{}'.format(content, translation))
                    # 删除成功，修改译文
                    db_word.add_content(content, translation_list[1], db='public')
                    logger.info('已将{}的译文{}写入公共数据库'.format(content, new_translation))
                    print('公共库已经成功更改{}的译文！'.format(content))
                else:
                    logger.info('删除失败！未删除：公共单词表中{}的译文{}'.format(content, translation))
                    print('公共库不存在{}的数据，请使用*s直接同步该单词数据到公共数据库'.format(content))
            else:
                print('公共库未更改{}的译文！'.format(content))
        else:
            logger.info('删除失败！未删除：个人单词表中{}的译文{}'.format(content, translation))
            print('更改失败！没有更改{}的译文！'.format(content))


# 删除用户不想要的单词及其译文
def delete_main(enabled, content):
    logger.debug('程序到达：manager.py-delete_main函数')
    if enabled not in ['*d', '*delete']:
        return None
    if not content:
        print(compatible.colorize(text='要删除单词请用命令：[单词] *d', color='cyan'))
        print(compatible.colorize(text='要删除单词请用命令：[单词] *delete', color='cyan'))
        return None
    logger.debug('进入删除单词数据函数')
    choice = collect.get_input(prompt='退出(Enter)，确认删除{}的单词数据(*)：'.format(content))
    if choice == '':
        compatible.clear_screen(debug=public.DEBUG)
        config.print_config()
    elif choice == '*':
        logger.info('开始删除个人数据库中{}单词的数据'.format(content))
        db_word.delete_content_from_dict(content, db='private')
        print('已经删除单词{}的数据'.format(content))


# 更多操作函数
# 用于扩展用户操作
def more_operator(enabled, content):
    logger.debug('程序到达：manager.py-more_operator函数')
    # 给用户返回帮助内容
    if enabled in ['*h', '*help']:
        help_user(enabled)
        compatible.clear_screen(debug=public.DEBUG)
        config.print_config()
    # 进入单词导出操作
    elif enabled in ['*e', '*export']:
        db_export.export_datas(enabled)
        compatible.clear_screen(debug=public.DEBUG)
        config.print_config()
    # 进入单词导入操作
    elif enabled in ['*i', '*import']:
        db_import.main(enabled)
        update_config()
        compatible.clear_screen(debug=public.DEBUG)
        config.print_config()
    # 进入单词译文修改函数
    elif enabled in ['*c', '*change']:
        change_main(enabled, content)
    # 进入单词删除函数
    elif enabled in ['*d', '*delete']:
        delete_main(enabled, content)
    # 进入单词匹配查找函数
    elif enabled in ['*f', '*filter']:
        db_filter.filter_translation(enabled)
    # 进入用户词库汇总到公共词库函数
    elif enabled in ['*s', '*summary']:
        summary_user_words(enabled)
    # 进入用户音频汇总到总音频库函数
    elif enabled in ['*m', '*merge']:
        merge_audios(enabled)
    elif enabled in ['*r', '*revise']:
        db_revise.main(enabled)
    # 仅当content='*'时，更改配置数据库名称函数激活
    elif enabled == '*':
        config.main(enabled)
    # 进入仅查译文函数
    elif enabled == '-':
        lookup_only(enabled, content)
    # 进入查找更多译文函数
    elif enabled == '+':
        lookup_more(enabled, content)
    else:
        return None


def main():
    logger.debug('程序到达：manager.py-main函数')
    logger.info('\n{}主函数{}'.format('='*19, '='*20))
    compatible.clear_screen(debug=public.DEBUG)
    logger.debug('\n{}manager - main函数标记点00{}'.format('-'*9, '-'*10))
    config.check_config()
    logger.debug('\n{}manager - main函数标记点01{}'.format('-'*9, '-'*10))
    threading.Thread(target=db_backup.backup_data).start()
    logger.debug('\n{}manager - main函数标记点02{}'.format('-'*9, '-'*10))
    # 给用户打印数据库单词数量提示
    config.print_config()
    logger.debug('\n{}manager - main函数标记点03{}'.format('-'*9, '-'*10))
    logger.info('\n{}循环块{}'.format('+'*19, '+'*20))
    # 统计循环次数
    count = 0
    split_len = int((45-3-8)//2)
    while True:
        count += 1
        logger.info('\n{}第{:03d}次循环{}'.format('-'*split_len, count, '-'*split_len))
        logger.debug('\n{}manager - main函数标记点04{}'.format('-'*9, '-'*10))
        # 查单词流程正式开始
        content = collect.get_content()
        logger.debug('\n{}manager - main函数标记点05{}'.format('-'*9, '-'*10))
        enabled, content = parse_enabled_and_content(content)
        logger.debug('\n{}manager - main函数标记点06{}'.format('-'*9, '-'*10))
        # 确保写入数据库的单词两端无空白符
        content = content.strip()
        logger.debug('\n{}manager - main函数标记点07{}'.format('-'*9, '-'*10))
        more_operator(enabled=enabled, content=content)
        logger.debug('\n{}manager - main函数标记点08{}'.format('-'*9, '-'*10))
        if enabled in ('*h', '*help',
                       '*e', '*export',
                       '*i', '*import',
                       '*d', '*delete',
                       '*c', '*change',
                       '*f', '*filter',
                       '*s', '*summary',
                       '*m', '*merge',
                       '*r', '*revise',
                       '-', '+', '*'):
            continue
        logger.debug('\n{}manager - main函数标记点09{}'.format('-'*9, '-'*10))
        # 判断退出，其中包含配置更新的函数
        judge_exit(content, prompt=None)
        logger.debug('\n{}manager - main函数标记点10{}'.format('-'*9, '-'*10))
        # 查单词，播放音频
        lookup_content(content)
        logger.debug('\n{}manager - main函数标记点11{}'.format('-'*9, '-'*10))
        audio_repeat(enabled=enabled, content=content)
        logger.debug('\n{}manager - main函数标记点12{}'.format('-'*9, '-'*10))



