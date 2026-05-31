# -*- coding: utf-8 -*-
import json
import threading
from time import sleep

import requests
from gevent import monkey
monkey.patch_all()
import concurrent.futures
import os
import sys
import time
from locust.runners import WorkerRunner,STATE_STOPPING, STATE_STOPPED
sys.path[0] = os.path.dirname(__file__)

from common import dataHandle
from common.apiCommon import commonTask
from utilTools.redisUtil import redisDB
from locustService import order_checkOrderDetail, order_mainflow
from utilTools.getConfig import CommonConfig
from locust import HttpUser, events
import random

# 被施压域名
host = CommonConfig.get_cf("config", "env", "host")
ifLog = CommonConfig.get_cf("config", "controller", "ifLog")
ifMixed = CommonConfig.get_cf("config", "controller", "ifMixed")
FAILURE_THRESHOLD = CommonConfig.get_cf("config", "controller", "FAILURE_THRESHOLD")

# 连接Redis
redis_host = CommonConfig.get_cf("config", "env", "redis_host")
redis_pwd = CommonConfig.get_cf("config", "env", "redis_pwd")
redis_db = CommonConfig.get_cf("config", "env", "redis_db")
db = redisDB(redis_host=redis_host, redis_pwd=redis_pwd, redis_db=redis_db)

# 初始化用户计数器
lenForAccount = 0
cForAccount = 0
listForAccount = []
worker_id = 0
cWorker = 0

symbol_reader = list(dataHandle.getCSVObject('symbol_quanlitity_marketPrice'))

"""
性能测试统一执行类
"""
def merge_task_sets(task_set_classes):
    """
    高度优化的平铺函数：
    1. 保持严格权重比例
    2. 复制完整的底层标签集合 (locust_tag_set)
    """
    flattened_tasks = []

    for ts_class, outer_weight in task_set_classes:
        for task_name in dir(ts_class):
            method = getattr(ts_class, task_name)
            
            # 识别带有 locust 任务特征的方法
            if hasattr(method, 'locust_task_weight'):
                inner_weight = method.locust_task_weight or 1
                total_weight = int(inner_weight * outer_weight)

                def make_wrapper(cls, meth):
                    def wrapper(user_or_taskset):
                        # 无论传入的是 user 还是 parent taskset，都解包出最底层的 user 实例
                        user_instance = getattr(user_or_taskset, "user", user_or_taskset)
                        ts = cls(user_instance)
                        return meth(ts)
                    
                    # 🌟 核心修复 1：提取并注入 Locust 官方过滤器唯一认的 `locust_tag_set` 属性
                    # 兼容不同 Locust 版本中装饰器的特殊命名
                    tags_set = set()
                    if hasattr(meth, 'locust_tag_set'):
                        tags_set = meth.locust_tag_set
                    elif hasattr(meth, '__locust_tags__'):
                        tags_set = set(meth.__locust_tags__)
                    
                    wrapper.locust_tag_set = tags_set
                    wrapper.locust_task_weight = 1  # 伪装成合法 task
                    return wrapper

                wrapped_func = make_wrapper(ts_class, method)
                # 🌟 按最终计算出的绝对权重次数放入列表中平铺
                flattened_tasks.extend([wrapped_func] * total_weight)
                
    return flattened_tasks


class User(HttpUser):
    host = host
    if str(ifMixed) == '0':
        tasks = {
            order_checkOrderDetail.checkOrderDetail: 1,
            order_mainflow.orderMainflow: 1
        }
    else:
        tasks = merge_task_sets([
            (order_checkOrderDetail.checkOrderDetail, 1),
            (order_mainflow.orderMainflow, 1)
        ])
        

    ''' 每启动一个用户，就会执行一次 '''
    def on_start(self):
        if str(ifLog) == '1': print("+++++++++++++on_start++++++++++++")
        account = self.get_next_account()
        # 处理账号数据
        customerInfo = json.loads(db.get(service="account", key=account))
        self.token = customerInfo['token']

        tags = self.environment.parsed_options.tags
        if tags and ('createOrder' in tags):
            self.prepareData()


    def get_next_account(self):
        global cForAccount, lenForAccount, listForAccount
        self.lock = threading.Lock()
        with self.lock:
            account = listForAccount[cForAccount if cForAccount < lenForAccount else cForAccount % lenForAccount]
            cForAccount += 1
            return account


    def prepareData(self):
        # 数据准备
        pass


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    if str(ifLog) == '1': print("+++++++++++++on_locust_init++++++++++++")
    if not isinstance(environment.runner, WorkerRunner):
        '''
            locust-master启动时&服务还没准备好进行初始化
        '''
        global listFo
        rAccount
        listForAccount = []

        reader = dataHandle.getCSVObject('account_pwd')
        threadMaxWorkers = int(CommonConfig.get_cf("config", "setting", "threadMaxWorkers"))

        with concurrent.futures.ThreadPoolExecutor \
                    (max_workers=threadMaxWorkers) as executor:
            executor.map(accountToList, [row[0] for row in reader])
        initCounter()
    else:
        sleep(2)
        global worker_id
        # db.set(service="worker", key=str(environment.runner), value=str(environment.runner))
        worker_id = db.setAndGet(service="worker", key=str(environment.runner), value=str(environment.runner))
        db.close()


@events.init.add_listener
def on_test_start(environment, **_kwargs):
    if str(ifLog) == '1': print("+++++++++++++on_test_start++++++++++++")
    time.sleep(2)
    if isinstance(environment.runner, WorkerRunner):
        global listForAccount, lenForAccount
        worker_count = db.get_key_account("worker*")
        account_reader = dataHandle.getCSVObject('account_pwd')
        print("worker_id is: ", worker_id)
        print("worker_count is: ", worker_count)
        listForAccount = [i[0] for i in account_reader][worker_id-1::worker_count]
        lenForAccount = len(listForAccount)


def initCounter():
    global lenForAccount, cForAccount
    lenForAccount = db.get_key_account("customer")
    print(f"lenForAccount is: {lenForAccount}")
    cForAccount = 0


def accountToList(i):
    listForAccount.append(i)



if __name__ == '__main__':
    print(CommonConfig.get_cf("config", "env", "host"))
