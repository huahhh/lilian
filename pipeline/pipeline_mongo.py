# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    pipeline_mongo.py
   Description :
   Author :       Huahng
   date：          2020/11/30
-------------------------------------------------
"""
__author__ = 'Huahng'

from uuid import uuid4

from pymongo import MongoClient
from bson.errors import InvalidDocument

from lilian.pipeline.pipeline_base import pipeline_base


class pipeline_mongo(pipeline_base):

    def __init__(self):
        super(pipeline_mongo, self).__init__()
        self.mongo_config = self.config.get_config(config_type='db_config', config_section='mongo_db')
        self._make_mongo_inst(self.mongo_config)

    def _fix_dict(self, data, ignore_duplicate_key=True):
        """
        Removes dots "." from keys, as mongo doesn't like that.
        If the key is already there without the dot, the dot-value get's lost.
        This modifies the existing dict!

        :param ignore_duplicate_key: True: if the replacement key is already in the dict, now the dot-key value will be ignored.
                                     False: raise ValueError in that case.
        """
        if isinstance(data, (list, tuple)):
            list2 = list()
            for e in data:
                list2.append(self._fix_dict(e))
            return list2
        if isinstance(data, dict):
            for key, value in data.items():
                value = self._fix_dict(value)
                old_key = key
                if "." in key:
                    key = old_key.replace(".", "_")
                    if key not in data:
                        data[key] = value
                    else:
                        error_msg = "Dict key {key} containing a \".\" was ignored, as {replacement} already exists".format(
                            key=old_key, replacement=key)
                        if ignore_duplicate_key:
                            import warnings
                            warnings.warn(error_msg, category=RuntimeWarning)
                        else:
                            raise ValueError(error_msg)
                    del data[old_key]
                data[key] = value
            return data
        return data

    def _make_mongo_inst(self, mongo_config):
        self.mongo_host = mongo_config.get('host', '')
        self.mongo_port = mongo_config.get('port', '')
        self.mongo_user_name = mongo_config.get('user_name', '')
        self.mongo_passwd = mongo_config.get('password', '')
        self.mongo_table_name = mongo_config.get('mongo_table_name', '')
        assert self.mongo_host and self.mongo_port, 'mongo config 不正确'
        self.mongo_inst = MongoClient(host=self.mongo_host, port=self.mongo_port, retryWrites=False)
        if self.mongo_user_name and self.mongo_passwd:
            self.mongo_inst[self.mongo_table_name].authenticate(self.mongo_user_name, self.mongo_passwd)

    def item_process(self, item):
        self._check_id(item)
        item['table_name'] = item.get('table_name') or item.get('spider_name')
        return self.put_to_mongo(item)

    def put_to_mongo(self, item):
        table_name = item.pop('table_name', 'unknown')
        try:
            self.mongo_inst[self.mongo_table_name][table_name].insert_one(item)
            return True
        except InvalidDocument as e:
            self.put_to_mongo(self._fix_dict(item))
        except Exception as e:
            self.log.error(str(e))
            self.log.error('插入数据到mongo失败, {}'.format(str(item)))

    def _check_id(self, item):
        if '_id' not in item:
            item['_id'] = str(uuid4())