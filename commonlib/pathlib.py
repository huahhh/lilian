# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    pathlib.py
   Description :
   Author :       Huahng
   date：          2020/11/19
-------------------------------------------------
"""
__author__ = 'Huahng'

import os

from lilian.commonlib.constant import project_name

def get_file_in_path(path, file_name, res_bool=False):
    for (root, dirs, files) in os.walk(get_project_path() + os.path.sep.join(path.split('/'))):
        for file in files:
            if file_name == file:
                if res_bool:
                    return True
                else:
                    return os.path.sep.join([root, file])
    return False

def get_project_path():
    return os.path.sep.join(os.getcwd().split(os.path.sep)
                            [:os.getcwd().split(os.path.sep).index(project_name) + 1] + [''])

def make_dirs(path):
    os.makedirs(path, exist_ok=True)

def get_path(flag="config"):
    if project_name in os.getcwd().split(os.path.sep):
        return os.path.sep.join(os.getcwd().split(os.path.sep)
                                      [:os.getcwd().split(os.path.sep).index(project_name)+1]+[flag, ''])
    else:
        path_list = os.getcwd().split(os.path.sep)
        for path_item in path_list:
            if project_name in path_item:
                path_list[path_list.index(path_item)] = project_name
        return os.path.sep.join(path_list + [flag, ''])


if __name__ == '__main__':
    # print(get_file_in_path('commonlib',
    #            'logger.py'))
    print(get_file_in_path('spiders', 'spider_%s.py' % 'tv_program', res_bool=False))
