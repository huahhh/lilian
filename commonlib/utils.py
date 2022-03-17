# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    utils.py
   Description :
   Author :       Huahng
   date：          2020/12/2
-------------------------------------------------
"""
__author__ = 'Huahng'

import time
import base64
import hashlib

def md5_sum(_str):
    return hashlib.md5(_str.encode()).hexdigest()

def now_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

def now_time_stamp():
    return int(time.time() * 1000)

def b64_decode(_str):
    return base64.b64decode(_str)

def b64_encode(_str):
    return base64.b64encode(_str)
