# -*- coding: utf-8 -*-

START_ITEM = 0
START_LIST = 1
END_LIST = 2

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
                "status": None,
                "annot": ""
                }
        depth = []

        for line in log:
            if len(item["readable_depth"]) == 0:
                print "readable_depth len is 0"
#                 return msg.get_digest()
                break

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
                    item["status"] = START_LIST
                else:
                    item["status"] = START_ITEM

            elif line.find('<') > -1:

                item["length"] = int(line[line.find('[')+1: line.rfind(']')])

                if item["length"] == 0:
                    item["type"] = line[line.find('<')+1: line.rfind('[')]
                    item["value"] = None
                else:
                    space_pos = line.rfind(' ')
                    item["type"] = line[line.find('<')+1: line.rfind('[')]
                    item["value"] = line[space_pos+1: line.rfind('>')]

                item["readable_depth"][-1] += 1
                if len(depth) > 0:
                    depth[-1] -= 1

                item["status"] = START_ITEM

            elif line.find('>') > -1:
                item["type"] = "closeL"
                item["length"] = None
                item["value"] = None

                item["readable_depth"].pop()
                depth.pop()

                item["status"] = END_LIST

#             msg.notify_item(item)
            yield item

#         return msg.get_digest()

S1F2_format = {
1: "NAME"
}


# CEID - EVENTNAME
event_list = {
              9991 : "Event1",
              9999 : "Event2"
              }

# CEID - target VNAMEs
target_vname_list = {
                     9999 : ["var5", "var4", "var3", "var2"]
}

