# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    singleton.py
   Description :
   Author :       Huahng
   date：          2019/10/18
-------------------------------------------------
"""
__author__ = 'Huahng'

"""
the singleton inst
"""

from functools import wraps


def singleton(cls):
    instances = {}
    @wraps(cls)
    def get_instance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return get_instance