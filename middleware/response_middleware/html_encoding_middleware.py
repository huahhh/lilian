# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    html_encoding_middleware.py
   Description :
   Author :       Huahng
   date：          2020/12/2
-------------------------------------------------
"""
__author__ = 'Huahng'

from requests.utils import get_encoding_from_headers
from requests.utils import get_encodings_from_content

class html_encoding_middleware(object):

    def middleware_process(self, resp_inst, spider_inst):
        encoding = None
        if hasattr(resp_inst, 'encoding'):
            encoding = resp_inst.encoding

        if not encoding:
            html_text = resp_inst.response.text[1:]  # 去除bom标记
            encoding = get_encodings_from_content(html_text)
            if encoding:
                encoding = encoding[0]

        if not encoding:
            encoding = get_encoding_from_headers(resp_inst.response.headers)

        encoding_type = encoding or 'utf-8'
        resp_inst.response.encoding = encoding_type

        return resp_inst