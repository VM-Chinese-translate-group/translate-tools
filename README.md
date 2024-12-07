## VM翻译辅助工具

[![Downloads](https://img.shields.io/github/downloads/VM-Chinese-translate-group/translate-tools/total?style=flat-square&logo=github)](https://github.com/VM-Chinese-translate-group/translate-tools/releases/)[![Last Version](https://img.shields.io/github/release/VM-Chinese-translate-group/translate-tools/all.svg?style=flat-square)](https://github.com/VM-Chinese-translate-group/translate-tools/releases/)[![License](https://img.shields.io/github/license/VM-Chinese-translate-group/translate-tools?style=flat-square)](LICENSE)

[![官网](https://img.shields.io/badge/官网-介绍-blue?style=flat-square)](https://vmct-cn.top/tools)

所有工具均完全免费且开源，一切为了社区发展。

# FTBQ 颜色字符检查

用于检查翻译后的语言文件中是否存在FTB任务&颜色字符后面的数字或字母丢失的问题。这会导致任务无法正常显示。

输入一个json路径，会检查颜色字符是否合法。

- 支持彩色提示信息。报错为红色，通过为绿色。
- 新增支持导出错误报告为txt。
- 可选是否在控制台打印详细信息
1. 开启会在控制台显示具体译文内容
2. 关闭会显示行号

开启详细信息：
```
[CNPack\kubejs\assets\ftbquest\lang\zh_cn.json] SyntaxError: Invalid character '。' after '&' at line 2705
    "不用末影龙，直接制造&6龙息&。",
```

关闭详细信息：

```
[CNPack\kubejs\assets\ftbquest\lang\zh_cn.json] SyntaxError: Invalid character after '&' at line 2705
```

注：无论选择什么，最终保存报错的文件永远为详细版本。
- 支持检查单个或整个目录的json文件，更方便。
- 支持检查json本身格式问题。

# Paratranz译文同步工具

批量上传多个文件到Paratranz翻译平台，同时支持下载译文到本地。

使用相关功能需要有Paratranz的项目id和有对应权限用户的token，可在Paratranz个人主页查看。

## 下载

<a href="https://github.com/VM-Chinese-translate-group/translate-tools/releases">请在Release页面找到下载不同工具的对应页面</a>

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

## 星标

支持开发者的最简单方式是点击页面顶部的星标（⭐）。

<p style="text-align: center;">
    <a href="https://api.star-history.com/svg?repos=VM-Chinese-translate-group/translate-tools&Date">
        <img alt="start" width=50% src="https://api.star-history.com/svg?repos=VM-Chinese-translate-group/translate-tools&Date"/>
    </a>
</p>