# coding=utf-8
# =================================
# 作者声明：
# 文件用途：设置配置数据
# 运行系统：Android 6.0
# 运行平台：Python 3.6.1
# 测试平台：QPython3
# 其他依赖：无
# =================================
import shutil
import pprint
# ---------------------------------
from . import log
from . import collect
from .independent import path
from .independent import emails
from .independent import public
from .independent import compatible
# =================================
# 日志记录
import logging
logger = logging.getLogger('main.config')
# =================================

# 禁止删除的数据库名称
BAN_DELETE_NAMES = ['[退出]', '[新建库]', '[删除库]',
                    'PUBLIC', 'TEMP']



# 初始化配置文件的相关操作

# {'user':{'user_name':'xxx',
#          'user_email':'xxx@xx.com',
#          'user_pwd':'xxxx',
#          'init_time':'xxxxxxxxxxxxxxxxxxxx'},
#  'datas':[(database_name, database_name_time),
#           ]}
def initialize_init():
    logger.debug('程序到达：config.py-initialize_init函数')
    filename = path.own.init_filename()
    if path.path_exist(filename):
        return True
    if public.AUTHOR:
        print('不存在用户设置，请按流程配置相应信息：')
    init = dict()
    init['user'] = dict()
    init['datas'] = list()
    # 获取用户名，用于识别用户身份
    user_name = collect.get_username()
    # 获取用户密码，用于加密用户备份字典
    user_pwd = collect.get_password()
    # 获取用户邮箱，用于给用户自己备份单词库
    user_email = collect.get_email()
    # 获取初始化配置时间，字符串，代表时间
    init_time = public.get_detail_time_now()
    init['user']['user_name'] = user_name
    init['user']['user_pwd'] = user_pwd
    init['user']['user_email'] = user_email
    init['user']['init_time'] = init_time
    # PUBLIC：所有生词的汇总生词本
    # Master：研究生入学考试生词本
    # CET6：大学英语6级生词本
    # CET4：大学英语4级生词本
    # GRE：GRE生词本
    # TEMP：临时存储生词本
    database_names = ['[退出]', '[新建库]','[删除库]', 'PUBLIC', 'TEMP']
    for database_name in database_names:
        detail_time = public.get_detail_time_now()
        # 数据库名称，数据库创建时间，数据库中单词量
        init['datas'].append((database_name, detail_time, 0))
    public.write_pickle(init, filename)
    return True


# 删除初始化配置文件
def del_init():
    logger.debug('程序到达：config.py-del_init函数')
    filename = path.user.init_filename()
    if path.path_exist(filename):
        choice_continue = collect.get_input('确认删除配置文件(*)：')
        if choice_continue == '*':
            path.os_remove(filename)
            return True
        else:
            return False
    return True


# 写入初始化配置字典，具体配置信息请参考path模块
# 注意：字典写入文件'~/Words/data/config/init.conf'
def write_init(init):
    logger.debug('程序到达：config.py-write_init函数')
    filename = path.own.init_filename()
    public.write_pickle(init, filename)


# 读取初始化配置
def read_init():
    logger.debug('程序到达：config.py-read_init函数')
    filename = path.own.init_filename()
    if not path.path_exist(filename):
        initialize_init()
    return public.read_pickle(filename)


# 获取初始配置时间
def get_init_time():
    logger.debug('程序到达：config.py-get_init_time函数')
    init = read_init()
    return init['user']['init_time']


# 获取初始配置文件中的用户名
def get_user_name():
    logger.debug('程序到达：config.py-get_user_name函数')
    init = read_init()
    return init['user']['user_name']


# 获取初始配置文件中的用户邮件地址
def get_user_email():
    logger.debug('程序到达：config.py-get_user_email函数')
    init = read_init()
    return init['user']['user_email']


# 获取可用数据库名称列表
def get_database_names():
    logger.debug('程序到达：config.py-get_database_names函数')
    init = read_init()
    database_names_list = init['datas']
    names = [name for name, _, _ in database_names_list]
    return names


# 获取可用数据库名称对应的创建时间字符串
# 返回：20位的数字字符串，代表名称创建的具体时间
# 异常返回：None， 当数据库名称不存在时返回
def get_database_time(database_name):
    logger.debug('程序到达：config.py-get_database_time函数')
    init = read_init()
    database_names_list = init['datas']
    for name, detail_time, _ in database_names_list:
        if name == database_name:
            return detail_time
    return None


