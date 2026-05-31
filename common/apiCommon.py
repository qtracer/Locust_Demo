# -*- coding: utf-8 -*-
import json
import os
import sys
import time
import hashlib
from locust import TaskSet, SequentialTaskSet
import logging, warnings
from utilTools.getConfig import CommonConfig

ifLog = CommonConfig.get_cf("config", "controller", "ifLog")
getTimeout = float(CommonConfig.get_cf("config", "controller", "getTimeout"))
postTimeout = float(CommonConfig.get_cf("config", "controller", "postTimeout"))
warnings.filterwarnings('ignore')

class commonTask(TaskSet):
    '''
    GET方法
    '''
    def pyget(self, url, headers=None, **kwargs):
        try:
            params = kwargs['params'] if kwargs['params'] else kwargs['param']
        except:
            params = {}
        if params:
            with self.client.get(url, headers=headers, params=params ,
                                 verify=False, catch_response=True, name=url, timeout=getTimeout) as response:
                if response.status_code == 200 and response.json()['success'] == True:
                    if str(ifLog) == '1': logging.info(msg=url + "-----" + response.text)
                    return response  # return response是为了做进一步的断言和参数化
                else:
                    logging.error(msg=url + response.text)
        else:
            with self.client.get(url, headers=headers, verify=False, catch_response=True, name=url, timeout=getTimeout) as response:
                if response.status_code == 200 and response.json()['success'] == True:
                    if str(ifLog) == '1': logging.info(msg=url + "-----" + response.text)
                    return response  # return response是为了做进一步的断言和参数化
                else:
                    logging.error(msg=url + "-----" + response.text)

        # try:
        #     with self.client.get(url, headers=headers, params=kwargs['params'] if kwargs['params'] else kwargs['param'], verify=False, catch_response=True) as response:
        #         try:
        #             if response.status_code == 200 and response.json()['success'] == True:
        #                 if str(ifLog) == '1': logging.info(msg=url +"-----"+response.text)
        #                 return response  # return response是为了做进一步的断言和参数化
        #             else:
        #                 logging.error(msg=url + response.text)
        #         except BaseException as e:
        #             logging.error(e)
        # except:
        #     with self.client.get(url, headers=headers, verify=False, catch_response=True) as response:
        #         try:
        #             if response.status_code == 200 and response.json()['success'] == True:
        #                 if str(ifLog) == '1': logging.info(msg=url +"-----"+response.text)
        #                 return response  # return response是为了做进一步的断言和参数化
        #             else:
        #                 logging.error(msg=url +"-----"+ response.text)
        #         except BaseException as e:
        #             logging.error(e)

    ''' 
    POST方法，用json传参
        method,  # 请求方法
        url,     # 请求地址
        params=None,  # get请求入参
        data=None,    # post 或 put 请求入参
        headers=None, # 请求头
        cookies=None, # Cookie
        files=None,   # 文件上传
        auth=None,    # 鉴权
        timeout=None, # 超时处理
        allow_redirects=True, # 是否允许重定向
        proxies=None,  # 是否设置代理
        hooks=None,    # 钩子
        stream=None,   # 文件下载
        verify=None,   # 证书验证
        cert=None,     # CA认证
        json=None,     # post请求传参的一种方式
    '''
    def pypost(self, url, headers=None, params=None, json=None):
        with self.client.post(url, headers=headers, params=params, json=json, verify=False, catch_response=True, timeout=postTimeout) as response:
            if response.status_code == 200 and response.json()['success'] == True:
                if str(ifLog) == '1': logging.info(msg=url +"-----"+response.text)
                return response
            else:
                logging.error(msg=url +"-----"+response.text)


    # data格式传参
    def pypostd(self, url, headers=None, params=None, data=None, **kwargs):
        with self.client.post(url, headers=headers, params=params, data=data, verify=False, catch_response=True, timeout=postTimeout) as response:
            if response.status_code == 200 and response.json()['success'] == True:
                if str(ifLog) == '1': logging.info(msg=url +"-----"+response.text)
                return response
            else:
                logging.error(msg=url +"-----"+response.text)


    @staticmethod
    def getHeader(**kwargs):
        tmplHeaders = {}
        # dict转str
        json_str = json.dumps(tmplHeaders)
        # str转dict
        header = json.loads(json_str)
        return header


    @staticmethod
    def getApiJson(name, changes=None):
        path = os.path.dirname(os.path.dirname(__file__)) + '/apiJson/'
        with open(path + name + '.json', "r", encoding='utf-8') as file:
            data = json.load(file)
        if changes != None:
            """
            一次性修改嵌套 JSON 数据中的多个字段，支持列表的增删操作
            :param data: 解析后的 JSON 数据（Python 字典或列表）
            :param changes: 包含修改信息的字典，键为路径，值为新值或操作指令
            :return: 修改后的 JSON 数据
            """
            for path, value in changes.items():
                keys = path.split('.')
                current = data
                for key in keys[:-1]:
                    if isinstance(current, dict):
                        current = current.get(key)
                    elif isinstance(current, list):
                        try:
                            index = int(key)
                            current = current[index]
                        except (ValueError, IndexError):
                            break
                    if current is None:
                        break

                if current is not None:
                    last_key = keys[-1]
                    if isinstance(current, dict):
                        current[last_key] = value
                    elif isinstance(current, list):
                        if last_key == "__append__":
                            current.append(value)
                        elif last_key == "__delete__":
                            try:
                                index = int(value)
                                if 0 <= index < len(current):
                                    del current[index]
                            except (ValueError, IndexError):
                                pass
                        else:
                            try:
                                index = int(last_key)
                                if 0 <= index < len(current):
                                    current[index] = value
                            except (ValueError, IndexError):
                                pass
        return data



if __name__ == '__main__':
    pass
