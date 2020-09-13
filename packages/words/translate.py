# coding=utf-8
# =================================
# 作者声明：
# 文件用途：翻译中英文的方法
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 其他依赖：无
# 运行注意：在本文件中的翻译方法需要连网
# =================================
import re
import json
import urllib.request
# 捕获异常：http.client.BadStatusLine
import http.client
# 捕获异常：urllib.error.HTTPError
import urllib.error
# ---------------------------------
from ..core.independent import path
from ..core.independent import public
# =================================
# 日志记录
import logging
logger = logging.getLogger('main.translate')
# =================================
# 下载单词音频

# 下载扇贝单词音频
# cover_old：若要覆盖原数据，请设置cover_old=True
def get_en_audio_from_shanbay(content, cover_old=False):
    logger.info('程序到达：translate.py-get_en_audio_from_shanbay函数')
    logger.info('正在抓取扇贝单词音频链接并准备下载音频文件')
    content = public.deal_content(content)
    # 英音
    url = 'http://media.shanbay.com/audio/uk/{}.mp3'.format(content)
    mp3_filename = path.own.mp3_filename()
    try:
        # 下载音频
        urllib.request.urlretrieve(url, mp3_filename)
    except UnicodeEncodeError:
        logger.info('因含有中文，扇贝音频下载异常(正常情况)，链接：{}'.format(url))
        return None
    except urllib.error.HTTPError:
        logger.info('因扇贝网对单词的支持度不好，该单词({})没有音频'.format(content))
        return None
    # 检查下载音频的存在性
    if not path.path_exist(mp3_filename):
        return None
    # 将下载的音频文件添加至音频数据库，首先获取数据库路径
    audio_filename = path.own.audio_filename(content)
    # 英音设置为0，美音设置为1，这里是英音
    index = 0
    packages = __import__('packages')  # for 小米-qpython3v1.0.0(python3.2.2)
    add_result = packages.words.db_audio.add_audio(content, audio_type=index, mp3_filename=mp3_filename, audio_filename=audio_filename, cover_old=cover_old)
    if add_result:
        logger.info('扇贝单词的音频成功添加至数据库')
    if not add_result:
        logger.info('扇贝单词的音频添加至数据库失败')
    # 清理所下载的音频
    path.os_remove(mp3_filename)
    logger.info('要添加的扇贝单词的临时音频已被清除')


# 获取网页源代码
# 若出现Connect reset by peer，请修改该部分内容
def get_en_html(content):
    logger.info('程序到达：translate.py-get_en_html函数')
    url_template = 'http://m.youdao.com/dict?le=eng&q={}'
    url = url_template.format(content)
    data = {}
    data['type'] = 'AUTO'
    data['i'] = content
    data['doctype'] = 'json'
    data['xmlVersion'] = '1.8'
    data['keyfrom'] = 'fanyi.web'
    data['ue'] = 'UTF-8'
    data['action'] = 'FY_BY_CLICKBUTTON'
    data['typoResult'] = 'true'
    data = urllib.parse.urlencode(data).encode('utf-8')
    # ----------------------------------------
    try:
        # 获取请求
        response = urllib.request.urlopen(url, data, timeout=5)
        # 读取网页
        html = response.read().decode('utf-8')
        return html
    except urllib.error.URLError as e:
        print('-----(translate en)无网络，请连网翻译')
        return None
    except http.client.BadStatusLine as e:
        # 捕获：http.client.BadstatusLine
        print("网页解析失败，请重试")
        logger.error('网页解析失败', exc_info=True)
        return False
    except Exception as e:
        # 捕获所有异常，可能是未考虑过的异常
        print('出现未考虑的异常：{}'.format(e))
        logger.error('出现异常', exc_info=True)
        return False


# 根据url获取中文的翻译信息
def get_ch_json(content):
    logger.info('程序到达：translate.py-get_ch_json函数')
    data = dict()
    data['type'] = 'AUTO'
    data['i'] = content
    data['doctype'] = 'json'
    data['xmlVersion'] = '1.8'
    data['keyfrom'] = 'new-fanyi.smartResult'
    data['ue'] = 'UTF-8'
    data['action'] = 'FY_BY_CLICKBUTTON'
    data['typoResult'] = 'true'
    data = urllib.parse.urlencode(data).encode('utf-8')
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null'
    try:
        response = urllib.request.urlopen(url, data)
        html = response.read().decode('utf-8')
        target_dict = json.loads(html)
        logger.debug('获取到的内容：{}'.format(target_dict))
        return target_dict
    except urllib.error.URLError as e:
        print('-----(translate ch)请连网翻译')
        return None
    except Exception as e:
        print('出现未考虑的异常：{}'.format(e))
        logger.error('出现异常', exc_info=True)
        return False