# 获取数据库中的单词数量
# 返回：整数，代表该数据库中含有的单词量
# 异常返回：None， 当数据库名称不存在时返回
def get_database_words_amount(database_name):
    logger.debug('程序到达：config.py-get_database_words_amount函数')
    init = read_init()
    database_names_list = init['datas']
    for name, _, words_amount in database_names_list:
        if name == database_name:
            return words_amount
    return None


# 设置数据库中单词数量
def set_database_words_amount(database_name, words_amount):
    logger.debug('程序到达：config.py-set_database_words_amount函数')
    init = read_init()
    database_names_list = init['datas']
    for name, detail_time, amount in database_names_list:
        if name == database_name:
            index = database_names_list.index((database_name, detail_time, amount))
            init['datas'][index] = (database_name, detail_time, words_amount)
            write_init(init)
            return True
    return False



# 向数据库名称列表中添加一个数据库名称
# database_name：要添加的数据库名称
# 返回：True 或 False，表示添加结果
# 返回结果用于判断是否允许创建该数据库
def add_database_name(database_name, words_amount=0):
    logger.debug('程序到达：config.py-add_database_name函数')
    if not collect.valid_database_name(database_name):
        logger.info('数据库名称格式非法，禁止添加')
        return False
    database_names = get_database_names()
    if database_name in database_names:
        logger.info('已存在数据库名称，不需要添加：{}'.format(database_name))
        return False
    init = read_init()
    detail_time = public.get_detail_time_now()
    init['datas'].append((database_name, detail_time, words_amount))
    write_init(init)
    logger.info('已添加新数据库名称：{}'.format(database_name))
    return True


# 从数据库名称列表中删除一个数据库名称
# database_name：要删除的数据库名称
def delete_database_name(database_name):
    logger.debug('程序到达：config.py-delete_database_name函数')
    database_names = get_database_names()
    # 禁止删除的数据库名称
    if database_name in BAN_DELETE_NAMES:
        logger.info('禁止删除数据库：{}'.format(database_name))
        return False
    elif database_name in database_names:
        init = read_init()
        detail_time = get_database_time(database_name)
        words_amount = get_database_words_amount(database_name)
        init['datas'].remove((database_name, detail_time, words_amount))
        write_init(init)
        logger.info('已经删除数据库名称：{}'.format(database_name))
        return True
    else:
        logger.info('删除的数据库名称不存在！')
        return False


# 打印并返回可用数据库名称列表
def print_database_names(database_names=None):
    logger.debug('程序到达：config.py-print_database_names函数')
    if database_names is None:
        database_names = get_database_names()
    n = len(database_names)
    print('='*45)
    for index, database_name in enumerate(database_names):
        # 计算空格宽度
        prompt_width = public.real_width_in_screen(database_name)
        space_width = 15 - 3 - prompt_width
        cell = '{}{}:{}{}'.format(compatible.SPACE*space_width,
            database_name,
            compatible.SPACE if len(str(index))==1 else '',
            index)
        print(cell, end='\n' if (index+1)%3==0 else '')
    else:
        fill = '\n' if (index+1)%3 != 0 else ''
        print(fill+'='*45)
    return database_names


# =================================
# 操作配置文件

# 配置文件的初始化值形式，生成配置字典
# 返回：一个字典
def initialize_config(database_name='TEMP'):
    logger.debug('程序到达：config.py-initialize_config函数')
    filename = path.own.config_filename()
    if path.path_exist(filename):
        logger.info('配置信息已存在，修改请用set_config函数')
        return True
    # 首先检查，是否允许创建该数据库
    if database_name not in get_database_names():
        # 该名称不在数据库名称列表中，要先尝试添加
        if not add_database_name(database_name):
            # 添加失败，说明名称格式非法
            raise NameError('数据库命名非法！')
    # 名称已经存在于数据库名称列表中，可以创建配置字典
    config = dict()
    # 将用户初始信息拷贝到配置文件，用于识别用户和备份用户单词
    config['init'] = dict()
    # 用户使用本程序的用户名和初始时间
    config['init']['user_name'] = get_user_name()
    config['init']['init_time'] = get_init_time()
    # ------------------------------------
    # 数据库配置，谨慎改动
    config['database'] = dict()
    # 数据库名称，默认为'TEMP'
    config['database']['database_name'] = database_name
    # 数据库创建时间
    create_time = get_database_time(database_name)
    config['database']['create_time'] = create_time
    # 数据库配置最近修改时间
    last_time = public.get_detail_time_now()
    config['database']['last_time'] = last_time
    # 数据库单词数，初始值为0
    config['database']['words_total'] = get_database_words_amount(database_name)
    logger.debug('已生成初始化配置：\n{}'.format(pprint.pformat(config)))
    public.write_pickle(config, filename)
    return True


