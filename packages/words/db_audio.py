# coding=utf-8
# =================================
# 作者声明：
# 文件用途：
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 其他依赖：无
# =================================
import zlib
import shutil
# ---------------------------------
# 从顶层文件执行本脚本使用
from . import translate
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
logger = logging.getLogger('main.db_audio')
# =================================
# 注意！已知以下音频有问题：
# a matter of
# =================================
# 音频数据的压缩和解压缩


# 压缩音频文件内容成一段字节串
# 若传入compressed_filename，则将压缩后的字节串写入该文件，
# 否则，就将压缩后的字节串直接返回
def compress_audio(mp3_filename, compressed_filename=None):
    logger.info('正在压缩音频数据')
    with open(mp3_filename, 'rb') as f:
        content = f.read()
        content_out = zlib.compress(content)
        len_content = len(content)
        len_content_out = len(content_out)
        len_change = len_content_out - len_content
        logger.debug('原数据大小({x0:7d})===>新数据({x1:7d})，改变({x2:7d})'.format(x0=len_content, x1=len_content_out, x2=len_change))
        logger.debug('压缩后的数据类型：{}'.format(type(content_out)))
    if compressed_filename is None:
        return content_out
    else:
        with open(compressed_filename, 'wb') as f:
            f.write(content_out)
        return compressed_filename


# 解压缩音频数据
# 若传入压缩数据字节串byte_strings，则对字节串施加解压缩命令，
# 若传入了压缩文件名路径compressed_filename，
# 则对文件内容施加解压缩命令，否则，返回None
# 若传入了参数mp3_filename，
# 则还会将解压缩后的内容写入文件，否则直接返回解压缩后的内容
def decompress_audio(byte_strings=None, compressed_filename=None, mp3_filename=None):
    if byte_strings is not None:
        decompressed = zlib.decompress(byte_strings)
    elif compressed_filename is not None:
        with open(compress_filename, 'rb') as f:
            byte_strings = f.read()
        decompressed = zlib.decompress(byte_strings)
    else:
        print('未传入数据来源！')
        return None
    len_byte_strings = len(byte_strings)
    len_byte_strings_decompressed = len(decompressed)
    len_change = len_byte_strings_decompressed - len_byte_strings
    logger.debug('正在解压缩音频数据，并创建音频文件')
    logger.debug('原数据大小({x0:7d})===>新数据({x1:7d})，改变({x2:7d})'.format(x0=len_byte_strings, x1=len_byte_strings_decompressed, x2=len_change))
    logger.debug('解压缩后的数据类型：{}'.format(type(decompressed)))
    logger.debug('解压缩后的文件路径：{}'.format(mp3_filename))
    logger.info('解压缩数据完毕！')
    if mp3_filename is None:
        logger.info('成功返回解压缩数据')
        return decompressed
    else:
        with open(mp3_filename, 'wb') as f:
            f.write(decompressed)
        logger.info('成功写入解压缩数据到文件')
        logger.debug('文件名:{}'.format(mp3_filename))
        return mp3_filename

# =================================

