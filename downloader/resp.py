# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    resp.py
   Description :
   Author :       Huahng
   date：          2020/11/26
-------------------------------------------------
"""
__author__ = 'Huahng'

import json

from lxml.etree import HTML
from urllib.parse import urljoin

class resp(object):

    def __init__(self, response, seed_inst):
        self.response = response
        self.seed_inst = seed_inst

        for seed_field in ['meta', 'url', 'method', 'parser_func']:
            setattr(self, seed_field, getattr(self.seed_inst, seed_field))

    @property
    def res_etree(self):
        try:
            return HTML(self.response.text)
        except:
            return

    @property
    def res_json(self):
        try:
            return json.loads(self.response.text)
        except:
            return

    @property
    def res_content(self):
        return self.response.content

    @property
    def res_text(self):
        return self.response.text

    @property
    def seed_raw(self):
        return self.seed_inst.seed_raw

    def url_join(self, url_item):
        return urljoin(self.response.url, url_item)

