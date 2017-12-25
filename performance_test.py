# -*- coding: utf-8 -*-

# digest_generator_hook に変更

'''
Created on 2017/12/25

@author: GYN
'''
from datetime import datetime

import random

class Timer(object):
    def enter(self):
        self.start = datetime.now()
    def exit(self):
        diff = (datetime.now() - self.start).microseconds / 1000
        print("time: %dms" % diff)

class Dummy(object):
    def __init__(self):
        self.value = []
        self.name = "abasdfasfae"
        self.timestamp = "5460484685"

    def cleanup(self):
        self.value = []
        self.name = "abasdfasfae"
        self.timestamp = "5460484685"

if __name__ == '__main__':
    timer = Timer()
    '''
    検証1. valueの生成方法
        a. listとdictを用意し、まずdictに値を突っ込んでいく。最後にlistの順にdictから変数を取り出し、値を結合する
        b. dictに値とindexを格納する。index順に辞書から値を取り出し、結合する

    検証2. インスタンスの生成/破棄と初期化関数呼び出しのどちらが良いか
        a. インスタンスの生成/破棄を繰り返す
        b. 初期化関数を呼び出す
    '''

    value_list = []
    for i in xrange(10000):
        v = random.randint(1, 100000)
        value_list.append("str" + str(v))

    for x in xrange(10):
        ### 1-1
        timer.enter()
        value_dict = {}
        value_data = ""

        # -*-*- 値挿入共通部
        for i in xrange(10000):
            v = random.randint(1, 100000)
            value_name = "str" + str(v)

            value_dict[value_name] = i
        # -*-*-

        for val in value_list:
            v = value_dict.get(val)
            if v is not None:
                value_data += str(v)
        print "idea1: "
        timer.exit()

        ### 1-4 setを使う 1-1とほぼ変わらない(1-2よりは早い)、実運用上こっちのほうがいいはず(listにないvalueが多いはずなので)
        timer.enter()
        value_dict = {}
        value_set = set(value_list)
        value_data = ""

        # -*-*- 値挿入共通部
        for i in xrange(10000):
            v = random.randint(1, 100000)
            value_name = "str" + str(v)

            if value_name in value_set:
                value_dict[value_name] = i
        # -*-*-

        for val in value_list:
            v = value_dict.get(val)
            if v is not None:
                value_data += str(v)
        print "idea4: "
        timer.exit()

        ### 1-2
        timer.enter()
        value_dict = {}
        value_dict_index = {}
        value_data = ""

        for val_name in value_list:
            value_dict_index[val_name] = i

        # -*-*- 値挿入共通部
        for i in xrange(10000):
            v = random.randint(1, 100000)
            value_name = "str" + str(v)

            value_dict[value_name] = i
        # -*-*-

        for k, v in sorted(value_dict_index.items(), key=lambda x: x[1]):
            entry_v = value_dict.get(k)
            if entry_v is not None:
                value_data += str(entry_v)
        print "idea2: "
        timer.exit()

#         ### 1-3 list使う(ありえない遅さ)
#         timer.enter()
#         value_dict = {}
#         value_dict_index = {}
#         value_data = ""
#
#         value_store_list = [None] * len(value_list)
#
#         # -*-*- 値挿入共通部
#         for i in xrange(10000):
#             v = random.randint(1, 100000)
#             value_name = "str" + str(v)
#
#             try:
#                 index = value_list.index(value_name)
#                 value_store_list[index] = i
#             except ValueError:
#                 pass
#         # -*-*-
#
#         for v in value_store_list:
#             if v is not None:
#                 value_data += str(v)
#         print "idea3: "
#         timer.exit()

        #######################################
#         ### 2-2 意外と違う 350ms
#         timer.enter()
#         dummy = Dummy()
#         for i in xrange(1000000):
#             dummy.cleanup()
#
# #             for j in xrange(1000):
# #                 dummy.value.append(j)
#
#         print "idea2-2: "
#         timer.exit()
#
#         ### 2-1    520mx
#         timer.enter()
#         for i in xrange(1000000):
#             dummy = Dummy()
#
# #             for j in xrange(1000):
# #                 dummy.value.append(j)
#
#         print "idea2-1: "
#         timer.exit()