# 下载有道单词音频
# html是已经获取的网页文件
# content是查找的单词，用来给mp3文件命名
# cover_old：传入True将覆盖原有音频数据，否则传入False(默认)
@public.retry_decorator()
def get_en_audio(html, content, cover_old=False):
    logger.info('程序到达：translate.py-get_en_audio函数')
    logger.info('正在抓取有道词典音频链接并准备下载音频文件')
    content = public.deal_content(content)
    audio_pattern = r'''data-rel="(.*?)"\r\n'''
    audio_url_list = re.findall(audio_pattern, html, re.S)
    audio_names_list = list()  # 用于返回值
    # 如果音频链接不存在，直接返回空列表
    if audio_url_list is None:
        return audio_names_list
    # 若链接存在，则尝试下载
    for index, audio_url in enumerate(audio_url_list):
        # 首先获取临时音频文件存储路径
        # mp3_filename：可以播放的音频文件名
        mp3_filename = path.own.mp3_filename()
        # https不能爬取，替换成http
        audio_url = audio_url.replace('https', 'http', 1)
        # 下载音频文件
        urllib.request.urlretrieve(audio_url, mp3_filename)
        # 将下载的音频文件添加至音频数据库，首先获取数据库路径
        # audio_filename：用来存储音频的文件名
        audio_filename = path.own.audio_filename(content)
        packages = __import__('packages')  # for 小米-qpython3v1.0.0(python3.2.2)
        # 添加至音频数据库，若要覆盖原数据请设置cover_old=True
        add_result = packages.words.db_audio.add_audio(content,
                audio_type=index,
                mp3_filename=mp3_filename,
                audio_filename=audio_filename,
                cover_old=cover_old)
        if add_result:
            logger.info('音频成功添加至数据库')
        if not add_result:
            logger.info('音频添加至数据库失败')
        # 清理所下载的音频
        path.os_remove(mp3_filename)
        logger.info('要添加的音频已被清除')


def get_en_soundmark(html):
    logger.info('程序到达：translate.py-get_en_soundmark函数')
    # 获取音标：得到的结果必须是字符串
    logger.info('正在抓取音标')
    pattern_soundmark = r'<span class="phonetic">(.*?)</span>\r\n'
    soundmark = re.findall(pattern_soundmark, html, re.S)
    try:
        logger.info('音标：{}'.format(soundmark))
        if len(soundmark) == 2:
            # 如果存在两个音标，说明英，美音音标都有
            # 第一个是英音音标，第二个是美音音标
            if soundmark[0] == soundmark[1]:
                # 如果英美音相同，则只要一个
               return soundmark[0]
            else:
                # 若英美音不同，则两个可能都要，这要看个人爱好，这里我只要英音                
                # 英音音标，选择该项注释上句表示只要英音标
                return soundmark[0]
        elif len(soundmark) == 1:
            return soundmark[0]  # 英文音标或美音音标
        else:
            # 程序运行到这里，说明根本没有抓取到音标
            raise IndexError("没有抓取到英文音标！")
    except IndexError:
        # 异常原因1：网页被改变
        # 异常原因2：单词输入错误
        # 异常原因3：英文(短语或个别合成词等)本身不存在音标
        logger.info('音标未获取(也可能是正常情况：偏词怪词无音标)！', exc_info=True)
        return str('')


# 解析有道翻译(机器翻译)结果
# 返回：一个字符串
# 返回：None，代表不存在翻译结果
def parse_youdao_trans_en(html):
    logger.info('程序到达：translate.py-parse_youdao_trans_en函数')
    pattern = r'<div id="fanyi" class="trans-container fanyi\s*">\s*<div class="trans-container \S*\s?">\s*<p>.*?</p>\s*<p>(.*?)</p>\s*<p.*?>.*?</p>'
    trans = re.findall(pattern, html, re.S)
    if trans:
        return trans[0]
    print('机器翻译没有获取到结果！')
    logger.info('机器翻译没有获取到结果')
    return None


