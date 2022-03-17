# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    config_apollo.py
   Description :
   Author :       Huahng
   date：          2020/11/19
-------------------------------------------------
"""
__author__ = 'Huahng'

import os
import json
import requests
import configparser

from lilian.config.config_base import config_base
from lilian.commonlib.catch_retry import catch_retry
from lilian.commonlib.pathlib import get_path


class config_apollo_manager(object):

    def __init__(self, host, params):
        self.params = self._parser_params(params)
        self.host = host
        self.appid = self.params.get('appid', 'lilian')
        self.user = self.params.get('user', 'apollo')
        self.token = self.params.get('token', '')
        assert self.token, "token is null"
        self.header = {'Authorization': self.token,
                       'Content-Type': 'application/json;charset=UTF-8'}

    def _parser_params(self, params):
        return {i.split('=')[0]: i.split('=')[1] for i in params.split('&')}

    def _load_files_name(self, dir_name):
        file_list = []
        for (root, dirs, files) in os.walk(os.path.sep.join([get_path(), dir_name])):
            for file in files:
                if '.ini' in file:
                    file_list.append(file.replace('.ini', ''))
        return file_list

    def _read_config(self, dir_name, config_type):
        ini_config_inst = configparser.ConfigParser()
        ini_config_inst.read(''.join([get_path(), dir_name, os.path.sep, config_type, '.ini']), encoding='utf-8')
        return ini_config_inst

    def _parser_config_file(self, dir_name, file_name):
        config_dict = {}
        ini_config_inst = self._read_config(dir_name, file_name)
        for section_item in ini_config_inst.sections():
            for kv_item in ini_config_inst.items(section_item):
                config_dict['.'.join([section_item, kv_item[0]])] = kv_item[1]
        return config_dict


    def _upload_items(self, cluster_name, config_type, key, value):
        url = 'http://{portal_address}/openapi/v1/envs/DEV/' \
              'apps/{appId}/clusters/{clusterName}/namespaces/{namespaceName}/items'.format(portal_address=self.host,
                                                                                            appId=self.appid,
                                                                                            clusterName=cluster_name,
                                                                                            namespaceName=config_type)
        data = {
            'key': key,
            'value': value,
            'dataChangeCreatedBy': self.user
        }
        res = requests.post(url, json=data, headers=self.header)
        print(res.text)

    def make_cluster(self, cluster_name):
        url = 'http://{portal_address}/openapi/v1/envs/DEV/apps/{appId}/clusters'.format(portal_address=self.host,
                                                                                              appId=self.appid,
                                                                                              )
        data = {
            'name': cluster_name,
            'appId': self.appid,
            'dataChangeCreatedBy': self.user
        }
        res = requests.post(url, json=data, headers=self.header)
        print(res.text)

    def get_all_namespace(self, cluster_name):
        url = 'http://{portal_address}/openapi/v1/envs/DEV/apps/{appId}/clusters/{clusterName}/namespaces'.format(
            portal_address = self.host,
            appId = self.appid,
            clusterName=cluster_name
        )
        res = requests.get(url, headers=self.header)
        return [item.get('namespaceName') for item in res.json()]

    def release_namespace(self, clusterName, namespace):
        url = 'http://{portal_address}/openapi/v1/envs/DEV/apps/{appId}/' \
              'clusters/{clusterName}/namespaces/{namespaceName}/releases'.format(portal_address=self.host,
                                                                                  appId=self.appid,
                                                                                  clusterName=clusterName,
                                                                                  namespaceName=namespace)
        data = {
            'releaseTitle': 'first release',
            'releasedBy': self.user
        }
        res = requests.post(url, json=data, headers=self.header)
        print(res.text)

    def upload_application(self, dir_name, cluster):
        files = self._load_files_name(dir_name)
        self._upload_items(cluster, 'application', 'config_list', json.dumps(files, ensure_ascii=False))
        return files

    def upload_config_file(self, file, dir_name, cluter):
        file_json = self._parser_config_file(dir_name, file)
        for item in file_json:
            self._upload_items(cluter, file, item, file_json[item])

    def upload_apollo(self, dir_name, cluster=None):
        cluster = cluster if cluster else dir_name
        self.make_cluster(cluster)
        files = self.upload_application(dir_name, cluster)
        for file in files:
            self.upload_config_file(file, dir_name, cluster)

    def release_apollo(self, cluster):
        all_name_space = self.get_all_namespace(cluster)
        for name_space_item in all_name_space:
            self.release_namespace(cluster, name_space_item)



class config_apollo(config_base):

    def __init__(self, host, params):
        self.params = self._parser_params(params)
        self.host = host
        self.appid = self.params.get('appid', 'lilian')
        self.cluster = self.params.get('cluster', '')
        self.apollo_url = "http://{host}/configfiles/json/{appid}/{cluster}/{namespace}"

    @catch_retry
    def get_config_from_apollo(self, config_type):
        url = self.apollo_url.format(
            host = self.host,
            appid = self.appid,
            cluster = self.cluster,
            namespace = config_type
        )
        res = requests.get(url)
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 404:
            return "not found"
        else:
            return None

    def _parser_params(self, params):
        return {i.split('=')[0]: i.split('=')[1] for i in params.split('&')}


    def _parser_apollo_json(self, config_dict):
        def nested_set(dic, keys, value):
            for key in keys[:-1]:
                dic = dic.setdefault(key, {})
            dic[keys[-1]] = value

        mu_dict = {}

        for key in config_dict:
            keys = key.split('.')
            nested_set(mu_dict, keys, config_dict[key])

        return mu_dict

    def write_config_file(self, config_dict, namespace):

        if config_dict == "not found":
            conf = configparser.ConfigParser()
            with open(os.path.sep.join([get_path(), self.cluster, '%s.ini' % namespace]), 'w') as f:
                conf.write(f)
            return

        if config_dict is None:
            return

        conf = configparser.ConfigParser()
        mu_dict = self._parser_apollo_json(config_dict)

        for k in mu_dict:
            conf[k] = mu_dict[k]

        with open(os.path.sep.join([get_path(), self.cluster, '%s.ini' % namespace]), 'w') as f:
            conf.write(f)

    def save_config(self):
        config_path = get_path()
        if not os.path.exists(os.path.sep.join([config_path, self.cluster])):
            os.makedirs(os.path.sep.join([config_path, self.cluster]))
        for config_item in eval(
                self.get_config_from_apollo('application').get('config_list', [])):
            config_dict = self.get_config_from_apollo(config_item)
            self.write_config_file(config_dict, config_item)
        # self.log.info('生成环境为%s的配置' % xiaoming_cleaner_env)

    def get_config(self, config_type, config_section=None, config_item=None):
        raw_config_dict = self.get_config_from_apollo(config_type)
        assert raw_config_dict != 'not found', '配置类 {} 未找到'.format(config_type)
        config_dict = self._parser_apollo_json(raw_config_dict)
        if config_section:
            assert config_section in config_dict, '配置组 {} 未找到'.format(config_section)
            if config_item:
                assert config_item in config_dict[config_section], '配置项 {} 未找到'.format(config_item)
                return config_dict[config_section][config_item]
            else:
                return config_dict[config_section]
        return config_dict

if __name__ == '__main__':
    pass


