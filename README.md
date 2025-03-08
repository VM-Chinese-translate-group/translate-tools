## VM翻译辅助工具

[![Downloads](https://img.shields.io/github/downloads/VM-Chinese-translate-group/translate-tools/total?style=flat-square&logo=github)](https://github.com/VM-Chinese-translate-group/translate-tools/releases/)
[![Last Version](https://img.shields.io/github/release/VM-Chinese-translate-group/translate-tools/all.svg?style=flat-square)](https://github.com/VM-Chinese-translate-group/translate-tools/releases/)
[![License](https://img.shields.io/github/license/VM-Chinese-translate-group/translate-tools?style=flat-square)](LICENSE)

[![官网](https://img.shields.io/badge/官网-介绍-blue?style=flat-square)](https://vmct-cn.top/tools)

所有工具均完全免费且开源，一切为了社区发展。

# FTB任务颜色字符合法检查

用于检查翻译后的语言文件中是否存在FTB任务`&`颜色字符后面的数字或字母丢失的问题。这会导致任务无法正常显示。

可以选择一个json文件路径或目录，会检查所有json文件内的颜色字符是否合法。

![](/ftbq_color_check/preview.png)

- 支持彩色日志信息。错误信息为红色，键名为青色，文件名为蓝色，通过检查为绿色。
- 支持排除各类转义符，精准检查到真正的错误
- 支持导出错误报告为html网页，支持暗色模式
- 支持检查单个或整个目录的json文件
- 支持检查json本身格式问题
- 检查错误后会显示具体译文内容，出错位置和对应的键名

效果预览：
```
文件: C:\Users\Administrator\Downloads\CNPack\kubejs\assets\integrateddynamics\lang\zh_cn.json
键: info_book.integrateddynamics.tutorials.theValueOfOperators.text4
值: &2运算符&0有很多其他的操作，例如&谓词&r合取，翻转&2运算符&0参数，以及关于&7列表&0的更多操作……
错误: '&'后包含非法字符 '谓'
```

# Paratranz译文同步工具

批量上传多个文件到Paratranz翻译平台，同时支持下载译文到本地。

使用相关功能需要有Paratranz的项目id和有对应权限用户的token，可在Paratranz个人主页查看。

## snbt json 互转工具

用于将FTB任务在mc1.21+新加入的snbt语言文件文件与json格式互转，便于导入翻译平台进行翻译。

输入一个文件路径或目录，会按照选择的模式转换所有文件

- 支持彩色提示信息
- 支持将语言文件导入翻译平台
- 支持转换单个或整个目录的文件
- 支持 snbt json 互转

## 下载

请在[Release页面](https://github.com/VM-Chinese-translate-group/translate-tools/releases)找到下载不同工具的对应页面

## 构建

1. 安装 `Python` 环境

2. 构建（成品为对应系统的可执行文件）

FTBQ颜色字符检查：
```bash
    pip install pyinstaller
    pip install -r ftbq_color_check/requirements.txt
    python -m PyInstaller -F -n FTBQ-Color-Check ftbq_color_check/main.py
```

Paratranz译文同步工具：
```bash
    pip install pyinstaller
    pip install -r paratranz_sync/requirements.txt
    python -m PyInstaller paratranz_sync/main.spec
```

snbt json 互转工具：
```bash
    pip install pyinstaller
    pip install -r snbt_json_converter/requirements.txt
    python -m PyInstaller -F -n snbt-json-converter snbt_json_converter/main.py
```

## 星标

支持开发者的最简单方式是点击页面顶部的星标（⭐）。

<p style="text-align: center;">
    <a href="https://api.star-history.com/svg?repos=VM-Chinese-translate-group/translate-tools&Date">
        <img alt="start" width=50% src="https://api.star-history.com/svg?repos=VM-Chinese-translate-group/translate-tools&Date"/>
    </a>
</p>