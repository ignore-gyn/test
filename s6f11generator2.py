# -*- coding: utf-8 -*-

import sys

log = """<L[3]
    <U4[1] 1001>
    <U4[1] 9999>
    <L[3]
        <L[2]
            <U4[1] 1001>
            <L[4]
                <L[0]>
                <L[2]
                    <L[1]
                        <A[3] "abc">
                    >
                    <U4[1] 123>
                >
                <A[4] "test">
                <U4[1] 987>
            >
        >
        <L[2]
            <U4[1] 1002>
            <L[0]>
        >
        <L[2]

            <U4[1] 1003>
            <L[4]
                <L[1]
                    <L[1]
                        <L[0]>
                    >
                >
                <A[4] "lkjo">
                <U4[3] 123>
                <L[0]>
            >
        >
    >
>"""
# CEID - EVENTNAME
event_list = {
              9991 : "Event1",
              9999 : "Event2"
              }

# RPTID - VIDs
report_list = {
              1004 : [1, 2, 3],
              1002 : [1, 2, 3],
              1003 : [4, 2, 3, 5],
              1005 : [1, 2, 3],
              1001 : [4, 5, 6, 9],
    }
# VID - VNAME
var_list = {
            1 : "var1",
            2 : "var2",
            3 : "var3",
            4 : "var4",
            5 : "var5",
            6 : "var6",
            7 : "var7",
            }

# rfindでも先頭インデクスが返ることに注意

class LogParser(object):
    def __init__(self):
#         self.__item_value = None
#         self.__item_len = None
#         self.__item_type = None
        pass

    def parse_len(self, log):
        # timestampチェック
        pass

    def parse_hdr(self, log):
        # target SFチェック
        # targetならここで、generatorのインスタンス化
        pass

    def parse_msg(self, log):
        # depth : メッセージ構造の妥当性チェックのみに内部で使う
        # readable_depth : SML、ダイジェスト等外に渡す用に使う

        item = {
                "type" : None,
                "length" : None,
                "value" : None,
                "readable_depth" : [0],
                }
        depth = []

        msg = S6F11()


        for line in log:
            if len(item["readable_depth"]) == 0:
                print "readable_depth len is 0"
                return msg.get_digest()

            if line.find('<L') > -1:
                item["type"] = "L"
                item["value"] = None
                item["length"] = int(line[line.find('[')+1: line.rfind(']')])

                item["readable_depth"][-1] += 1
                if len(depth) > 0:
                    depth[-1] -= 1

                if item["length"] != 0:    # <L>じゃないことを確認
                    item["readable_depth"].append(0)
                    depth.append(item["length"])

            elif line.find('<') > -1:
                space_pos = line.rfind(' ')
                if space_pos == -1:
                    item["type"] = line[line.find('<')+1: line.rfind('[')]
                    item["value"] = None
                else:
                    item["type"] = line[line.find('<')+1: line.rfind('[')]
                    item["value"] = line[space_pos+1: line.rfind('>')]
                item["length"] = int(line[line.find('[')+1: line.rfind(']')])

                item["readable_depth"][-1] += 1
                depth[-1] -= 1

            elif line.find('>') > -1:
                item["readable_depth"].pop()
                depth.pop()
#                 print line.ljust(40, ' ') + " # depth=" + str(readable_depth)
#                 digest["detail"] += line + '\n'
                msg.notify_end_list(item)
                continue

            msg.notify_item(item)

        return msg.get_digest()

class DigestGenerator(object):
    def __init__(self):

        self.digest = {
                       "detail": [],
                       "value": "",
                       }

    def generate_detail(self, item):
        values = ''

        if item["type"] == 'L' and item["length"] > 0:
            self.digest["detail"].append('%s<L' % (' '* ((len(item["readable_depth"])-1)*4)))
        else:
            if item["value"] is not None:
                values = ' ' + item["value"]
            self.digest["detail"].append('%s<%s%s>' % (' '* (len(item["readable_depth"])*4), item["type"], values))

#         while self.depth[-1] <= 0:
#             self.depth.pop()
#             self.digest["detail"].append('%s>\n' % (' '* len(item["readable_depth"])))

#         return sml

    def notify_item(self, item):
        self.generate_detail(item)

    def notify_end_list(self, item):
        self.digest["detail"].append('%s>' % (' '* (len(item["readable_depth"])*4)))

class S6F11(DigestGenerator):

    def __init__(self):
        super(S6F11, self).__init__()

        self.ceid = None
#         self.report_list = None
        self.current_rptid = None
        self.tmp_varname = ""

    def notify_item(self, item):

        depth = item["readable_depth"]

        super(S6F11, self).generate_detail(item)

        # CEID
        current_line = self.digest["detail"][-1]
        if len(depth) == 2 and depth[1] == 2:
            ceid = int(item["value"])
            self.digest["detail"][-1] = ("%s// %s" %
                                (current_line.ljust(32, ' '), event_list[ceid]))

        # RPTID
        elif len(depth) == 4 and depth[3] == 1:
            self.current_rptid = int(item["value"])

        # VarTop (non-L or 0-length L)
        elif len(depth) == 5 and depth[4] > 0:
            vid = report_list[self.current_rptid][depth[4]-1]
            var_name = var_list.get(vid)

            if var_name is not None:
                self.digest["detail"][-1] = '%s// %d %s' % (current_line.ljust(32, ' '), vid, var_name)

            if item["value"] is not None:
                if self.digest["value"] != "":
                    self.digest["value"] += ', '
                self.digest["value"] += '%s: %s' % (var_name, str(item["value"]))
            self.tmp_varname = ""

        # VarTop (L)
        elif len(depth) == 6 and depth[5] == 0:
            vid = report_list[self.current_rptid][depth[4]-1]
            var_name = var_list.get(vid)

            if var_name is not None:
                self.digest["detail"][-1] = '%s// %d %s' % (current_line.ljust(32, ' '), vid, var_name)

            # 中身が何もない可能性があるので、ここでは変数名を"value"にいれない
            self.tmp_varname = var_name

        # Value in L
        elif len(depth) >= 6 and depth[5] > 0:
            if item["value"] is not None:
                # First Value
                if self.tmp_varname != "":
                    if self.digest["value"] != "":
                        self.digest["value"] += ', '
                    self.digest["value"] += "%s: %s" % (self.tmp_varname, str(item["value"]))
                    self.tmp_varname = ""

                # Second or after Value
                else:
                    self.digest["value"] += " | %s" % str(item["value"])

        print self.digest["detail"][-1], item["readable_depth"]
