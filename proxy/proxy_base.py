# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    proxy_base.py
   Description :
   Author :       Huahng
   date：          2020/11/27
-------------------------------------------------
"""
__author__ = 'Huahng'


from abc import ABC, abstractmethod


class proxy_base(ABC):

    @abstractmethod
    def get_proxy(self):
        pass