# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    db_redis.py
   Description :
   Author :       Huahng
   date：          2020/11/23
-------------------------------------------------
"""
__author__ = 'Huahng'

import redis

class db_redis(object):

    def __init__(self, redis_host, redis_port, **kwargs):
        self.redis_conn = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            db=kwargs.get('db'),
            password=kwargs.get('password'),
            decode_responses=True)

    def __getattr__(self, item):
        if item not in self.__dict__:
            self.__dict__[item] = getattr(self.redis_conn, item)
        return self.__dict__[item]
