# coding=utf8
# =================================
# 声明：
# 用途：
# 系统：Android 6.0, 4.4, 8.0
# 系统：Window 7
# 版本：Python 3.6, 3.2
# 平台：QPython3
# 依赖包：pygame(Window使用时)
# =================================
from packages import manager
# ---------------------------------
from packages.core import log
from packages.core.independent import public
# =================================
# 日志记录
logger = log.get_logger(log_name='main', log_level=None)
# =================================


@public.catch_exception
def cage_main():
    logger.debug('程序到达：main.py-cage_main函数')
    logger.info('\n'+'*'*45)
    try:
        manager.main()
    except KeyboardInterrupt as e:
        public.exit_program(prompt='已退出！')
        return None
    except Exception as e:
        print('出现严重异常，程序正在强制退出，请稍后……')
        logger.fatal(e, exc_info=True)
        log.send_log(e)
        print('已退出！')


# 等待完成的功能：
# 02.导出单词到CSV
# 06.允许从CSV导入单词
# 08.对于复习单词，可以分组复习、整体复习、导出个别单词复习
# 11.允许修改(或删除)单词音频(外部提供单词发音)
if __name__ == '__main__':
    cage_main()