# 设置配置字典
def set_config(database_name='TEMP'):
    logger.debug('程序到达：config.py-set_config函数')
    filename = path.own.config_filename()
    if not path.path_exist(filename):
        logger.info('配置信息不存在，创建请用initialize_config函数')
        return None
    # 首先检查，是否允许创建该数据库
    if database_name not in get_database_names():
        # 该名称不在数据库名称列表中，要先尝试添加
        if not add_database_name(database_name):
            # 添加失败，说明名称格式非法
            raise NameError('数据库命名非法！')
    # 名称已经存在于数据库名称列表中，可以创建配置字典
    config = dict()
    # 将用户初始信息拷贝到配置文件，用于识别用户和备份用户单词
    config['init'] = dict()
    # 用户使用本程序的用户名和初始时间
    config['init']['user_name'] = get_user_name()
    config['init']['init_time'] = get_init_time()
    # ------------------------------------
    # 数据库配置，谨慎改动
    config['database'] = dict()
    # 数据库名称，默认为'TEMP'
    config['database']['database_name'] = database_name
    # 数据库创建时间
    create_time = get_database_time(database_name)
    config['database']['create_time'] = create_time
    # 数据库配置最近修改时间
    last_time = public.get_detail_time_now()
    config['database']['last_time'] = last_time
    # 数据库单词数，初始值为0
    config['database']['words_total'] = get_database_words_amount(database_name)
    logger.debug('已生成配置字典：\n{}'.format(pprint.pformat(config)))
    return config


# 将配置字典写入配置文件
# config：配置字典
# 注意：字典写入文件'~/Words/data/config/config.conf'
def write_config(config):
    logger.debug('程序到达：config.py-write_config函数')
    logger.debug('写入配置：\n{}'.format(pprint.pformat(config)))
    filename = path.own.config_filename()
    public.write_pickle(config, filename)
    logger.info('配置已写入文件')
    # 配置文件写入完毕，接下来更新用户初始信息
    database_name = config['database']['database_name']
    words_amount = config['database']['words_total']
    set_database_words_amount(database_name, words_amount)
    logger.info('初始信息已写入文件')
    return True


# 读取配置文件中的配置字典
# 注意：配置文件是一个pickle文件，其中有一个字典
# 该字典中的内容如下：
# {'init':{'user_name':xxx,
#          'init_time':xxx,  # 一旦创建，禁止更改
#             }
#  'database':{'database_name':xxx,
#              'create_time':xxx,  # 一旦创建，禁止更改
#              'last_time':xxx,
#              'words_total':xxx},
#  }
def read_config():
    logger.debug('程序到达：config.py-read_config函数')
    filename = path.own.config_filename()
    if not path.path_exist(filename):
        initialize_config(database_name='TEMP')
    config = public.read_pickle(filename)
    if not config:
        raise ValueError('配置文件中的字典是空的！')
    logger.debug('当前配置：\n{}'.format(pprint.pformat(config)))
    return config


# 修改当前配置文件中的数据库名称
# database_name：数据库名称，字符串
# 注意：修改database_name，将更新整个配置文件
# 注意：函数修改文件'~/Words/data/config/config.conf'
def set_database_name(database_name):
    logger.debug('程序到达：config.py-set_database_name函数')
    # 首先检查，是否允许创建该数据库
    if database_name not in get_database_names():
        logger.debug('数据库名称不在初始化配置列表中，请先添加名称：{}'.format(database_name))
        return False
    config = set_config(database_name)
    write_config(config)
    return True