# 向audio数据库文件中添加一条压缩后的音频数据
# content：指单词，类型是字符串，用于找到该单词对应的音频数据库
# audio_type：该音频是英音要传入0，是美音要传入1，类型是整数
# mp3_filename：原未压缩的mp3数据文件的文件名路径
# audio_filename：压缩后的数据库文件的文件名路径，其中写入了一个字典
# 该字典中的内容为：{单词1:[英音音频0, 美音音频1], ...}
# cover_old：传入True时，将覆盖原有数据
def add_audio(content, audio_type, mp3_filename, audio_filename, cover_old=False):
    if not path.path_exist(audio_filename):
        public.write_pickle(dict(), audio_filename)
    audio_dict = public.read_pickle(audio_filename)
    # 数据库获取异常，直接返回False
    if audio_dict is None:
        logger.info('因数据库获取异常，添加音频失败！请检查数据库！！！')
        return False
    # 数据存在，并且没有要求覆盖原数据，则直接返回
    if (content in audio_dict) and (not cover_old):
        logger.info('音频数据已经存在，但未要求覆盖原数据，因此不再添加到音频数据库')
        return False
    # --------------------
    # 以下任一中情况都要添加音频字符串，因此，先压缩音频数据
    # 压缩后的音频内容字节串：
    decompression = compress_audio(mp3_filename)
    # 音频文件数据字节串不存在，检查并添加
    if content not in audio_dict:
        # 先创建音频占位列表
        audio_dict[content] = [None, None]
        audio_dict[content][audio_type] = decompression
        # 将新字典写入音频数据库
        public.write_pickle(audio_dict, audio_filename)
        logger.info('音频数据原来不存在，现已创建，并正常添加到音频数据库')
        logger.info(audio_filename)
        return True
    # 部分类型的音频数据不存在，检查并添加
    if audio_dict[content][audio_type] is None:
        # 添加到音频字典
        audio_dict[content][audio_type] = decompression
        # 将新字典写入音频数据库
        public.write_pickle(audio_dict, audio_filename)
        logger.info('对应类型的音频数据原来不存在，现已添加正常到音频数据库')
        logger.info(audio_filename)
        return True
    # 虽然音频数据已经存在，但是要求覆盖原数据，因此检查并添加
    if (audio_dict[content][audio_type] is not None) and cover_old:
        audio_dict[content][audio_type] = decompression
        # 将新字典写入音频数据库
        public.write_pickle(audio_dict, audio_filename)
        logger.info('对应类型的音频数据原来存在，现已覆盖原数据，并正常添加到音频数据库')
        logger.info(audio_filename)
        return True

# =================================

# 从pk_filename文件中获取音频数据列表
# 注意：数据库或数据不存在时，返回None
# audio_type：音频类型，0为英音音频，1为美音音频
def get_audio_bytes_from_pickle(content, audio_type):
    # 获取音频数据库名称路径
    pk_filename = path.own.audio_filename(content)
    if not path.path_exist(pk_filename):
        public.write_pickle(dict(), pk_filename)
    logger.debug('音频数据库路径：{}'.format(pk_filename))
    # 读取音频数据库字典
    audio_dict = public.read_pickle(pk_filename)
    # 判断单词是否存在于音频数据中
    if content not in audio_dict:
        logger.info('{}的音频不存在于音频数据库{}'.format(content, pk_filename))
        return None
    # 音频数据存在，进一步检查对应类型的音频是否存在
    audio_list = audio_dict[content]
    audio_bytes = audio_list[audio_type]
    if audio_bytes is not None:
        return audio_bytes
    logger.info('并未获取到音频字节串')
    return None


# 获取、生成、播放，并最后删除临时音频
# content：单词原文
# play：传入True表示播放
# audio_type：指播放英音指定为0，美音指定为1
# sleep_time：音频播放时间
def word_play(content, play=True, audio_type=0, debug=False):
    # 如果确定不播放音频，则跳过
    if not play:return False
    # -------------------------
    # 修正单词的格式
    content = public.deal_content(content)
    # 根据需要获取指定音频
    audio_bytes = get_audio_bytes_from_pickle(content, audio_type=audio_type)
    # 检查音频是否获取正确
    if audio_bytes is None:
        logger.info('查找的音频不存在！')
        return False
    # -------------------------
    # 正确获取到了音频数据，接下来解压缩，并创建和播放音频文件
    # 要创建的临时音频文件名路径
    mp3_filename = path.own.mp3_filename()
    # 将字节串转化为音频文件，并返回音频文件名路径
    # 注意：这个路径正常情况下与mp3_filename相同
    final_filename = decompress_audio(byte_strings=audio_bytes, compressed_filename=None, mp3_filename=mp3_filename)
    if final_filename != mp3_filename:
        logger.info('音频文件路径已被改变为：{}'.format(final_filename))
    # 播放音频，然后删除临时创建的mp3音频文件
    # 注意：如果传入debug=True，则实际并不会删除音频文件
    remove_result = compatible.play_and_remove_audio(final_filename, play=play, debug=debug)
    if not remove_result:
        logger.info('对临时文件的删除步骤已处理完毕')
        logger.debug('未删除临时音频文件：{}'.format(final_filename))
    else:
        logger.info('对临时文件的删除步骤已处理完毕')
        logger.debug('成功删除临时音频文件：{}'.format(final_filename))
    return True


