# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    utils.py
   Description :
   Author :       Huahng
   date：          2021/1/18
-------------------------------------------------
"""
__author__ = 'Huahng'

import re
import json

def get_json_from_html(js_str):
    json_raw = re.search('({[\S\s]*\})', js_str).group(1)
    jsn = json.loads(json_raw)
    return jsn