# RPTID - VIDs
report_list = {
              '1004' : [1, 2, 3],
              '1002' : [1, 2, 3],
              '1003' : [4, 2, 3, 5],
              '1005' : [1, 2, 3],
              '1001' : [4, 5, 9, 5],
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



S16F11_format = {
"L": 7,
1: "DATAID",
2: "PRJOBID",
3: "MF",
4: {
    "L": -1,
    -1: "MID"
    },
5: {
    "L": 3,
    1: "RECIPE_METHOD",
    2: "RCPSPEC",
    3: {
        "L": -1,
        -1: {
             "L": 2,
             1: "RCP_PAR_NM",
             2: "RCP_PAR_VAL"
             }
        }
    },
6: "PROCESSSTART",
7: "PAUSEEVENT"
}
S16F11_digest_value_target = [
# (Name to output, Item Name for output Name, Item Name for output Value)
# ("PJID", None, "PRJOBID"),
# ("RCPSPEC", None, "RCPSPEC"),
# (None, "RCP_PAR_NM", "RCP_PAR_VAL")
# ]
# PJID: "job1", RCPSPEC: "/test", "ReticleID": "/testret"
]
S16F11_digest_annot_target = {
                              "PRJOBID": "PRJOBID",
                              "RCPSPEC": "RCPSPEC",
                              "RCP_PAR_VAL":"RCP_PAR_VAL"}


S1F1_format = {}   # header-only

S2F33_format = {
"L": 2,
1: "DATAID",
2: {
    "L": -1,
    -1: {
         "L": 2,
         1: "RPTID",
         2: {
             "L": -1,
             -1: "VID"
             }
         }
    }
}

S2F34_fomat = {0: "DRACK"}
S2F34_fomat = "DRACK"


def generate_digest_val_depth_dict():
    digest_val_depth_dict = {}
    depth = [1]
    tree = S16F11_format
    target = []
    for v in S16F11_digest_value_target:
        if isinstance(v, tuple):
            for i in v:
                target.append(i)
        else:
            target.append(v)
    print target

    tree_iterator(tree, depth, digest_val_depth_dict, target)
    print generate_digest_val_depth_dict
    return digest_val_depth_dict

import copy
def tree_iterator(tree, depth, digest_val_depth_dict, target_list):
    print "target", target_list
    d = tree.get("L")
#     if None:    # only 1 item
#     else

    if d != -1:
        depth.append(0)
        for i in xrange(d):
            depth[-1] += 1
            item_name = tree[i+1]

            if isinstance(item_name, dict):
                tree_iterator(item_name, depth, digest_val_depth_dict, target_list)
            else:
                print item_name, depth
                if item_name in target_list:
                    digest_val_depth_dict[item_name] = copy.deepcopy(depth)
    else:
        depth.append(-1)
        item_name = tree[-1]
        print item_name, depth

        if isinstance(item_name, dict):
            tree_iterator(item_name, depth, digest_val_depth_dict, target_list)
        else:
            print item_name, depth
            if item_name in target_list:
                digest_val_depth_dict[item_name] = copy.deepcopy(depth)

    if len(depth) > 0:
        depth.pop()



def compare_depth_tree(expect, depth):
    if len(depth) < len(expect):
        return False

    for (i, j) in zip(expect, depth):
        if i == -1:
            continue
        if i != j:
            return False
    return True

def create_S6F11_testdata():

    f = open("./data/text3.txt", 'w')
    txt = '''<L[3]
    <U4[1] 1001>
    <U4[1] 9999>
    <L[503]
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
        >'''
    txt += '''
        <L[2]
            <U4[1] 1002>
            <L[0]>
        >'''
    txt += '''
        <L[2]
            <U4[1] 1004>
            <L[2]
                <L[0]>
                <A[4] "ttmp">
                <U4[1] 6565>
            >
        >''' * 500
    txt += '''
        <L[2]
            <U4[1] 1003>
            <L[3001]
                <L[1]
                    <L[1]
                        <L[0]>
                    >
                >'''

    txt += '''
                <A[4] "lkjo">
                <U4[1] 123>
                <L[0]>''' * 1000
    txt += '''
            >
        >
    >
>'''
    f.write(txt)
    f.close()

import datetime
class Timer(object):
    def enter(self):
        self.start = datetime.datetime.now()
    def exit(self):
        diff = datetime.datetime.now() - self.start
        print("time: %s" % str(diff))
        self.start = None




class BaseDigestGenerator(object):
    TAB = '    '

    def __init__(self, format=None, value_target=None, annot_target=None):

        if format:
            self.format = format
        else:
            self.format = None

        if value_target:
            self.value_target = set(value_target)
        else:
            self.value_target = None

        if annot_target:
            self.annot_target = annot_target
        else:
            self.annot_target = None

        self.detail = []
        self.value = []

        self.current_item = None
        self.tmp_value_name = ""
        self.tmp_value_txt = ""

        self.is_value_txt_full = False  # Value text is longer than maximum length or not

    def _generate(self, item, item_name):

        if item_name is not None:
            self.current_item = item_name

        # Create Detail
        depth = len(item["readable_depth"])-1
        if item["status"] is END_LIST:
            txt = '%s>' % (BaseDigestGenerator.TAB * depth)
        elif item["status"] is START_LIST:
            txt = '%s<L[%d]' % (BaseDigestGenerator.TAB * (depth-1), item["length"])
        elif item["status"] is START_ITEM:
            if item["value"] == None:
                txt = '%s<%s[%d]>' % (BaseDigestGenerator.TAB * depth,
                                      item["type"], item["length"])
            else:
                txt = '%s<%s[%d] %s>' % (BaseDigestGenerator.TAB * depth,
                                         item["type"], item["length"], item["value"])

        if self.format is None:
            print txt
            return txt

        # Add Annot
        if item["status"] is not END_LIST:
            ret = self.annot_target.get(item_name)
            if ret == "CEID":
                ret = self._get_event_name_from_CEID(item["value"])
                if ret:
                    txt = txt.ljust(70) + "// " + ret
            elif ret:
                txt = txt.ljust(70) + "// " + ret

        # Compose digest Value
        # in oreder it appear

        # type1. even if no actual value (only list etc.), list the value (i.e. output as
        # <Item Name>; , )

#         if self.current_item in self.value_target:
#             if item_name is None:   # Inside of target value
#                 if item["value"] is not None:
#                     if self.tmp_value_txt:
#                         self.tmp_value_txt += ' | '
#                     self.tmp_value_txt += item["value"]
#
#             else:
#                 if item["status"] == START_LIST:
#                     self.tmp_value_name = item_name + ': '
#
#                 elif item["status"] == END_LIST:
#                     self.value.append(self.tmp_value_name + self.tmp_value_txt)
#                     self.tmp_value_name = ""
#                     self.tmp_value_txt = ""
#
#                 else:
#                     if item["value"] is not None:
#                         val = item_name + ': ' + item["value"]
#                     else:
#                         val = item_name + ': '
#                     self.value.append(val)

        # type2. if no actual value (only list etc.), no output
        if self.value_target and self.current_item in self.value_target:
            if item_name is None:   # Inside of target value
                if item["value"] is not None:
                    if self.tmp_value_txt:
                        self.tmp_value_txt += ' | '
                    else:
                        self.tmp_value_txt = self.current_item + ': '
                    self.tmp_value_txt += item["value"]

            else:
                if item["status"] == END_LIST:
                    if self.tmp_value_txt:
                        self.value.append(self.tmp_value_txt)
                    self.tmp_value_name = ""
                    self.tmp_value_txt = ""

                elif item["value"] is not None:
                    val = item_name + ': ' + item["value"]
                    self.value.append(val)

#         print txt
        return txt

    def get_digest(self):
        val = ', '.join(self.value)

        return val

    def _get_event_name_from_CEID(self, ceid):
        return event_list.get(int(ceid))

    def _get_V_name_from_VID(self, vid):
        return var_list.get(int(vid))

    # ItemParser
    def iterator3(self, item_generator):
        format = self.format

        '''
        2. 毎アイテム解析と一緒に、フォーマット内の位置を移動していき、現在のアイテム名を取得する
        '''

        for l, d in enumerate(item_generator):
            if ((len(d["readable_depth"]) == 2 and d["status"] is START_LIST)
                or self.format is None):
                self._generate(d, "")
                continue

            ret = ""
            current_item = None

            if d["status"] is END_LIST:
                format = self.format
                for i in d["readable_depth"][1:-1]:
    #                 if i == 0:
    #                     break

                    if not format:   # {}
                        format = None
                        break

                    ret = format.get(-1)
                    if ret is None:
                        ret = format.get(i)

                    if ret is None:
                        print "<not found> END LIST"
                        format = None
                        break
                    elif isinstance(ret, dict):
                        format = ret
                    else:
                        format = None
                        break

                if format:
                    ret = format.get(-1)
                    if ret is None:
                        ret = format.get(d["readable_depth"][-1])

                    if not isinstance(ret, dict):
                        current_item = ret

            elif format:
                list_count = format.get("L")
                if list_count == -1:
                    ret = format.get(-1)
                elif d["status"] is START_LIST:
                    ret = format.get(d["readable_depth"][-2])
                else:
                    ret = format.get(d["readable_depth"][-1])

                if ret is None:
                    print "<not found>"
                elif isinstance(ret, dict):
                    if d["status"] is START_LIST:
                        format = ret
                    else:
    #                     print "<0-length item or ERROR>"
                        pass
                else:
                    current_item = ret
                    if d["status"] is START_LIST:
                        format = None


    #         print '-' * 80
    #         print d["readable_depth"]
    #         print l, ': ', d["type"].ljust(2), d["value"]
    #         if current_item is not None:
    #             print "item name: ", current_item
    #         else:
    #             print "item name: None"
    #         print format
    #         print


            self._generate(d, current_item)


class S16F15DigestGenerator(BaseDigestGenerator):


    S16F15_format = {
    "L": 2,
    1: "DATAID",
    2: {
        "L": -1,
        -1: {
            "L": 6,
            1: "PRJOBID",
            2: "MF",
            3: {
                "L": -1,
                -1: "MID"
                },
            4: {
                "L": 3,
                1: "RECIPE_METHOD",
                2: "RCPSPEC",
                3: {
                    "L": -1,
                    -1: {
                         "L": 2,
                         1: "RCP_PAR_NM",
                         2: "RCP_PAR_VAL"
                         }
                    }
                },
            5: "PROCESSSTART",
            6: "PAUSEEVENT"
            }
        }
    }
    S16F15_digest_value_target = ["PRJOBID", "RCPSPEC"]
    S16F15_digest_annot_target = {"PRJOBID": "PRJOBID", "RCPSPEC": "RCPSPEC", "RCP_PAR_VAL":"RCP_PAR_VAL"}

    def __init__(self):
        super(S16F15DigestGenerator, self).__init__(S16F15DigestGenerator.S16F15_format,
                                                    S16F15DigestGenerator.S16F15_digest_value_target,
                                                    S16F15DigestGenerator.S16F15_digest_annot_target)

    def _generate(self, item, item_name):
        txt = super(S16F15DigestGenerator, self)._generate(item, item_name)

        # type2. if no actual value (only list etc.), no output
        if self.current_item == "RCP_PAR_NM" and item["value"] is not None:
            # Assume RCP_PAR_NM is always A (never L) and prior to RCP_PAR_VAL
            self.tmp_value_name = item["value"] + ': '
            self.tmp_value_txt = ""

        elif self.current_item == "RCP_PAR_VAL":
            if item_name is None:   # Inside of List of target value
                if item["value"] is not None:
                    if self.tmp_value_txt:
                        self.tmp_value_txt += ' | '
                    self.tmp_value_txt += item["value"]

            else:
                if item["status"] == END_LIST:
                    if self.tmp_value_name and self.tmp_value_txt:
                        self.value.append(self.tmp_value_name + self.tmp_value_txt)
                    self.tmp_value_name = ""
                    self.tmp_value_txt = ""

                elif item["value"] is not None:
                    if self.tmp_value_name:
                        self.value.append(self.tmp_value_name + item["value"])

        print txt

class S6F11DigestGenerator2(BaseDigestGenerator):

    S6F11_format = {
    "L": 3,
    1: "DATAID",
    2: "CEID",
    3: {
        "L": -1,
        -1: {
            "L": 2,
            1: "RPTID",
            2: {
                "L": -1,
                -1 : "V"
                }
            }
        }
    }
    # S6F11_digest_value_target = ["var5", "var4", "var3", "var2"]
    S6F11_digest_annot_target = {"CEID": "CEID"}

    def __init__(self):
        super(S6F11DigestGenerator2, self).__init__(S6F11DigestGenerator2.S6F11_format,
                                                    None,
                                                    S6F11DigestGenerator2.S6F11_digest_annot_target)

        self.value_target = None        # set of target V
        self.value_target_list = None

        self.tmp_value = None
        self.current_report = None

        self.value_dict = {}

    def _generate(self, item, item_name):
        txt = super(S6F11DigestGenerator2, self)._generate(item, item_name)

        # Compose digest Value and add Annot
        if item_name == "CEID":
            ret = target_vname_list.get(int(item["value"]))
            if ret:
                self.value_target_list = ret
                self.value_target = set(ret)   # ここで毎回set化するのではなく、設定読み込み時にしておきたい

        elif item_name == "RPTID":
            ret = report_list.get(item["value"])
            if ret:
                self.current_report = ret
                self.tmp_value_name = ""
                self.tmp_value_txt = ""

        elif self.current_item == "V":
            if item_name is None:   # Inside of List of V
                if item["value"] is not None and self.tmp_value_name:
                    if self.tmp_value_txt:
                        self.tmp_value_txt += ' | '
                    self.tmp_value_txt += item["value"]

            else:
                if item["status"] == END_LIST:
                    if self.tmp_value_name and self.tmp_value_txt:
                        if self.value_target:
                            self.value_dict[self.tmp_value_name] = (self.tmp_value_name +
                                                                    ': ' + self.tmp_value_txt)
                        else:
                            self.value.append(self.tmp_value_name + ': ' + self.tmp_value_txt)
                    self.tmp_value_name = ""
                    self.tmp_value_txt = ""

                else:     # START_LIST or START_ITEM of V
                    self.tmp_value_name = ""
                    self.tmp_value_txt = ""
                    index = item["readable_depth"][4] - 1

                    if self.current_report is not None and index < len(self.current_report):
                        var_name = var_list.get(self.current_report[index])
                        if var_name:
                            # Add Annot
                            txt = txt.ljust(70) + "// " + var_name

                            if self.value_target is None:
                                self.tmp_value_name = var_name

                            elif var_name in self.value_target:
                                if self.value_dict.get(var_name) is None:
                                    self.tmp_value_name = var_name
                                    # If this variable already appeared, No more update.
                                    # (i.e. var_name is not set to self.tmp_value_name)

                    if self.tmp_value_name and item["value"] is not None:   # START_ITEM with value
                        if self.value_target:
                            self.value_dict[self.tmp_value_name] = self.tmp_value_name + ': ' + item["value"]
                        else:
                            # Add even if vairable is duplicated
                            self.value.append(self.tmp_value_name + ': ' + item["value"])
                        self.tmp_value_name = ""
                        self.tmp_value_txt = ""

        print txt


    def get_digest(self):

        print self.value_dict

        txt = ''

        if self.value_target:
            for var_name in self.value_target_list:
                value_txt = self.value_dict.get(var_name)
                if value_txt:
                    if txt:
                        txt += ', '
                    txt += value_txt
        else:
            txt = ', '.join(self.value)

        return txt

class S1F2DigestGenerator(BaseDigestGenerator):

    S1F2_format = {
    1: "ACK"
    }
    S1F2_digest_value_target = ["ACK"]
    S1F2_digest_annot_target = {"ACK": "REPLY"}

    def __init__(self):
        super(S1F2DigestGenerator, self).__init__(S1F2DigestGenerator.S1F2_format,
                                                  S1F2DigestGenerator.S1F2_digest_value_target,
                                                  S1F2DigestGenerator.S1F2_digest_annot_target)



import sys
if __name__ == '__main__':
    timer = Timer()

#     val_depth_dict = generate_digest_val_depth_dict()
#     val = {}

    fp = open("./data/textS1F2.txt")
    f = fp.readlines()
    fp.close()

    '''
    1. 指定したアイテムにコメントをつける

    2. 指定したアイテムの値を取得する。L型の場合は値を結合する
        a. 指定したアイテム名に対応するアイテムの値を出現順に取得する(S16F15等)
        b. 指定したアイテム名リスト順に値を取得する(S6F11リスト指定時のみ)
        c. 指定したアイテム名と値名に対応する、アイテムの名前および値をそれぞれ別のアイテムから取得する。出力は出現順
            (aのアイテムと複合)(S16F11等)
        c.1 cの亜種として、アイテム名はID->Name変換をして取得する。出力は出現順(S6F11リスト無指定時のみ)

        * CPNAMEが"..."のもののみ、CPNAME:CPVAL のようにダイジェストする、という要求あるかも

    * フォーマットからアイテム名を取得する方法
    下記のパフォーマンスを比較する
    1. 毎アイテムごとに、フォーマットの頭から辿り、アイテム名を取得する
    ★2. 毎アイテム解析と一緒に、フォーマット内の位置を移動していき、現在のアイテム名を取得する

    * 現在のフォーマット表現の問題点
    可変長リスト ({"L" : -1}を辞書に含む)自体がアイテム名を持たない→これ自体を値収集orコメント付与対象に指定できない
    対策： "name"要素を可変長リストの辞書に追加する
    ただ、フォーマット上使用されるであろう可変長リストは、E5上も無名のもののみと想定されるため、
    本対策は不要と思われる
    '''

    for count in xrange(1):
#         timer.enter()
#         for loop in xrange(1000):
#             iterator1(f)
#
#         print "idea1: "
#         timer.exit()

    #     print '#' * 80

#         timer.enter()
#         for loop in xrange(1000):
#             iterator2(f)
#
#         print "idea2: "
#         timer.exit()

        timer.enter()
        for loop in xrange(1):
            log_parser = LogParser()
#             dg = S1F2DigestGenerator()
            dg = BaseDigestGenerator()
            item_generator = log_parser.parse_msg(f)

            dg.iterator3(item_generator)

#             dg = S16F15DigestGenerator(S16F15_digest_value_target, S16F15_digest_annot_target)
#             dg = S6F11DigestGenerator2(S6F11_digest_value_target, S6F11_digest_annot_target)
#             dg = S6F11DigestGenerator2(None, S6F11_digest_annot_target)
#             dg = BaseDigestGenerator(S16F15_digest_value_target, S16F15_digest_annot_target)
#             iterator3(f, S6F11_format, dg)

            print
            print '#' * 80
            print "[Value]"
            print dg.get_digest()

        print "-" * 80
        print "idea3: "
        timer.exit()


