# coding=utf-8
# =================================
# 作者声明：
# 文件用途：用有道翻译爬取句子和中文译文
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 其他依赖：无
# 运行注意：在本文件中的翻译方法需要连网
# =================================
import re
import urllib.request
import urllib.error
import http
# ---------------------------------
from ..core.independent import path
from ..core.independent import public
from ..core.independent import compatible
# =================================
# 日志记录
import logging
logger = logging.getLogger('main.translate_expend')
# =================================
# 异常输入：Web Server Gateway Interface
# 上面这个输入没有译文，但是有道上有译文
# 网址：http://fanyi.youdao.com/
# =================================
# 获取待翻译内容的url
# 返回：字符串，代表url
def get_url(content):
    logger.debug('程序到达：translate_expend.py-get_url函数')
    #url_template = 'http://www.youdao.com/w/eng/{content}'
    url_template = 'http://dict.youdao.com/search?q={content}&keyfrom=new-fanyi.smartResult'
    url = url_template.format(content=content)
    return url


# 将html写入文件
def write_html(html, content):
    logger.debug('程序到达：translate_expend.py-write_html函数')
    filename = path.user.html_filename(name=content)
    public.write(html, filename)


# 读取html文件内容
def read_html(content):
    logger.debug('程序到达：translate_expend.py-read_html函数')
    filename = path.user.html_filename(name=content)
    if not path.path_exist(filename):
        return None
    return public.read(filename)


# 下载html文件后返回文件内容
# 注意：暂时只用于获取有道翻译的网页内容
@public.retry_decorator(prompt='网络超时中断，正在重试...', force_return=True)
def get_html(url):
    logger.debug('程序到达：translate_expend.py-get_html函数')
    try:
        response = urllib.request.urlopen(url, timeout=5)
    except urllib.error.URLError:
        logger.error('有道翻译程序网络连接失败，翻译终止', exc_info=True)
        print('-----(expend en)请连网翻译')
        return None
    except urllib.error.HTTPError:
        logger.error('注意！有道翻译已被禁用，请及时更改代码！', exc_info=True)
        return None
    except http.client.BadStatusLine:
        logger.error('太长了，有道翻译不能成功请求', exc_info=True)
        return None
    except ConnectionResetError as e:
        logger.error('连接被重置，请更改爬虫代码！\n异常提示：{}'.format(e), exc_info=True)
        return None
    # 还可能遇到网络连接超时异常，由装饰器处理
    html = response.read().decode('UTF-8')
    return html


# 解析网页的内容区域
def parse_scontainer(html):
    logger.debug('程序到达：translate_expend.py-parse_scontainer函数')
    pattern = r'<!-- 内容区域 -->(.*?)<!-- 内容区域 -->'
    scontainer = re.findall(pattern, html, re.S)
    if not scontainer:
        return None
    return scontainer[0]

# =================================

