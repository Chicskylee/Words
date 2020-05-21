
# coding=utf-8
# =================================
# 作者声明：
# 文件用途：依版本或平台而改变的函数
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 第三方库依赖：无
# =================================
import platform
import os, sys, time
import socket
# ---------------------------------
# 用于播放音频，用于网络连接判断
try:
    # 华为mate20x-qpython2v2.2.4(python3.6.4)
    import androidhelper.sl4a as sl4a
except:
    try:
        # 小米4-qpython3v1.0(Python3.2.2)
        import sl4a
    except:
        pass
if 'sl4a' in globals():
    try:
        # 该异常会在小米4-qpython3v1.0(Python3.2.2)中引发
        # 该异常也会在华为mate20x-qpython2v2.2.4(python3.6.4)中引发
        droid = sl4a.Android()
    except socket.error:
        pass
# 用于播放音频
try:
    import pygame
except:
    pass
# =================================
# 用于记录日志
import logging
logger = logging.getLogger('main.compatible')
# =================================
# 用SPACE代替空格
SPACE = chr(160)
# ---------------------------------

# 返回程序运行的平台名称
# Windows返回：Windows
# Linux返回：Linux
# Android返回：Android
def depend_system():
    if os.name == 'nt':
        return 'Windows'
    if os.name == 'posix':
        # 尝试获取Android系统的外置内存卡
        if os.path.exists('/sdcard'):
            return 'Android'
    return 'Linux'


# ---------------------------------

# 获取手机扩展SD卡名称
# 返回形式：'E8FE-B6E3'
# 注意：不要在非Android设备上使用该函数
# 'storage'内的文件夹：'emulated'、'self'和SD卡文件夹
def get_external_sdcard_name():
    android_path = os.listdir('/storage')
    dirs_list = [i for i in android_path if i != 'emulated' and i != 'self']
    logger.info('SD List: {}'.format(dirs_list))
    if len(dirs_list) == 1:
        # 有且仅有一个外置储存卡
        sd_sdcard = dirs_list[0]
        if '-' in sd_sdcard:
            return sd_sdcard
    else:
        # 有多个不同的储存卡，此时用户可能是插入了OTG设备
        # 选择最后一个
        sd_sdcard = dirs_list[-1]
        if '-' in sd_sdcard:
            return sd_sdcard

# ---------------------------------

# 颜色函数
# 将text内容两侧增加颜色装饰符
def colorize(text, color='default'):
    colors = {'default':'\033[0m',
        'bold': '\033[1m',
        'shadow': '\033[3m',
        'underline': '\033[4m',
        'bold': '\033[5m',
        'reverse': '\033[7m',
        'concealed': '\033[8m',

        'black': '\033[30m',
        'red':'\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',

        'on_black': '\033[40m',
        'on_red': '\033[41m',
        'on_green': '\033[42m',
        'on_yellow': '\033[43m',
        'on_blue': '\033[44m',
        'on_magenta': '\033[45m',
        'on_cyan': '\033[46m',
        'on_white': '\033[47m',

        'up_green':'\033[92m',
        'up_yellow':'\033[93m',
        'up_purple':'\033[94m',
        'up_magenta':'\033[95m',
        'up_cyan':'\033[96m',
        'black':'\033[0;30;40m',  # 前景色和背景色都是黑色
        'white':'\033[0;37;47m', # 前景色和背景色都是白色
        }
    return '{}{}\033[0m'.format(colors[color], text)

# ---------------------------------

# 用于当调用终端(cmd命令行或linux Shell)时清理屏幕
# 注意：用Python shell调用时请屏蔽该函数
def clear_screen(prompt=None, pause=False, debug=False):
    if debug:
        print(colorize('程序正以debug模式运行', color='cyan'))
        logger.info('程序正以debug模式运行，因此不执行清屏命令')
        return None
    # 自动查词时屏蔽清屏命令，否则执行清屏
    # 根据不同系统选择相应的清屏命令
    system = depend_system()
    if pause:
        if prompt is not None:
            input(prompt)
        else:
            input()
    else:
        if prompt is not None:
            print(prompt)
    if system == 'Windows':
        # Windows系统使用的清屏命令
        os.system('cls')
    elif system == 'Android':
        # Linux系统使用的清屏命令
        os.system('clear')
    else:
        os.system('clear')


# =================================
# 音频的播放

# 根据文件名路径播放音频
def play_audio(filename):
    if 'droid' in globals():
        logger.info('程序成功导入droid，可用该库播放音频')
        # 播放mp3
        droid.mediaPlay(filename)
    elif 'pygame' in globals():
        logger.info('程序成功导入pygame，可用该库播放音频')
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
    else:
        print('程序无法导入sl4a和pygame，请用其它方法播放音频')
        logger.info('程序无法导入sl4a和pygame，请用其它方法播放音频')


# 播放并删除文件
def play_and_remove_audio(filename, play=True, debug=False):
    if filename is None:
        logger.info('传入的文件名为None，无法播放音频，但仍返回True')
        return True
    if play:
        logger.info(filename)
        play_audio(filename)
    if not debug:
        try:
            os.remove(filename)
            logger.debug('成功删除临时音频文件：\n{}'.format(filename))
        except Exception as e:
            logger.info('音频文件删除失败：\n{}'.format(e))
            return False
        logger.info('播放函数调用完毕')
        return True
    else:
        logger.debug('调试模式，未删除临时音频文件：\n{}'.format(filename))
        logger.info('播放函数调用完毕')
        return False

# =================================
# 对话框

# 从用户获取自定义译文
def get_custom_translation(default='',
            prompt="自定义译文",
            subprompt="注意：不同译文用**号隔开"):
    try:
        droid = sl4a.Android()
        # 从对话框中获取值
        _input = droid.dialogGetInput(prompt, subprompt, default).result
    # ConnectionRefusedError：qpython中的sl4a服务在未提前启动时引发，属于qpython的bug
    except ConnectionRefusedError:
        _input = input(prompt+':')
    return _input


