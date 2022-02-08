#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_unicode.py
# @DATE: 2022/01/16 Sun
# @TIME: 11:06:09
#
# @DESCRIPTION: 共通包 字符判断


import re


"""
@description: 判断是否为中文
-------
@param:
-------
@return:
"""
def is_chinese(char):
    if (char >= "\u4e00" and char <= "\u9fa5"):
        return True
    else:
        return False

"""
@description: 判断是否为英文字符
-------
@param:
-------
@return:
"""
def is_alphabet(char):
    if ((char >= "\u0041" and char <= "\u005a")
            or (char >= "\u0061" and char <= "\u007a")):
        return True
    else:
        return False

"""
@description: 判断是否为数字
-------
@param:
-------
@return:
"""
def is_number(char):
    if (char >= "\u0030" and char <= "\u0039"):
        return True
    else:
        return False

"""
@description: 判断字符串中是否只有数字和字母
-------
@param:
-------
@return:
"""
def is_all_alphabet_and_number(_string):
    len_after_filter = re.sub(
        u"([^\u0041-\u005a\u0061-\u007a\u0030-\u0039])", "", _string)
    if (len(len_after_filter) == len(_string)):
        return True
    else:
        return False

"""
@description: 获取字符串中全角和半角字符的数量
-------
@param:
-------
@return:
"""
def get_true_length(_string):
    true_length = 0
    for char in _string:
        if (char >= "\u0000" and char <= "\u0019"):
            true_length += 0
        elif(char >= "\u0020" and char <= "\u1FFF"):
            true_length += 1
        elif(char >= "\u2000" and char <= "\uFF60"):
            true_length += 2
        elif(char >= "\uFF61" and char <= "\uFF9F"):
            true_length += 1
        else:
            true_length += 2
    return true_length


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    _string = "全角字符，。abc0123456,./™★"
    print(get_true_length(_string))
    print(is_all_alphabet_and_number(_string))