# 获得基础解释：单词、音标、词性及解释、其它内容
# 返回：[str:单词,
#       list:[(str:'英', str:音标), (str:'美', str:音标)],
#       list:[str:解释一,...],
#       list:[str:其他内容]]
# 返回：[str:单词,
#       list:[(str:'英(或美)', str:音标)],
#       list:[str:解释一,...],
#       list:[str:其他内容]]
# 返回：任何未获取成功的值将被替换成None，即 [None, None, None, None]
# 返回：所有值都是None，则返回 None
def parse_basis(scontainer):
    logger.debug('程序到达：translate_expend.py-parse_basis函数')
    # 单词
    pattern_word = r'<span class="keyword">(.*?)</span>'
    word = re.findall(pattern_word, scontainer, re.S)
    word = word[0] if word else None
    # 音标：有可能只有一种音标，比如monopolize只有美音标，这是有道的锅，不赖我(•̀⌄•́)
    pattern_pronounce = r'<span class="pronounce">.*?(英|美).*?<span class="phonetic">(.*?)</span>'
    soundmark = re.findall(pattern_pronounce, scontainer, re.S)
    soundmark = soundmark if soundmark else None
    # 词性及其解释
    pattern_container = r'<div class="trans-container">\s*<ul>.*?</ul>.*?</div>.*?</div>'
    container = re.findall(pattern_container, scontainer, re.S)
    #print(container)
    if len(container) > 1:
        raise IndexError('注意container的长度：{}'.format(len(container)))
    if container:
        container = container[0]
    elif any([word, soundmark, None, None]):
        return [word, soundmark, None, None]
    else:
        return None
    translation = re.findall(r'<li>(.*?)</li>', container, re.S)
    # 额外的一些解释，如现在分词、过去式、过去分词；比较级、最高级等
    additional = re.findall(r'<p class="additional">(.*?)</p>', container, re.S)
    # 去除两端和内部的空白符
    pattern_blank = re.compile(r'(\n\s*)')
    additional = [pattern_blank.sub(' ', ad) for ad in additional]
    if any([word, soundmark, translation, additional]):
        return [word, soundmark, translation, additional]
    else:
        return None


# 获得词组及其解释
# 返回：[(str:原文, str:译文), ...]
# 返回：None
def parse_phrases(scontainer):
    logger.debug('程序到达：translate_expend.py-parse_phrases函数')
    # 缩小范围：获得所有词组的div
    pattern_phrases_container = r'<div id="wordGroup".*?>.*?</div>'
    phrases_container = re.findall(pattern_phrases_container, scontainer, re.S)
    if phrases_container:
        phrases_container = phrases_container[0]
    else:
        return None
    # 再次缩小范围：获得每个词组的p
    pattern_phrases = r'<p class="(?:wordGroup|wordGroup collapse)">\s*<span class="contentTitle"><a .*?>(.*?)</a>\s*</span>\s*(.*?)\s*(?:\<a.*?\>.*?\</a\>)*\s*</p>'
    phrases = re.findall(pattern_phrases, phrases_container, re.S)
    # 减少其中的空白字符
    pattern_blank = re.compile(r'\s+')
    phrases = [(phrase, pattern_blank.sub(' ', translation)) for phrase, translation in phrases]
    return phrases


# 获得网络翻译中的词组及其解释
# 返回：[(str:原文, str:译文), ...]
# 返回：None
# 注意：这部分代码较多，属于正则表达式没有学好，等学好了再重写
# 争取下次重写后，一个匹配模式完成所有匹配(而不是现在的4个)
def parse_web_phrases(scontainer):
    logger.debug('程序到达：translate_expend.py-parse_web_phrases函数')
    # 缩小范围：获得所有词组的div
    pattern_web_phrases_container = r'<div id="webPhrase".*?>\s*<div class="title">短语</div>(.*?)</div>'
    web_phrases_container = re.findall(pattern_web_phrases_container, scontainer, re.S)
    if not web_phrases_container:
        return None
    web_phrases_container = web_phrases_container[0]
    # 再次缩小范围：获得每个词组的p
    pattern_web_phrases = r'<p class="(?:wordGroup|wordGroup collapse)">\s*<span class="contentTitle"><a .*?>(.*?)</a>\s*</span>\s*(.*?)\s*</p>'
    web_phrases = re.findall(pattern_web_phrases, web_phrases_container, re.S)
    # 去除内部的空白符
    pattern_blank = re.compile(r'\n\s*')
    web_phrases = [(phrs, pattern_blank.sub(' ', tslt)) for phrs, tslt in web_phrases]
    # 去除灰色标记标签
    pattern_gray = re.compile(r'<span class=gray>|</span>')
    web_phrases = [(phrs, pattern_gray.sub('', tslt)) for phrs, tslt in web_phrases]
    return web_phrases


