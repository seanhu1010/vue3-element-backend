#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author:  HUHU
# @File:    utils.py
# @Time:    2024/01/14
"""
全局异常处理，异常信息统一返回到response的msg字段里
"""

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # 调用REST框架的默认异常处理函数，获取标准的错误响应
    response = exception_handler(exc, context)

    # 如果得到了一个响应，那么修改响应的数据结构
    if response is not None:
        # 创建一个新的数据字典
        custom_data = {'msg': response.data}

        # 使用新的数据字典替换原来的数据
        response.data = custom_data

    return response
