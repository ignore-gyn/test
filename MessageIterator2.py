# -*- coding: utf-8 -*-

START_ITEM = 0
START_LIST = 1
END_LIST = 2

import sys


# CEID - EVENTNAME
event_list = {
              9991 : "Event1",
              9999 : "Event2"
              }

# CEID - target VNAMEs
target_vname_list = {
#                      9999 : ["var5", "var4", "var3", "var2"]
9999: []
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

    def parse_msg(self, log, digest_generator):
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

            digest_generator.generate(item)

#         return msg.get_digest()

class BaseDigestGenerator(object):
    TAB = '    '

    def __init__(self, format=None, value_target=None, pair_target=None, annot_target=None):

        if format:
            self.format = format
        else:
            self.format = {}

        if value_target:
            self.value_target = set(value_target)
        else:
            self.value_target = set()

        if pair_target:
            self.pair_target = pair_target
        else:
            self.pair_target = {}

        if annot_target:
            self.annot_target = annot_target
        else:
            self.annot_target = {}

        self.cleanup()

    def cleanup(self):
        self.detail = []
        self.value = ""

        self.tmp_value_name = ""
        self.tmp_value_txt = ""
        self.waiting_item_name = ""

        self.current_format = self.format
        self.available_depth = 0

        self.is_err = False

    def get_digest(self):
        return self.value, '\n'.join(self.detail)

    def generate(self, item):
        if not self.format:
            current_item_name = None
        else:
            if item["status"] is END_LIST:
                current_item_name = self._handle_end_list(item)

            elif item["status"] is START_LIST:
                current_item_name = self._handle_start_list(item)

            elif item["status"] is START_ITEM:
                current_item_name = self._handle_item(item)
                # <L[0]> is also included (in that case, current_item_name type is dictionary)

        print item["readable_depth"], "av =", self.available_depth, "name =", current_item_name
        self._generate_detail(item, current_item_name)
        print

        self._generate_value(item, current_item_name)


    def _generate_detail(self, item, item_name):
        txt = ""

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

        if not self.format:
            print txt
            self.detail.append(txt)
            return

        # Add Annot
        if item["status"] is not END_LIST and isinstance(item_name, str):

            if item_name and self._is_vararray(item) is False:
                # vararrayの開始Lも含む
                ret = self.annot_target.get(item_name)
                if ret == "CEID":
                    try:
                        ret = self._get_event_name_from_CEID(item["value"])
                    except:
                        ret = None
                    if ret:
                        txt = txt.ljust(50) + "// " + ret
                elif ret:
                    txt = txt.ljust(50) + "// " + ret

        self.detail.append(txt)
        print txt
        return


    def _generate_value(self, item, current_item_name):
        if self.is_err:
            return

        if not isinstance(current_item_name, str):
            return

        if item["status"] is END_LIST:
            self._write_vararray_value()
        elif current_item_name in self.value_target:
            self.tmp_value_name = current_item_name
            self._store_value(item)
        elif current_item_name in self.pair_target:
            self.tmp_value_name = item["value"]
            self.waiting_item_name = self.pair_target[current_item_name]
        elif current_item_name == self.waiting_item_name:
            self._store_value(item)
        else:
            self.waiting_item_name = ""


    def _write_vararray_value(self):
        self._write_to_value(self.tmp_value_name, self.tmp_value_txt)

        self.tmp_value_name = ""
        self.tmp_value_txt = ""
        self.waiting_item_name = ""

    def _store_value(self, item):
        if item["status"] is START_LIST:
            return
        elif self._is_vararray(item):
            if item["value"]:
                if self.tmp_value_txt:
                    self.tmp_value_txt += " | "
                self.tmp_value_txt += item["value"]
        else:
            self._write_to_value(self.tmp_value_name, item["value"])

            self.tmp_value_name = ""
            self.tmp_value_txt = ""
            self.waiting_item_name = ""

    def _write_to_value(self, name, value):
        if name and value:
            if self.value:
                self.value += ', '

            self.value += name + ': ' + value


    def _get_event_name_from_CEID(self, ceid):
        return event_list.get(int(ceid))

    def _get_V_name_from_VID(self, vid):
        return var_list.get(int(vid))


    def _is_vararray(self, item):
        # vararrayの開始、終了LではFalseを返す(vararray: フォーマット上はL型ではないアイテム)
        # vararrayの終了LではTrueを返す
        if item["status"] is START_LIST:
            if len(item["readable_depth"])-2 > self.available_depth:

                return True
            else:
                return False
        else:
            if len(item["readable_depth"])-2 >= self.available_depth:
                return True
            else:
                return False


    def _handle_item(self, item):
        return self.current_format.get(item["readable_depth"][self.available_depth])


    def _handle_start_list(self, item):
        if self.available_depth  == 0:
            # First List of Message
            self.available_depth = 1
            return None

        elif self._is_vararray(item):
            return None

        else:
            fmt = self.current_format.get(item["readable_depth"][self.available_depth])
            if isinstance(fmt, str):
                # Beginning of vararray, return name
                return fmt
            elif isinstance(fmt, dict):
                self.available_depth += 1
                format_list_length = fmt.get("L")
                if format_list_length is None:
                    print "Invalid SF format found: ", fmt
                    self.is_err = True
                elif format_list_length == -1:
                    for i in xrange(2, item["length"]+1):
                        fmt[i] = fmt[1]
                elif item["length"] != format_list_length:
                    print "[ERR]Invalid length List:", item["readable_depth"], ", available_depth =", self.available_depth
                    print "    ", "length=", item["length"], ", fmtL=", fmt.get("L")
                    self.is_err = True

                self.current_format= fmt
                return None
            else:
                print "[ERR]Invalid format:", item["readable_depth"], ", available_depth =", self.available_depth
                self.is_err = True
                return None


    def _handle_end_list(self, item):
        if self._is_vararray(item):
            # vararrayの中
            return None

        elif len(item["readable_depth"])-1 == self.available_depth:
            # End of vararray, return name
            return self.current_format.get(item["readable_depth"][self.available_depth])

        else:
            self.available_depth -= 1
            self.current_format = self.format
            for i in item["readable_depth"][1:-1]:
                self.current_format = self.current_format.get(i)
            return None


class S16F15DigestGenerator(BaseDigestGenerator):
    S16F15_format = {
    "L": 3,
    1: "DATAID",
    2: {
        "L": -1,
        1: {
            "L": 6,
            1: "PRJOBID",
            2: "MF",
            3: {
                "L": -1,
                1: "MID"
                },
            4: {
                "L": 3,
                1: "RECIPE_METHOD",
                2: "RCPSPEC",
                3: {
                    "L": -1,
                    1: {
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
    S16F15_digest_value_target = ["PRJOBID", "MID", "RCPSPEC", "PROCESSSTART"]
    S16F15_digest_pair_target = {"RCP_PAR_NM": "RCP_PAR_VAL"}
    S16F15_digest_annot_target = {"RCP_PAR_NM":"RCP_PAR_NM", "PRJOBID": "PRJOBID", "RCPSPEC": "RCPSPEC", "RCP_PAR_VAL":"RCP_PAR_VAL"}

    def __init__(self):
        super(S16F15DigestGenerator, self).__init__(S16F15DigestGenerator.S16F15_format,
                                                    S16F15DigestGenerator.S16F15_digest_value_target,
                                                    S16F15DigestGenerator.S16F15_digest_pair_target,
                                                    S16F15DigestGenerator.S16F15_digest_annot_target)



class S6F11DigestGenerator2(BaseDigestGenerator):

    S6F11_format = {
    "L": 3,
    1: "DATAID",
    2: "CEID",
    3: {
        "L": -1,
        1: {
            "L": 2,
            1: "RPTID",
            2: {
                "L": -1,
                1 : "V"
                }
            }
        }
    }
    # S6F11_digest_value_target = ["var5", "var4", "var3", "var2"]
    S6F11_digest_annot_target = {"CEID": "CEID"}

    def __init__(self):
        super(S6F11DigestGenerator2, self).__init__(S6F11DigestGenerator2.S6F11_format,
                                                    None,
                                                    None,
                                                    S6F11DigestGenerator2.S6F11_digest_annot_target)

        self.value_target = None        # set of target V
        self.value_target_list = None


        self.current_report = None

        self.value_dict = {}

    def _generate_value(self, item, current_item_name):
        if self.is_err:
            return

        if not isinstance(current_item_name, str):
            return

        if current_item_name == "CEID":
            try:
                ret = target_vname_list.get(int(item["value"]))
            except:
                ret = None
            if ret:
                self.value_target_list = ret
                self.value_target = set(ret)   # ここで毎回set化するのではなく、設定読み込み時にしておきたい

        elif current_item_name == "RPTID":
            ret = report_list.get(item["value"])
            if ret:
                self.current_report = ret
                self.tmp_value_name = ""
                self.tmp_value_txt = ""
            else:
                pass
#                 error_report_id.add(item["value"])

        elif current_item_name == "V":
            '''
            if "VIDS" is not specified, all variables are target. They are shown in the order of apperance even if duplicated.
            if "VIDS" is specified but empyt list, no variables are target.
            if "VIDS" is specified and not empty list, They are shown in the order in "VIDS" list and not duplicated.
            '''
            if item["status"] is END_LIST:
                if self.tmp_value_name and self.tmp_value_txt:
                    if self.value_target is None:
                        self._write_vararray_value()
                    else:
                        self.value_dict[self.tmp_value_name] = (self.tmp_value_name +
                                                                ': ' + self.tmp_value_txt)
                self.tmp_value_name = ""
                self.tmp_value_txt = ""

            elif self._is_vararray(item):
                if self.tmp_value_name:
                    # update self.tmp_value_txt
                    self._store_value(item)

            else:
                self.tmp_value_name = ""
                self.tmp_value_txt = ""
                index = item["readable_depth"][4] - 1

                if self.current_report is not None and index < len(self.current_report):
                    var_name = var_list.get(self.current_report[index])
                    if var_name:
                        # Add Annot
                        self.detail[-1] = self.detail[-1].ljust(50) + "// " + var_name

                        if self.value_target is None:
                            self.tmp_value_name = var_name
                        elif var_name in self.value_target:
                            if self.value_dict.get(var_name) is None:
                                self.tmp_value_name = var_name
                                # If this variable already appeared, No more update.
                                # (i.e. var_name is not set to self.tmp_value_name)

                if self.tmp_value_name and item["status"] is START_ITEM:
                    if item["value"]:
                        if self.value_target is None:
                            # Add even if vairable is duplicated
                            self._write_to_value(self.tmp_value_name, item["value"])
                        else:
                            self.value_dict[self.tmp_value_name] = self.tmp_value_name + ': ' + item["value"]

                    self.tmp_value_name = ""
                    self.tmp_value_txt = ""




    def get_digest(self):

        print self.value_dict

        txt = ''

        if self.value_target is not None:
            for var_name in self.value_target_list:
                value_txt = self.value_dict.get(var_name)
                if value_txt:
                    if txt:
                        txt += ', '
                    txt += value_txt
        else:
            txt = self.value

        return txt, '\n'.join(self.detail)


class S1F2DigestGenerator(BaseDigestGenerator):

    S1F2_format = {
                   1: "NAME"
    }
    S1F2_digest_value_target = ["NAME", "RCPSPEC"]

    def __init__(self):
        super(S1F2DigestGenerator, self).__init__(S1F2DigestGenerator.S1F2_format,
                                                  S1F2DigestGenerator.S1F2_digest_value_target,
                                                    None,
                                                    None)


class S16F11DigestGenerator(BaseDigestGenerator):


    S16F11_format = {
    "L": 7,
    1: "DATAID",
    2: "PRJOBID",
    3: "MF",
    4: {
        "L": -1,
        1: "MID"
        },
    5: {
        "L": 3,
        1: "RECIPE_METHOD",
        2: "RCPSPEC",
        3: {
            "L": -1,
            1: {
                 "L": 2,
                 1: "RCP_PAR_NM",
                 2: "RCP_PAR_VAL"
                 }
            }
        },
    6: "PROCESSSTART",
    7: "PAUSEEVENT"
    }
    S16F11_digest_value_target = ["PRJOBID", "RCPSPEC"]
    S16F11_digest_pair_target = {"PROCESSSTART": "PAUSEEVENT",
                                 "MF":"MID",
                                 "RCP_PAR_NM": "RCP_PAR_VAL"}
    S16F11_digest_annot_target = {"PRJOBID": "PRJOBID", "RCPSPEC": "RCPSPEC", "RCP_PAR_VAL":"RCP_PAR_VAL"}


    def __init__(self):
        super(S16F11DigestGenerator, self).__init__(S16F11DigestGenerator.S16F11_format,
                                                    S16F11DigestGenerator.S16F11_digest_value_target,
                                                    S16F11DigestGenerator.S16F11_digest_pair_target,
                                                    S16F11DigestGenerator.S16F11_digest_annot_target)

import glob
import signal
import time


if __name__ == '__main__':
    def handle_signal(signum, stack):
        '''
        開いているログファイルを閉じる -> 読み込みgeneratorを止めて閉じる（フラグを追加する）
        書き込み中のダイジェストファイルを閉じる、消す -> 書き込みクラスにメソッド追加
        (一時ファイルを消す)
        '''
        if fp:
            fp.close()
            print fp, "closed."

        print "Received:", signum

        sys.exit()

    signal.signal(signal.SIGINT, handle_signal)

    for f in glob.glob("./data/text*"):
        fp = open(f)

    #     fp = open("./data/textS16F15_test1.txt")
        f = fp.readlines()

        log_parser = LogParser()
    #             dg = S1F2DigestGenerator()
#         dg = S6F11DigestGenerator2()
        dg = S1F2DigestGenerator()
        log_parser.parse_msg(f, dg)
        dg.cleanup()

        print
        print '#' * 80
        value, detail = dg.get_digest()
        print detail
        print
        print "[Value]"
        print value
        if dg.is_err:
            print "ERROR OCCUR"

        time.sleep(0)

        fp.close()