# 解析有道翻译(机器翻译)结果
# 返回：一个字符串
# 返回：None，代表不存在翻译结果
def parse_youdao_trans_en(scontainer):
    logger.debug('程序到达：translate_expend.py-parse_youdao_trans_en函数')
    pattern = r'<div id="fanyiToggle">\s*<div class="trans-container">\s*<p>.*?</p>\s*<p>(.*?)</p>\s*<p>.*?<a.*?>'
    trans = re.findall(pattern, scontainer, re.S)
    if trans:
        return trans[0]
    return None


# 获得异常结果div
# 返回：None，有译文的情况下
# 返回：非空列表,[(str:可能的原文, str:可能的原文的翻译), ...]
def parse_error_wrapper(scontainer):
    logger.debug('程序到达：translate_expend.py-parse_error_wrapper函数')
    pattern_error_wrapper = r'<div class="error-wrapper">(.*?)</div>'
    error_wrapper = re.findall(pattern_error_wrapper, scontainer, re.S)
    if not error_wrapper:
        return None
    error_wrapper = error_wrapper[0]
    pattern_typo_rel = r'<p class="typo-rel">\s*<span class="title"><a .*?>(.*?)</a>\s*</span>\s*(.*?)\s*</p>'
    typo_rel = re.findall(pattern_typo_rel, error_wrapper, re.S)
    return typo_rel

# =================================

# 获得基础解释
# 返回：[[原文, 拼音, [(词性, 译文), ], ...], [(词语辨析英文, 词语辨析解释)]]
def parse_basis_ch(scontainer):
    logger.debug('程序到达：translate_expend.py-parse_basis_ch函数')
    # 单词：中文通用
    pattern_word = r'<span class="keyword">(.*?)</span>'
    word = re.findall(pattern_word, scontainer, re.S)
    word = word[0] if word else None
    # 拼音
    pattern_pronounce = r'<span class="phonetic">(.*?)</span>'
    soundmark = re.findall(pattern_pronounce, scontainer, re.S)
    soundmark = soundmark[0] if soundmark else None
    # 词性及其英文
    pattern_container = r'<div class="trans-container">\s*<ul>.*?</ul>.*?</div>.*?</div>'
    container = re.findall(pattern_container, scontainer, re.S)
    #print(container)
    if len(container) > 1:
        raise IndexError('注意container的长度：{}'.format(len(container)))
    if container:
        container = container[0]
    elif any([word, soundmark, None]):
        return [word, soundmark, None]
    else:
        return None
    pattern_translations = r'<p class="wordGroup">(.*?)</p>'
    translations = re.findall(pattern_translations, container, re.S)
    if translations:
        property_and_tslts = list()
        for translation in translations:
            # 词性
            pattern_tslt_property = r'<span style=.*?>(\S+\.)</span>'
            tslt_property = re.findall(pattern_tslt_property, translation, re.S)
            tslt_property = tslt_property[0] if tslt_property else None
            # 单词
            pattern_tslts = r'<span class="contentTitle"><a class=.*?>(.*?)</a>\s*(?:<span style=.*?> ;</span>\s*)?</span>\s*'
            tslts = re.findall(pattern_tslts, translation, re.S)
            property_and_tslts.append((tslt_property, tslts))
    return [word, soundmark, property_and_tslts]


# 获取网络释义
# 返回：列表
def parse_web_translation_ch(scontainer):
    logger.debug('程序到达：translate_expend.py-parse_web_translation_ch函数')
    pattern_web_translation = r'<div class="wt-container wt-collapse">\s*<div class="title">\s*<a.*?>.*?</a>\s*<span.*?>\s*(.*?)</span>\s*</div>'
    web_translation = re.findall(pattern_web_translation, scontainer, re.S)
    # 删除专有名词排版代码
    pattern_compose = re.compile(r'<span class=gray>(\[.*?\])</span>\s*(.*?)')
    web_translation = [pattern_compose.sub(r'\1\2', translation) for translation in web_translation]
    return web_translation


