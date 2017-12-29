# -*- coding: utf-8 -*-
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
#                 msg.notify_end_list(item)
                yield None
                continue

#             msg.notify_item(item)
            yield item

#         return msg.get_digest()

S6F11_format = {
"L": 3,
1: "dataid",
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

S16F11_format = {
"L": 7,
1: "DAATAID",
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
S16F11_digest_value_target = ["PRJOBID", "RCPSPEC", ("RCP_PAR_NM", "RCP_PAR_VAL")]

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

import sys
if __name__ == '__main__':
    val_depth_dict = generate_digest_val_depth_dict()
    val = {}

    log_parser = LogParser()

    f = open("./data/text1.txt")
    digest = log_parser.parse_msg(f)

    current_index = 1
    current_item = S16F11_format[1]

    for d in digest:
#         print d["readable_depth"], d["type"]
        if d["value"] is None:
            continue

        # a. 辞書に登録されたアイテムと一致するかチェックする方法
        for item_depth in val_depth_dict:
            if compare_depth_tree(val_depth_dict[item_depth], d["readable_depth"]):
                val.setdefault(item_depth, []).append(d["value"])

        # b. 毎アイテムごとにアイテム名を取得する方法
        format = S16F11_format
        ret = ""
#         print d["readable_depth"]
        for index in d["readable_depth"][1:]:
            if not format:   # {}
                break
            ret = format.get(index)
            if isinstance(ret, dict):
                format = ret
            elif ret is None:
                ret = format.get(-1)
                if ret is None:
                    print "not found"
                    break
                elif isinstance(ret, dict):
                    format = ret
                else:
                    break
            else:
                break

#         print ret, d["value"]

        print current_item

    print val
    f.close()