# 修改(设置)已经存在的配置文件中的配置信息
# database_name：数据库名称，字符串
# words_total：当前数据库中的单词总数，整数
# 注意：修改words_total，其它值不会改变
# 注意：如果当前数据库名称不是database_name，将修改失败
def set_words_total(database_name, words_total):
    logger.debug('程序到达：config.py-set_words_total函数')
    config = read_config()
    # 下面具体修改各项内容
    if config['database']['database_name'] != database_name:
        logger.debug('传入数据库名称与当前数据库名称不一致，不可修改单词量')
        return False
    if isinstance(words_total, int):
        config['database']['words_total'] = words_total
        # 数据库配置最近修改时间
        last_time = public.get_detail_time_now()
        config['database']['last_time'] = last_time
        logger.debug('单词总数修改为：{}'.format(words_total))
    # 检查配置是否被修改，如果修改了，就写入文件
    old_config = read_config()
    if config == old_config:
        logger.info('配置文件未改变')
        return False
    # 配置已经更改
    write_config(config)
    return True


# 获取当前单词库名称
def get_database_name():
    logger.debug('程序到达：config.py-get_database_name函数')
    config = read_config()
    database_name = config['database']['database_name']
    logger.debug('当前数据库名称：{}'.format(database_name))
    return database_name


# 获取当前数据库中的单词总条数
def get_database_words_total():
    logger.debug('程序到达：config.py-get_database_words_total函数')
    config = read_config()
    logger.debug('当前配置：\n{}'.format(pprint.pformat(config)))
    words_total = config['database']['words_total']
    logger.info('当前配置文件中的单词量：{}'.format(words_total))
    return words_total


# 获取初始化配置信息的init_time
def get_config_init_time():
    logger.debug('程序到达：config.py-get_config_init_time函数')
    config = read_config()
    return config['init']['init_time']


# 引导用户创建一个配置文件字典，并返回创建的字典
# choice_create：当指定为True时才真正创建配置文件
# 注意：应该禁止创建超过13(不含)个英文长度的数据库名称
def create_config(choice_create=True):
    logger.debug('程序到达：config.py-create_config函数')
    if not choice_create:
        # 无配置文件不能查单词，所以必须退出程序！
        public.exit_program(prompt='没有完成配置，已退出(Enter)：', pause=True)
    # 该函数将在未正确获取database_name时执行退出函数
    database_name = collect.get_database_name(prompt=None)
    config = set_config(database_name)
    # 将用户设置的配置内容写入文件
    write_config(config)
    logger.info('成功新建数据库：{}'.format(database_name))
    return config


# 在主程序中给用户打印配置文件的提示内容
# n：一行内容的屏幕总宽度
def print_config(n=45):
    logger.debug('程序到达：config.py-print_config函数')
    # 当前数据库名称
    database_name = get_database_name()
    # 当前数据库的单词总数
    words_total = get_database_words_total()
    # 计算需要打印的空格数
    prompt_width = public.real_width_in_screen(database_name+str(words_total))
    space_width = n - 16 - prompt_width
    # 打印给用户查看的内容
    result = '词库名称：{}{}已有：{}'.format(database_name, compatible.SPACE*space_width, words_total)
    print(result)


# =================================
# 数据库文件的相关操作

def delete_database(database_name):
    logger.debug('程序到达：config.py-delete_database函数')
    # 删除一个数据库
    logger.info('用户进入删除数据库操作！！！')
    print('注意：该操作将删除数据库，且无法恢复！')
    choice = collect.get_input('删除库{}中所有数据(确认*)'.format(database_name))
    if choice == '*':
        database_path = path.user.word(database_name)
        # 要求用户验证密码才可以继续删除
        if database_name not in BAN_DELETE_NAMES:
            logger.info('用户删除数据库目录及其文件：{}'.format(database_path))
            shutil.rmtree(database_path)
            return True
        else:
            # 程序不应该走到这里，
            # 如果程序走到这里了，说明历史上的修改导致用户可以删除禁止删除的数据库了
            print('禁止删除数据库：{}'.format(database_name))
            raise IndexError('程序不应该走到这里，请通知开发者！')
    else:
        return False


# 将删除的数据库中的单词添加同步到综合数据库
def synchronize_words(database_name):
    logger.debug('程序到达：config.py-synchronize_words函数')
    pass


# =================================

# 检查用户配置信息
def check_config():
    logger.debug('程序到达：config.py-check_config函数')
    # 检查用户配置
    configuration = read_config()
    # 检查开发者配置：该程序在当public.AUTHOR=True时，如果不存在签名文件，触发退出函数
    author_config = emails.read_author_config()
    return True

