#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_cryptography.py
# @DATE: 2021/07/24 周六
# @TIME: 13:45:47
#
# @DESCRIPTION: 共同包 简易密码模块


import sys
import datetime
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config


"""
@description: 获得当天的日期 YYMMDD 格式作为默认加密密钥
-------
@param:
-------
@return:
"""
def get_default_key():
    today = datetime.date.today()
    return int(today.strftime('%Y%m%d'))

"""
@description: 将字符串转为数字
-------
@param:
-------
@return:
"""
def str_2_int(str_4_2_int):
    bytes_4_2_int = str_4_2_int.encode("UTF-8")
    return int.from_bytes(bytes_4_2_int, "little")

"""
@description: 将数字转回字符串
-------
@param:
-------
@return:
"""
def int_2_str(int_4_2_str):
    bytes_4_2_str = int_4_2_str.to_bytes((int_4_2_str.bit_length()+7)//8, "little")
    return bytes_4_2_str.decode("UTF-8")

"""
@description: 根据加密 KEY 加密字符串
-------
@param:
-------
@return:
"""
def encrypt(str_4_encrypt, encrypt_key: int = get_default_key()):
    try:
        encrypted_str = ""
        is_str = False
        # 数字可直接加密
        if (str(str_4_encrypt).isdigit()):
            int_4_encrypt = int(str_4_encrypt)
        else:
            # 字符串需要在最后加密后的字符上特殊标记
            is_str = True
            int_4_encrypt = str_2_int(str_4_encrypt)
        chars = rab_config.load_package_config(
            "rab_config.ini", "rab_cryptography", "chars")
        # 数字加密方法
        if (not is_str):
            # 乘以加密密钥
            encrypted_int = int_4_encrypt*encrypt_key
            # 位数
            encrypted_str = str(len(str(encrypted_int))) + "A"
            # 取除数和余数
            quotient = pow(10, len(str(encrypted_int))+3) // encrypted_int
            remainder = pow(10, len(str(encrypted_int))+3) % encrypted_int
            for quotient_char in str(quotient):
                encrypted_str += chars[int(quotient_char)]
            encrypted_str += "A"
            encrypted_str += str(remainder)
        # 字符串加密方法
        else:
            quotient = int_4_encrypt // encrypt_key
            remainder = int_4_encrypt % encrypt_key
            encrypted_str = str(int_4_encrypt) + "A" \
                            + str(quotient)[0] + "A" \
                            + str(remainder)[0] + "A" \
                            + "1"
        # 加密后的字符串长度向 10 凑整
        for _ in range(0, 10):
            if (len(encrypted_str)%10 == 0):
                break
            else:
                encrypted_str += "I"
        return True, encrypted_str, encrypt_key
    except Exception as e:
        print("字符串：" + str(str_4_encrypt) + " 加密失败！" + str(e))
        return False, None, encrypt_key

"""
@description: 解密
-------
@param:
-------
@return:
"""
def decrypt(str_4_decrypt, decrypt_key: int = get_default_key()):
    # 判断是否为用此密码模块加密过的字符
    if (len(str_4_decrypt)%10 != 0):
        print("字符串：" + str(str_4_decrypt) + " 不符合解密字符串要求！")
        return False, None, decrypt_key
    try:
        decrypted_str = ""
        is_str = False
        # 获取各个参数
        str_4_decrypt = str_4_decrypt.replace("I", "")
        encrypted_params = str_4_decrypt.split("A")
        # 参数有 4 个的话说明加密前为字符串类型
        if (len(encrypted_params) == 4):
            is_str = True
        # 如果加密前字符串是纯数字
        if (not is_str):
            chars = rab_config.load_package_config(
                "rab_config.ini", "rab_cryptography", "chars")
            # 取位数
            pow_num = int(encrypted_params[0]) + 3
            # 除余数
            remainder = int(encrypted_params[2])
            # 除整数
            quotient = ""
            encrypted_quotient = encrypted_params[1]
            for encrypted_quotient_char in encrypted_quotient:
                quotient += str(chars.find(encrypted_quotient_char))
            decrypted_int = int(
                (pow(10, pow_num)-remainder)/int(quotient)/decrypt_key)
            return True, str(decrypted_int), decrypt_key
        else:
            decrypted_str = int_2_str(int(encrypted_params[0]))
            return True, decrypted_str, decrypt_key
    except Exception as e:
        print("字符串：" + str(str_4_decrypt) + " 解密失败！" + str(e))
        return False, None, decrypt_key


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    string = "190235"
    print("加密前字符串：" + string)
    # print(str_2_int(string))
    encrypt_success_flg, encrypted_str, encrypt_key = encrypt(string)
    print("加密后字符串：" + encrypted_str)
    decrypt_success_flg, decrypted_str, decrypt_key = decrypt(encrypted_str)
    print("解密后字符串：" + decrypted_str)