# 解析词语辨析
def parse_words_analysis_ch(scontainer):
    logger.debug('程序到达：translate_expend.py-parse_words_analysis_ch函数')
    pattern_words_analysis = r'<div class="wordGroup">\s*<p>\s*<span class="contentTitle">\s*<a class=.*?>(.*?)</a>\s*</span>\s*(.*?)\s*</p>\s*</div>'
    words_analysis = re.findall(pattern_words_analysis, scontainer, re.S)
    #print('打印词语辨析：', words_analysis)
    pattern_blank = re.compile(r'(\n\s*|<p>|</p>)')
    words_analysis = [(word, pattern_blank.sub(' ', analysis)) for word, analysis in words_analysis]
    return words_analysis


# 解析有道翻译结果
# 返回：一个字符串
# 返回：None，代表不存在翻译结果
def parse_youdao_trans(scontainer):
    logger.debug('程序到达：translate_expend.py-parse_youdao_trans函数')
    pattern = r'<div id="fanyiToggle">\s*<div class="trans-container">\s*<p>.*?</p>\s*<p>(.*?)</p>\s*<p>.*?<a.*?>'
    trans = re.findall(pattern, scontainer, re.S)
    if trans:
        return trans[0]
    return None


# =================================

def youdao_translate_ch(content):
    logger.debug('程序到达：translate_expend.py-Youdao_translate_ch函数')
    # 获取中文原文的翻译内容
    logger.info('程序进入youdao_translate_ch()')
    content_encoded = public.str_encode(content)
    url = get_url(content_encoded)
    # 获取网页内容，优先获取本地网页内容
    html = read_html(content) or get_html(url)
    if html is None:
        print('请检查网络连接是否正常……')
        return None
    # 记录下载的html文件内容
    write_html(html, content)
    # 解析翻译的内容区域
    scontainer = parse_scontainer(html)
    # 有道翻译返回的异常：代表原文可能不正确，不存在译文
    error_wrapper = parse_error_wrapper(scontainer)
    if error_wrapper is not None:
        print(compatible.colorize('不存在译文，你是不是要找：', color='magenta'))
        for i in error_wrapper:
            print('  '+' '.join(i))
        #return None
    basis = parse_basis_ch(scontainer)
    words_analysis = parse_words_analysis_ch(scontainer)
    youdao_trans = parse_youdao_trans(scontainer)
    web_translation = parse_web_translation_ch(scontainer)
    return {'basis':basis, 'analysis':words_analysis, 'web_translation':web_translation, 'youdao_trans':youdao_trans}


# 获取英文原文的翻译内容
# 返回：字典，如果存在译文的情况下
# 返回：None，有道翻译认为译文错误
def youdao_translate_en(content):
    logger.debug('程序到达：translate_expend.py-youdao_translate_en函数')
    logger.info('程序进入英文扩展翻译函数youdao_translate_en()')
    url = get_url(content)
    html = read_html(content) or get_html(url)
    if html is None:
        print('请检查网络连接是否正常……')
        return None
    # 记录下载的html文件内容
    write_html(html, content)
    # 解析翻译的内容区域
    scontainer = parse_scontainer(html)
    # 有道翻译返回的异常：代表原文可能不正确，不存在译文
    error_wrapper = parse_error_wrapper(scontainer)
    if error_wrapper is not None:
        print('不存在译文，你是不是要找：')
        for i in error_wrapper:
            print('\t'+' '.join(i))
        return None
    basis = parse_basis(scontainer)
    phrases = parse_phrases(scontainer)
    web_phrases = parse_web_phrases(scontainer)
    youdao_trans = parse_youdao_trans_en(scontainer)
    return {'basis':basis, 'phrases':phrases,
            'web_phrases':web_phrases,
            'youdao_trans':youdao_trans}


