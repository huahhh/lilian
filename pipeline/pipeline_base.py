# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    pipeline_base.py
   Description :
   Author :       Huahng
   date：          2020/11/30
-------------------------------------------------
"""
__author__ = 'Huahng'

from abc import ABC, abstractmethod

from lilian.config.config import config
from lilian.commonlib.logger import logger

class pipeline_base(ABC):

    def __init__(self):
        self.config = config()
        self.log = logger('pipeline')
        self.pipeline_init()

    def pipeline_init(self):
        pass

    @abstractmethod
    def item_process(self, item):
        pass