#         print self.digest["detail"][-1], depth

    def get_digest(self):
        return self.digest



def joinItem(itemtype, values):
    if len(values) == 0:
        s = "<%s>" % itemtype
    else:
        s = "<%s %s>" % (itemtype, ' '.join(values))

    print s
    return s

def joinList(data, index):
    print '%s<L\n%s\n%s>' % (' ' * (index*4), data, ' ' * ((index-1)*4))
    return '%s<L\n%s\n%s>' % (' ' * (index*4), data, ' ' * ((index-1)*4))

def joinData(data):
    output = ''
    for i, item in enumerate(data):
        print item, type(item)

        if isinstance(item, list):
            for d in item:
                output += joinList(joinData(d), i)
        else:
            for k, v in item.items():
                output += '%s%s\n%s>\n' % (' ' * (i*4), joinItem(k, v), ' ' * ((i-1)*4))
    return output

if __name__ == '__main__':

#     digest = {
#               "value" : "",
#               "detail" : ""
#               }

#     f = open("./data/text1.txt")
#     i = 1
#     for line in f:
#         sys.stdout.write(str(i) + ": " + line)
#         i += 1
#     sys.exit()

#
#     data = ([
#     {"U4":["1001"]},
#     {"U4":["9999"]},
#     [
#         [
#             {"U4":["222"]},
#             [
#                 [],
#                 [
#                     [
#                         {"A": ["abc"]}
#                     ],
#                     {"U4": ["123"]}
#                 ],
#                 {"A": ["test"]},
#                 {"U4": ["987"]}
#             ]
#         ]
#     ]
# ])
#     output = joinData(data)
#
#     print "####"
#     print output
#     sys.exit()


#     print line.ljust(40, ' ') + " # depth=" + str(readable_depth)
#     msg.notifyItem(item, digest)

    msg = S6F11()
    log_parser = LogParser()

    f = open("./data/text1.txt")
    digest = log_parser.parse_msg(f)
    f.close()

    print "\n%s\n" % ('#' * 40)
    print '\n'.join(digest["detail"])
    print "\n%s\n" % ('#' * 40)
    print digest["value"]

#####
"""
【今】
②log_parserに1メッセージごとにパースさせる
②パース結果から、ダイジェスト対象か判定(SF&time)
③digest_generatorにダイジェスト情報を生成させる

【案】
chsms_log_parserからLEN, HDRのイベント(property)を上げる
①odmでLENイベントに対して、時間が対象か判定する
②odmでHDRイベントに対して、ダイジェスト対象か判定し、
    対象のsxfy_digest_generatorをインスタンス化
    インスタンスをchsms_log_parserへ渡す
③MSGのアイテムごとに、sxfy_digest_generatorにannotation, digest valueを生成させる
    S6F11の場合は、CEIDに遭遇し次第ダイジェスト対象か判定し、
    対象でなかった場合は、パースをとばす
④odmでMessageEndイベントに対して、digest情報を受け取り、ファイルへ出力する

####
・Key errorを出さない (get())かわりにNone
・listなら...素直にチェックするしかない
    def list_get(L, i, default_value = None):
        if -len(L) <= i < len(L): return L[i]
        else: return default_value

・行つなげるなら\でなく全体を()でくくる
・writeかwritelinesか
    write - 適宜
    writelines - []で用意しておいて一気に(改行コードを追加してくれるわけではないのでつけておく)
・new_list = [x+23 for x in old_list if x > 5]
・http://works.surgo.jp/translation/pyguide.html
    private には __（2つ）
    procted には _（1つ）
    クラス名、例外 CapWords★
    モジュール、パッケージ、関数 lower_with_under
    グローバル定数 CAPS_WITH_UNDER
    グローバル変数 lower_with_under
    インスタンス変数、メソッド名、関数/メソッドパラメータ、ローカル変数 lower_with_under
・filter 、 map 、 reduce ではなく、リスト内包表記や for ループを利用する。
・”空” の値を false と評価するため、 0, None, [], {}, “” のすべての評価は、 ブール値コンテキストでは false となります
・v = dict(a=1, b=2)
print '<' + ', '.join([ '%s=%s' % (k, v[k]) for k in v.keys() ]) + '>'  #=> '<a=1, b=2>'
####
[
    {U4:[1001]},
    {U4:[9999]},
    [
        [
            {U4:[222]},
            [
                [],
                [
                    [
                        {A: ["abc"]}
                    ],
                    {U4: [123]}
                ],
                {A: ["test"]},
                {U4: [987]}
            ]
        ]
    ]
]
"""