def view_en(result):
    logger.debug('程序到达：translate_expend.py-view_en函数')
    if result is None: return None
    basis = result['basis']
    phrases = result['phrases']
    web_phrases = result['web_phrases']
    youdao_trans = result['youdao_trans']
    if not any([basis, phrases, web_phrases, youdao_trans]):
        print('翻译不存在')
        return None
    if basis:
        # 音标
        # 音标可能是：[(str:'英', str:音标), (str:'美', str:音标)]
        # 也可能是：[(str:'英(或美)', str:音标)]
        soundmarks = basis[1]
        if not soundmarks:
            # 没有音标，返回是None
            logger.info('不存在音标：{}'.format(soundmarks))
        elif len(soundmarks) == 2:
            logger.info('soundmarks：{}'.format(soundmarks))
            [(uk, uk_sdmk), (us, us_sdmk)] = basis[1]
            print(uk, uk_sdmk, us, us_sdmk)
        elif len(soundmarks) == 1:
            logger.info('soundmarks：{}'.format(soundmarks))
            [(uk_or_us, uk_or_us_sdmk)] = soundmarks
            print(uk_or_us, uk_or_us_sdmk)
        else:
            logger.info('不存在音标：{}'.format(soundmarks))
        # 译文
        if basis[2]:
            for tslt in basis[2]:
                print(tslt)
        # 其它内容，如比较级、最高级；过去式、过去分词等
        if basis[3]:
            print(basis[3][0])
    if youdao_trans:
        print(compatible.colorize('机器翻译结果：', color='cyan'))
        print(youdao_trans)
    if phrases:
        print(compatible.colorize('相关短语：', color='cyan'))
        for index, phrase in enumerate(phrases, start=1):
            ph, tr = phrase
            print(format(index, '02d'), ph, tr)
    if web_phrases:
        print(compatible.colorize('网络短语：', color='cyan'))
        for index,  web_phrase in enumerate(web_phrases, start=1):
            ph, tr = web_phrase
            print(format(index, '02d'), ph, tr)


def view_ch(result):
    logger.debug('程序到达：translate_expend.py-view_ch函数')
    basis = result['basis']
    analysis = result['analysis']
    web_translation = result['web_translation']
    youdao_trans = result['youdao_trans']
    if not any([basis, analysis, web_translation, youdao_trans]):
        print('翻译不存在')
        return None
    if basis:
        if any([basis[1], basis[2]]):
            print('基本释义：')
        #word = basis[0]
        #print(word)
        soundmark = basis[1]
        if soundmark:
            print(soundmark)
        tslt = basis[2]
        if tslt:
            # p是词性，t是译文
            for p, t in tslt:
                # p可能是None
                print(p if p else str(), '; '.join(t))
    if web_translation:
        print('网络释义：', end='')
        print('; '.join(web_translation))
    if analysis:
        print('单词辨析：')
        for i, a in enumerate(analysis, start=1):
            print(format(i, '02d')+' '+' '.join(a))
    if youdao_trans:
        print('机器翻译结果：')
        print(youdao_trans)


def youdao_translate(content):
    logger.debug('程序到达：translate_expend.py-youdao_translate函数')
    # 该代码仅用来获取翻译内容，并不存储数据库
    if public.is_english(content):
        # 获取英文译文
        result = youdao_translate_en(content)
        if result is None:
            # 可能网络连接不正常，已给出提示
            return None
        view_en(result)
    # 获取中文译文
    else:
        result = youdao_translate_ch(content)
        if result is None:
            # 可能网络连接不正常，已给出提示
            return None
        view_ch(result)
    if public.is_english(content):
        # 获取英文译文
        result = youdao_translate_en(content)
        if result is None:
            # 可能网络连接不正常，已给出提示
            return None
        view_en(result)
    # 获取中文译文
    else:
        result = youdao_translate_ch(content)
        if result is None:
            # 可能网络连接不正常，已给出提示
            return None
        view_ch(result)