def get_en_translation_list(html):
    logger.info('程序到达：translate.py-get_en_translation_list函数')
    # 获取译文：得到的结果必须是列表
    # 正确的英文都应该有译文(不一定有音标)
    logger.info('正在抓取译文')
    try:
        pattern_translation = r'\t\t\t<li>(.*?)</li>\r\n'
        translation = re.findall(pattern_translation, html, re.S)
        logger.info(translation)
        if isinstance(translation, list) and (translation != list()):
            return translation  # 如果本身是列表(不能为空)，就直接接收
        elif isinstance(translation, str) and (translation != ''):
            return [translation]  # 如果本身是字符串(不为空)，就放入列表再接收
        elif translation == list():
            # 通常不存在译文时，正则表达式应该返回一个空列表
            # 如果译文不存在，则尝试获取机器翻译
            youdao_trans = parse_youdao_trans_en(html)
            # 获取到了机器翻译则返回，否则还是返回False
            if youdao_trans:
                return [youdao_trans]
            return False
        else:
            # 如果不是列表也不是字符串，那是不可能的，应该引发一个异常
            print("translation的类型：%s" % str(type(translation)))
            print("translation的结果：%s" % str(translation))
            raise ValueError("这里产生了不可能出现的异常，我已经等候多时！")
    except IndexError:
        # 也有可能是网址被改变了
        logger.error('翻译内容不存在', exc_info=True)
        # 可能是没有音标，但如果没有译文，可能网址需要更换了
        return False


# 获取英文的音标(如果存在)和译文，注意：不能查中文！！！
# content：字符串，是用户要查的单词
# cover_old：传入True将覆盖原有数据，否则传入False
# 返回一个二元列表，第一个元素代表音标(用字符串表示)，第二个元素代表翻译(用列表表示)
# 返回结果有：
# 英文：[音标字符串, 译文内容组成的列表]，查单词的正常情况
# 英文：['', 译文内容组成的列表]，查词语的正常情况
# 异常：['', False]
# 翻译获取失败，返回：[音标字符串, False]
# 网页解析失败，返回：['', False]，如http.client.BadStatusLine异常
# 联网失败，返回：None
# 注意：翻译失败必须返回False或None，否则可能意外通过数据库写入检查！！
def get_translation_en(content, cover_old=False):
    logger.info('程序到达：translate.py-get_translation_en函数')
    # 最终必须以下面的结构返回
    result = [str(), list()]
    html = get_en_html(content)
    if html is False:
        logger.info('由于html为空，音标和译文获获取失败')
        return ['', False]
    if html is None:
        logger.info('由于html为None，音标和译文获获取失败')
        return None
    # -----------------------------------
    # 以上为网页获取，下面开始解析网页
    # 下载真人发音并存储：不需要真人发音可以注释掉
    get_en_audio(html, content, cover_old=cover_old)
    # 获取音标
    result[0] = get_en_soundmark(html)
    # 获取译文
    result[1] = get_en_translation_list(html)
    logger.info('音标和译文获取完毕')
    return result


# =================================
# 中文翻译函数

# 获取中文译文
# 获取中文译文(其实也可以获取英文译文，不过不用它获取英文译文)
# 根据用户输入的内容，尝试联网翻译输入的内容，并返回翻译结果
# 注意：翻译结果可能为：空(None)、正确内容、未连网(False)
# 返回结果为：
# 中文，正常结果：['', 译文内容组成的列表]
# 异常1：['', False]
# 异常2：None  # 当且仅当未连网时返回的结果
def get_translation_ch(content):
    logger.info('程序到达：translate.py-get_translation_ch函数')
    target_dict = get_ch_json(content)
    if target_dict is None:
        return None
    try:
        target_list = target_dict["translateResult"]
        if (len(target_list) == 1) and (len(target_list[0]) == 1):
            translation = target_list[0][0]['tgt']
            return ['', translation]
        else:
            print('有多组数据但是只获取了一组，请修改代码！')
            print(target_list)
    except KeyError as e:
        print("翻译内容不存在！")
        logger.error('出现异常，翻译不存在', exc_info=True)
        return ['', False]


# 获取中文或英文的译文和音标(仅对于有些英文)
# 返回结果：
# 正常1：['', 译文内容组成的列表]  # 个别英文或中文
# 正常2：[音标字符串, 译文内容组成的列表]  # 英文
# 异常1：['', False]  # 翻译不存在
# 异常2：None  # 未连网
def get_translation(content):
    logger.info('程序到达：translate.py-get_translation函数')
    # 未输入任何内容情况下的处理
    if content == "":return ['', False]
    if public.is_english(content):
        return get_translation_en(content)
    else:
        return get_translation_ch(content)