# =================================


# 引导用户操作配置文件和数据库文件
# enabled：当且仅当其值为'*'时被激活
# 返回：True 或 False，用来表示是否真正修改了数据库
def main(enabled, debug=False):
    logger.debug('程序到达：config.py-main函数')
    if enabled != '*':
        return False
    # 引导用户操作配置文件和数据库文件
    compatible.clear_screen(debug=public.DEBUG)
    db_names = get_database_names()
    print_database_names(database_names=db_names)
    current_db_name = get_database_name()
    print('当前数据库名称：{}'.format(current_db_name))
    index = collect.get_input(prompt='正在设置数据库，请选择相应数字：')
    try:
        index = int(index)
    except ValueError:
        index = -1
    if (index >= len(db_names)) or (index < 0):
        logger.info('用户修改数据库名称时胡乱输入了内容：{}'.format(index))
        compatible.clear_screen(debug=public.DEBUG)
        print('选择错误，未更改数据库')
        print_config()
        return False
    # 用户输入了正确的序号，才应该进入接下来的代码
    logger.info('用户选择：{}'.format(db_names[index]))
    if db_names[index] == current_db_name:
        compatible.clear_screen(debug=public.DEBUG)
        print_config()
        return False
    elif db_names[index] == '[退出]':
        compatible.clear_screen(debug=public.DEBUG)
        print_config()
        return False
    elif db_names[index] not in ['[退出]', '[新建库]', '[删除库]']:
        # 将数据库设置为用户选择的数据库
        set_database_name(database_name=db_names[index])
        compatible.clear_screen(debug=public.DEBUG)
        print_config()
        return True
    elif db_names[index] == '[新建库]':
        logger.info('用户要新建数据库')
        create_config(choice_create=True)
        compatible.clear_screen(debug=public.DEBUG)
        print_config()
        return True
    elif db_names[index] == '[删除库]':
        logger.info('用户要删除数据库')
        database_name = collect.get_input('请输入要删除的数据库名称：')
        # 首先从数据库名称列表中删除数据库名称
        # 注意：只有非禁止删除的数据库名称才可以删除
        delete_result = delete_database_name(database_name)
        logger.info('删除结果：{}'.format(delete_result))
        if (database_name == current_db_name) and delete_result:
            # 将配置文件指向临时数据库：'TEMP'
            set_database_name(database_name='TEMP')
            # 接着，将要删除的数据库中的单词同步到综合数据库
            synchronize_words(database_name)
            # 最后删除数据库
            if delete_database(database_name):
                compatible.clear_screen(debug=public.DEBUG)
                print('已经删除数据库文件：{}'.format(database_name))
            else:
                compatible.clear_screen(debug=public.DEBUG)
                print('没有删除数据库文件：{}'.format(database_name))
            print('已删除数据库名称：{}，数据库被临时指向：TEMP'.format(database_name))
            print_config()
            # 更新配置文件中的单词数量的数据
            # 暂时不选择在此时更新
            return True
        elif database_name != current_db_name and delete_result:
            compatible.clear_screen(debug=public.DEBUG)
            print('数据库名称与当前数据库不对应，不需要删除配置文件')
            # 接着，将要删除的数据库中的单词同步到综合数据库
            synchronize_words(database_name)
            # 最后删除数据库
            if delete_database(database_name):
                compatible.clear_screen(debug=public.DEBUG)
                print('已经删除数据库文件：{}'.format(database_name))
            else:
                compatible.clear_screen(debug=public.DEBUG)
                print('没有删除数据库文件：{}'.format(database_name))
            print_config()
            return False
        elif not delete_result:
            compatible.clear_screen(debug=public.DEBUG)
            print('禁止删除数据库：{}，当前数据库仍为：{}'.format(database_name, get_database_name()))
            # 没有删除配置文件
            # 可能原因：配置文件禁止删除或当前配置文件与数据库名称不对应
            return False
        else:
            compatible.clear_screen(debug=public.DEBUG)
            logger.info('程序不应该来到这里，请通知开发者！')
            print('程序不应该来到这里，请通知开发者！')
            return False
    else:
        compatible.clear_screen(debug=public.DEBUG)
        logger.info('程序不应该来到这里，请通知开发者！')
        print('程序不应该来到这里，请通知开发者！')
        return False

