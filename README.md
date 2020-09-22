# Words是在QPython3上面使用的手机中英文翻译工具


## 它具有以下已完成的功能

### 0.支持中英文互译

### 1.支持英文离线翻译

### 2.支持单词本保存

### 3.支持单词分类存储

### 4.支持单词的导入和导出

### 5.支持单词备份

### 6.支持自动播放单词


### 注意：请输入 *h 或 *help 获取部分帮助

## 依赖第三方库

### 0.requests

### 1.Qpython自带的sl4a

### 2.如果要支持其它平台，最多只需要修改compatible.py文件，如用pygame取代sl4a




# 配置说明

### 两种运行方式二选其一即可

## 一、非作者模式下运行

### 在此模式下运行，程序不会将异常日志发送给开发者，也不会备份用户的词库到用户的邮箱。

### 请将 words/packages/core/independent/public.py 中的参数 AUTHOR 设置为 False


## 二、作者模式下运行

### 在此模式下运行，程序可能会将异常发送给开发者用于修复异常，同时也将帮助用户定期备份词库防止丢失。

### 请事先准备好文件名为words/own/conf/.author.conf的pickle文件

### 该文件内容为开发者邮箱及其密码格式为：

### {'pwd': '邮箱密码', 'addr': '邮箱号'}



# 其它

### gitee地址：https://gitee.com/chicsky/words

### github地址：https://github.com/Chicskylee/Words 因已弃坑github，将不再在此处更新

### 其它具体问题请联系：chic.sky.lee@gmail.com