# 从数据库播放音频
# debug：传入为True时，将在播放音频后，不删除音频文件
def audio_play(content, play=True):
    logger.info('程序进入音频查找和播放函数')
    try:
        play_result = word_play(content, audio_type=0, play=play)
    except TypeError:
        logger.info('可能由于含有中文，音频播放结果为None，返回True')
        return True
    if play_result:
        # 播放成功，play_result=True
        return True
    else:
        # 播放失败，play_result=False
        # 尝试下载音频(扇贝单词音频)，并存入音频数据库
        translate.get_en_audio_from_shanbay(content, cover_old=True)
        # 再次尝试播放音频
        play_result = word_play(content, audio_type=0, play=play)
        if play_result:
            return True
        else:
            return False



# =================================

# 对比音频，如果首音频不齐，则补全缺少的音频
# 返回：True，表明总库被改变；False，表明总库没有改变
# 注意：audios_pk_filename1是总库，audios_pk_filename2是私库
def _change_audios(audios_pk_filename1, audios_pk_filename2, cover_old=False):
    audios_bytes_dict1 = public.read_pickle(audios_pk_filename1)
    audios_bytes_dict2 = public.read_pickle(audios_pk_filename2)
    # 用于确认总库是否被改变了
    change_flag = False
    for content, audios_list2 in audios_bytes_dict2.items():
        # 总库不存在该单词的音频，复制到总库
        if content not in audios_bytes_dict1:
            audios_bytes_dict1[content] = audios_list2
            change_flag = True
        # 总库存在该单词的音频，分条处理
        else:
            # 处理英音
            if audios_bytes_dict2[content][0] is not None:
                # 总库英音不存在，复制；或总库英音存在但要求覆盖，覆盖
                if (audios_bytes_dict1[content][0] is None) or cover_old:
                    audios_bytes_dict1[content][0] = audios_bytes_dict2[content][0]
                    change_flag = True
            # 处理美音
            if audios_bytes_dict2[content][1] is not None:
                # 总库美音不存在，复制；或总库美音存在但要求覆盖，覆盖
                if (audios_bytes_dict2[content][1] is None) or cover_old:
                    audios_bytes_dict1[content][1] = audios_bytes_dict2[content][1]
                    change_flag = True
    # 总库音频字典被改变，写入
    if change_flag:
        public.write_pickle(audios_bytes_dict1, audios_pk_filename1)
    return change_flag


# 将私库音频 合并到总库
# 注意：请手动在path.py中设置总音频库和私库的文件夹路径
# 注意：千万不要写颠倒总音频库和私音频库，否则将丢失音频数据！
def _merge_audios(public_path, private_path):
    initials = 'abcdefghijklmnopqrstuvwxyz'
    for initial in initials:
        for initial2 in initials:
            print(' 正在汇总音频库{}{}_pickle\r'.format(initial, initial2), end='')
            audios_pk_filename1 = path.user.get_audios_filename(public_path, initial, initial2)
            audios_pk_filename2 = path.user.get_audios_filename(private_path, initial, initial2)
            if path.path_exist(audios_pk_filename1) and  path.path_exist(audios_pk_filename2):
                # 总库存在，私库也存在，对比选优
                change_result = _change_audios(audios_pk_filename1, audios_pk_filename2, cover_old=False)
                if change_result:
                    print('已更新音频库：{}'.format(path.get_basename(audios_pk_filename1)))
                    logger.info('已更改音频库：{}'.format(audios_pk_filename1))
            elif (not path.path_exist(audios_pk_filename1)) and path.path_exist(audios_pk_filename2):
                # 总音频库不存在，但私库存在，直接复制到总音频库
                shutil.copyfile(audios_pk_filename2, audios_pk_filename1)
                logger.info('复制用户音频库到总音频库！')
                logger.info('用户音频库{}'.format(audios_pk_filename2))
                logger.info('总的音频库{}'.format(audios_pk_filename1))
                print('已复制音频库：{}'.format(path.get_basename(audios_pk_filename1)))
            else:
                # 其它情况不处理
                continue
    collect.get_input('所有音频库已经全部汇总结束：')


