# -*- coding: utf-8 -*-
import time
from random import random

import redis
from gevent.subprocess import value
import secrets
import string
from utilTools.getConfig import CommonConfig

class redisDB(object):
    def __init__(self, is_master=False, redis_host="localhost", redis_port="6379", redis_pwd=None, redis_db = 0):
        self.pool = redis.ConnectionPool(host=redis_host,
                                        port=redis_port,
                                        db=redis_db,
                                        password=redis_pwd)
        self.conn = redis.StrictRedis(connection_pool=self.pool)

    def set(self, service, key, value=None):
        self.conn.set(name=service + ":" + key, value=value)


    def setAndGet(self, service, key, value=None):
        # 注册时用锁，避免冲突
        LOCK_KEY = "locust2026"
        while not self.conn.set(LOCK_KEY, "1", nx=True, ex=10):
            time.sleep(0.1)
        try:
            self.conn.set(name=service + ":" + key, value=value)
            count = self.get_key_account(service)
        finally:
            self.conn.delete(LOCK_KEY)
            return count


    def get(self, service, key):
        data = str(self.conn.get(service + ":" + key), encoding="utf-8")
        return data

    def getD(self, service, key):
        data = eval(str(self.conn.get(service + ":" + key), encoding="utf-8"))
        return data

    def get_key_account(self, service=None):
        # return len(self.conn.scan(match=service+'*'))
        count = 0
        cursor = 0
        while True:
            cursor, keys = self.conn.scan(cursor=cursor, match=service+'*')
            count += len(keys)
            if cursor == 0:
                break
        return count


    def flush_key(self, service):
        for key in self.conn.scan_iter(match=service+'*'):
            self.conn.delete(key)

    def close(self):
        self.conn.close()

if __name__ == '__main__':
    redis_host = CommonConfig.get_cf("config", "env", "redis_host")
    redis_pwd = CommonConfig.get_cf("config", "env", "redis_pwd")
    redis_db = CommonConfig.get_cf("config", "env", "redis_db")
    db = redisDB(redis_host=redis_host, redis_pwd=redis_pwd, redis_db=redis_db)
    # db.set(service='account', key='acc' ,value='1234')

