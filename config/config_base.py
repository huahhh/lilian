# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    config_base.py
   Description :
   Author :       Huahng
   date：          2020/11/19
-------------------------------------------------
"""
__author__ = 'Huahng'

from abc import ABC, abstractmethod

class config_base(ABC):

    @abstractmethod
    def save_config(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_config(self, *args, **kwargs):
        pass

