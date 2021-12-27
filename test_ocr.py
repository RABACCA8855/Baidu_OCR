#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/4/24 16:44
# @Author  : Jiajun LUO
# @File    : test_ocr.py
# @Software: PyCharm

import requests

from threading import Thread
from time import sleep


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


@async
def A():
    sleep(3)
    print("函数A睡了3秒钟。。。。。。")
    print("a function")


def B():
    print("b function")


A()
B()
