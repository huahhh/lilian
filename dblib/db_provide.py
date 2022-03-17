# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    db_provide.py
   Description :
   Author :       Huahng
   date：          2020/11/18
-------------------------------------------------
"""
__author__ = 'Huahng'

import importlib

def get_db_provide(db_type, db_host, db_port, **kwargs):
    project_name = kwargs.get('project_name') or 'lilian'
    return getattr(importlib.import_module('{}.dblib.db_%s'.format(project_name) % db_type),
                   'db_%s' % db_type)(db_host, db_port, **kwargs)

if __name__ == "__main__":
    a = get_db_provide('ssdb', '*', 18888)
    a.queue_put('11')